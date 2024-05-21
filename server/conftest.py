import pytest
import structlog

from app import app, create_app
from db import db

logger = structlog.getLogger(__name__)


@pytest.fixture()
def test_app():
    _test_app = create_app()
    _test_app.config.update({
        "TESTING": True,
    })

    with _test_app.app_context():
        yield _test_app


@pytest.fixture(autouse=True, scope="function")
def db_session(test_app):
    """
    Ensure tests are run in a transaction with automatic rollback.

    Initiate a connection and an outer transaction for the test, linking inner transactions to it.
    It allows database queries to check if test functions persist changes correctly. Post-test, it rolls back the outer
    transaction, resetting the database except for migrations.
    """
    with db.engine.connect() as test_connection:
        transaction = test_connection.begin()
        try:
            yield
        finally:
            transaction.rollback()


@pytest.fixture
def client():
    with app.test_client() as client:
        yield client
