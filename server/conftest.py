import pytest
import structlog
from sqlalchemy.orm.session import Session

from db import db
from db.database import SESSION_ARGUMENTS
from app import app

logger = structlog.getLogger(__name__)


@pytest.fixture(autouse=True, scope="function")
def db_session():
    """
    Ensure tests are run in a transaction with automatic rollback.

    Initiate a connection and an outer transaction for the test, linking inner transactions to it.
    It allows database queries to check if test functions persist changes correctly. Post-test, it rolls back the outer
    transaction, resetting the database except for migrations.
    """
    with db.engine.connect() as test_connection:
        test_session = Session(bind=test_connection, **SESSION_ARGUMENTS)
        db.session = test_session
        transaction = test_connection.begin()
        try:
            yield
        finally:
            transaction.rollback()


@pytest.fixture
def client():
    with app.test_client() as client:
        yield client
