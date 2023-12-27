import os
from contextlib import closing
from typing import Union, Dict

import pytest
import structlog
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine
from sqlalchemy import text
from sqlalchemy.engine.url import URL
from sqlalchemy.engine.url import make_url
from sqlalchemy.orm.session import sessionmaker
from starlette.testclient import TestClient

from db import db
from db.database import ENGINE_ARGUMENTS, SESSION_ARGUMENTS
from settings import app_settings

logger = structlog.getLogger(__name__)


def run_migrations(db_uri: str) -> None:
    """
    Configure the alembic context and run the migrations.

    Each test will start with a clean database. This a heavy operation but ensures that our database is clean and
    tests run within their own context.

    Args:
        db_uri: The database uri configuration to run the migration on.

    Returns:
        None

    """
    path = os.path.dirname(os.path.realpath(__file__))
    os.environ["DATABASE_URI"] = db_uri
    app_settings.DATABASE_URI = db_uri
    alembic_cfg = Config(file_=os.path.join(path, "../alembic.ini"))
    alembic_cfg.set_main_option("script_location", os.path.join(path, "db/migrations"))
    alembic_cfg.set_main_option(
        "version_locations",
        os.path.join(path, 'db/migrations/versions'),
    )
    alembic_cfg.set_main_option("version_path_separator", ';')
    alembic_cfg.set_main_option("sqlalchemy.url", db_uri)
    command.upgrade(alembic_cfg, "heads")


@pytest.fixture(scope="session")
def db_uri(worker_id):
    """
    Ensure each pytest thread has its database.

    When running tests with the -j option make sure each test worker is isolated within its own database.

    Args:
        worker_id: the worker id

    Returns:
        Database uri to be used in the test thread

    """
    database_uri = os.environ.get(
        "DATABASE_URI",
        "postgresql://postgres:postgres@localhost:54322/guardian-test",
    )
    if worker_id == "master":
        # pytest is being run without any workers
        return database_uri
    url = make_url(database_uri)
    return str(url.set(database=f"{url.database}-{worker_id}"))


@pytest.fixture(scope="session")
def database(db_uri):
    """Create database and run migrations and cleanup afterward.

    Args:
        db_uri: fixture for providing the application context and an initialized database.

    """
    url = make_url(db_uri)
    db_to_create = url.database
    # we need to connect to existing DB first
    existing_db_url = url.set(database="postgres")
    engine = create_engine(existing_db_url)
    with closing(engine.connect()) as conn:
        conn.execute(text("COMMIT;"))
        conn.execute(text(f'DROP DATABASE IF EXISTS "{db_to_create}";'))
        conn.execute(text("COMMIT;"))
        conn.execute(text(f'CREATE DATABASE "{db_to_create}";'))

    init_schema(url)
    run_migrations(db_uri)

    db.engine = create_engine(db_uri, **ENGINE_ARGUMENTS)

    try:
        yield
    finally:
        db.engine.dispose()
        with closing(engine.connect()) as conn:
            conn.execute(text("COMMIT;"))
            conn.execute(text(f'DROP DATABASE IF EXISTS "{db_to_create}";'))


def init_schema(url: Union[str, URL]) -> None:
    """
    Set up initial Database from the SQL dump
    :param url: Test database connection string
    """
    test_engine = create_engine(url)
    with closing(test_engine.connect()) as test_conn:
        path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        with open(os.path.join(path, "server", "db", "migrations", "init.sql")) as init_schema_file:
            test_conn.execute(text(init_schema_file.read()))
        with open(os.path.join(path, "supabase", "migrations",
                               "20231219212620_remote_schema.sql")) as sp_migration:
            test_conn.execute(text(sp_migration.read()))
        test_conn.commit()


@pytest.fixture(autouse=True)
def db_session(database):
    """
    Ensure tests are run in a transaction with automatic rollback.

    This implementation creates a connection and transaction before yielding to the test function.
    Any transactions started and committed from within the test will be tied to this outer
    transaction. From the test function's perspective it looks like everything will indeed be
    committed. It allowes for queries on the database to be performed to see if functions under test
    have persisted their changes to the database correctly.
    However, once the test function returns, this fixture will clean everything up by rolling back
    the outer transaction, leaving the database in an empty state (besides the migrations).

    Args:
        database: fixture for providing an initialized database.

    """
    with db.engine.connect() as test_connection:
        db.session_factory = sessionmaker(bind=test_connection, **SESSION_ARGUMENTS)
        db.session_context_var.set(db.session_factory())

        transaction = test_connection.begin()
        try:
            yield
        finally:
            transaction.rollback()


@pytest.fixture(scope="session")
def client(fastapi_app):
    return TestClient(fastapi_app)


@pytest.fixture()
def superuser_token_headers(client, user_admin) -> Dict[str, str]:
    login_data = {
        "username": "Admin",
        "password": "admin",
    }
    r = client.post("/api/login/access-token", data=login_data)
    tokens = r.json()
    a_token = tokens["access_token"]
    headers = {"Authorization": f"Bearer {a_token}"}
    return headers


@pytest.fixture()
def user_token_headers(client, user_non_admin) -> Dict[str, str]:
    login_data = {
        "username": "User",
        "password": "user",
    }
    r = client.post("/api/login/access-token", data=login_data)
    tokens = r.json()
    a_token = tokens["access_token"]
    headers = {"Authorization": f"Bearer {a_token}"}
    return headers
