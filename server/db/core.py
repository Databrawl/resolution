from __future__ import annotations

from contextvars import ContextVar
from typing import Any

from sqlalchemy.ext.declarative import DeferredReflection
from sqlalchemy.orm import Session, Mapped

from db import SessionLocal

db_session: ContextVar[Session] = ContextVar('db_session')
# noinspection PyUnresolvedReferences
current_org: ContextVar[Mapped["Org"]] = ContextVar('current_org')


class Reflected(DeferredReflection):
    __abstract__ = True


def get_db():
    db: Session = SessionLocal()
    Reflected.prepare(db.bind)

    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
    finally:
        db.close()


def enable_context(values_dict: dict[str, Any]):
    db_session.set(values_dict['db_session'])
    current_org.set(values_dict['current_org'])
