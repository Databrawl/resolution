from __future__ import annotations

from contextlib import contextmanager
from contextvars import ContextVar
from typing import Any
from typing import Generator, Iterator, Optional
from uuid import uuid4

import structlog
from sqlalchemy import create_engine
from sqlalchemy.orm import Query, Session, scoped_session, sessionmaker
from sqlalchemy_searchable import SearchQueryMixin
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp
from structlog.stdlib import BoundLogger

from server.utils.json import json_dumps, json_loads

logger = structlog.get_logger(__name__)


class SearchQuery(Query, SearchQueryMixin):
    """Custom Query class to have search() property."""

    pass


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
    "query_cls": SearchQuery,
}


class Database:
    """Setup and contain our database connection.

    This is used to be able to set up the database in a uniform way while allowing easy testing and
    session management.

    Session management is done using ``scoped_session`` with a special scopefunc, because we cannot
    use threading.local(). Contextvar does the right thing with respect to asyncio and behaves
    similar to threading.local().
    We only store a random string in the contextvar and let scoped session do the heavy lifting.
    This allows us to easily start a new session or get the existing one using the scoped_session
    mechanics.
    """

    def __init__(self, db_url: str) -> None:
        self.request_context: ContextVar[str] = ContextVar("request_context", default="")
        self.engine = create_engine(db_url, **ENGINE_ARGUMENTS)
        self.session_factory = sessionmaker(bind=self.engine, **SESSION_ARGUMENTS)

        self.scoped_session = scoped_session(self.session_factory, self._scopefunc)

    def _scopefunc(self) -> Optional[str]:
        scope_str = self.request_context.get()
        return scope_str

    @property
    def session(self) -> WrappedSession:
        return self.scoped_session()

    @contextmanager
    def database_scope(self, **kwargs: Any) -> Generator["Database", None, None]:
        """Create a new database session (scope).

        This creates a new database session to handle all the database connection from a single scope (request or workflow).
        This method should typically only been called in request middleware or at the start of workflows.

        Args:
            ``**kwargs``: Optional session kw args for this session
        """
        token = self.request_context.set(str(uuid4()))
        self.scoped_session(**kwargs)

        yield self
        self.scoped_session.remove()
        self.request_context.reset(token)


class DBSessionMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, database: Database, commit_on_exit: bool = False):
        super().__init__(app)
        self.commit_on_exit = commit_on_exit
        self.database = database

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        with self.database.database_scope():
            response = await call_next(request)
        return response


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
def transactional(db: Database, log: BoundLogger) -> Iterator:
    """Run a step function in an implicit transaction with automatic rollback or commit.

    It will rollback in case of error, commit otherwise. It will also disable the `commit()` method
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
