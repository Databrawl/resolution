import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from db.models import Reflected
from .config import settings


@pytest.fixture(scope="session")
def engine():
    # TODO: seed test db with auth schema data, then switch to test db
    return create_engine(settings.SUPABASE_DB)


@pytest.fixture
def dbsession(engine):
    """Returns an sqlalchemy session, and after the test tears down everything properly."""
    Reflected.prepare(engine)

    connection = engine.connect()
    # begin the nested transaction
    transaction = connection.begin()
    # use the connection with the already started transaction
    session = Session(bind=connection)

    yield session

    session.close()
    # roll back the broader transaction
    transaction.rollback()
    # put back the connection to the connection pool
    connection.close()
