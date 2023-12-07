from __future__ import annotations

from contextvars import ContextVar

from sqlalchemy.ext.declarative import DeferredReflection
from sqlalchemy.orm import Session, Mapped

from db import SessionLocal


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


db_session: ContextVar[Session] = ContextVar('db_session')
# noinspection PyUnresolvedReferences
current_org: ContextVar[Mapped["Org"]] = ContextVar('current_org')
