from uuid import uuid4

import pytest
from llama_index.constants import DEFAULT_EMBEDDING_DIM
from sqlalchemy import create_engine, exc
from sqlalchemy.orm import Session

from config import settings
from db.models import Chunk, Reflected, Org, User, OrgUser


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


class TestChunk:
    def test_create_chunk_instance_with_valid_values(self, dbsession):
        embedding = [1.0] * DEFAULT_EMBEDDING_DIM
        org = Org(name='test company')
        chunk = Chunk(embedding=embedding)
        org.chunks.append(chunk)
        dbsession.add(org)
        dbsession.commit()

        assert chunk.id is not None
        assert chunk.org_id == org.id
        assert all(chunk.embedding == embedding)

    def test_create_chunk_instance_with_invalid_embedding_length(self, dbsession):
        wrong_embedding_len = 10
        embedding = [1.0] * wrong_embedding_len
        org = Org(name='test company')
        chunk = Chunk(embedding=embedding)
        org.chunks.append(chunk)
        dbsession.add(org)
        with pytest.raises(exc.StatementError):
            dbsession.commit()


class TestGeneric:
    def test_all_models_together(self, dbsession):
        """ Test that all models can be created together """
        user = User(id=uuid4(), email="user@mail.com")
        org = Org(name='test company')
        embedding = [1.0] * DEFAULT_EMBEDDING_DIM
        chunk = Chunk(embedding=embedding)
        org.chunks.append(chunk)
        dbsession.add_all([user, org])
        dbsession.commit()

        org_user = OrgUser(user_id=user.id, org_id=org.id)
        dbsession.add(org_user)
        dbsession.commit()

        assert chunk.id is not None
        assert chunk.org_id == org.id
        assert chunk.org_id == org.id
        assert all(chunk.embedding == embedding)
