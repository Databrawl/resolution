from __future__ import annotations

from contextlib import contextmanager
from contextvars import ContextVar
from typing import Iterator

import structlog
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from structlog.stdlib import BoundLogger

from utils.json import json_dumps, json_loads

logger = structlog.get_logger(__name__)


class NoSessionError(RuntimeError):
    pass


class WrappedSession(Session):
    """This Session class allows us to disable commit during steps."""

    def commit(self) -> None:
        if self.info.get("disabled", False):
            self.info.get("logger", logger).warning(
                "Step function tried to issue a commit. It should not! "
                "Will execute commit on behalf of step function when it returns."
            )
        else:
            super().commit()


ENGINE_ARGUMENTS = {
    "connect_args": {"connect_timeout": 10, "options": "-c timezone=UTC"},
    "pool_pre_ping": True,
    "pool_size": 60,
    "json_serializer": json_dumps,
    "json_deserializer": json_loads,
}
SESSION_ARGUMENTS = {
    "class_": WrappedSession,
    "autocommit": False,
    "autoflush": True,
}


class Database:
    """Setup and contain database connection.

    This is used to be able to set up the database in a uniform way while allowing easy testing and
    session management.

    Session management is done using the  Contextvars. It does the right thing with respect to
    asyncio. Each context will have its own session. The session is automatically closed when used
    in a context manager:

        with db.session:
            # do stuff
    """

    def __init__(self, db_url: str) -> None:
        self.engine = create_engine(db_url, **ENGINE_ARGUMENTS)
        self.session_factory = sessionmaker(bind=self.engine, **SESSION_ARGUMENTS)
        self.session_context_var: ContextVar[Session] = ContextVar("session_context_var",
                                                                   default=self.session_factory())

    @property
    def session(self) -> Session:
        return self.session_context_var.get()


@contextmanager
def disable_commit(db: Database, log: BoundLogger) -> Iterator:
    restore = True
    # If `db.session` already has its `commit` method disabled we won't try disabling *and* restoring it again.
    if db.session.info.get("disabled", False):
        restore = False
    else:
        log.debug("Temporarily disabling commit.")
        db.session.info["disabled"] = True
        db.session.info["logger"] = log
    try:
        yield
    finally:
        if restore:
            log.debug("Reenabling commit.")
            db.session.info["disabled"] = False
            db.session.info["logger"] = None


@contextmanager
def with_transactional(db: Database, log: BoundLogger) -> Iterator:
    """Run a step function in an implicit transaction with automatic rollback or commit.

    It will roll back in case of error, commit otherwise. It will also disable the `commit()` method
    on `BaseModel.session` for the time `transactional` is in effect.
    """
    try:
        with disable_commit(db, log):
            yield
        log.debug("Committing transaction.")
        db.session.commit()
    except Exception:
        log.warning("Rolling back transaction.")
        raise
    finally:
        # Extra safe guard rollback. If the commit failed there is still a failed transaction open.
        # BTW: without a transaction in progress this method is a pass-through.
        db.session.rollback()
