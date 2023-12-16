import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from settings import app_settings


@pytest.fixture(scope="session")
def engine():
    # TODO: seed test db with auth schema data, then switch to test db
    return create_engine(app_settings.DATABASE_URI)


@pytest.fixture(autouse=True, scope="function")
def dbsession(engine):
    """Returns an sqlalchemy session, and after the test tears down everything properly."""
    Reflected.prepare(engine)

    connection = engine.connect()
    # begin the nested transaction
    transaction = connection.begin()
    # use the connection with the already started transaction
    session = Session(bind=connection)

    db_session.set(session)
    yield

    session.close()
    # roll back the broader transaction
    transaction.rollback()
    # put back the connection to the connection pool
    connection.close()
