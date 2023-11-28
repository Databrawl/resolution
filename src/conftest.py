import random
import string

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from db.models import Reflected, User
from src.config import settings


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


@pytest.fixture
def user_factory(dbsession):
    def create_user(length=5):
        characters = string.ascii_letters + string.digits + '_'
        local_part = ''.join(random.choice(characters) for _ in range(length))
        email = f"{local_part}@test.com"
        user = User(email=email)
        dbsession.add(user)
        dbsession.commit()
        return user

    return create_user
