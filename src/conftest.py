import random
import string
from hashlib import sha256

import pytest
from langchain.embeddings import OpenAIEmbeddings
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from db.models import Reflected, User, Chunk, Org
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


@pytest.fixture
def chunk_factory(dbsession):
    def create_chunk(org: Org, data: str = None, embedding: list[float] = None):
        if not embedding:
            embedding = OpenAIEmbeddings().embed_query(data)
        if not data:
            data = ''.join(random.choice(string.ascii_letters) for _ in range(10))
        hash_value = sha256(data.encode()).hexdigest()
        chunk = Chunk(org_id=org.id, hash_value=hash_value, embedding=embedding, data=data)
        dbsession.add(chunk)
        dbsession.commit()
        return chunk

    return create_chunk
