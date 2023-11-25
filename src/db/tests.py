from uuid import uuid4

import pytest
from llama_index.constants import DEFAULT_EMBEDDING_DIM
from sqlalchemy import create_engine, exc, select
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


class TestBase:
    def test_get_existing(self, dbsession):
        org = Org(name='test company')
        dbsession.add(org)
        dbsession.commit()

        retrieved_org = Org.get(dbsession, org.id)

        assert retrieved_org.name == 'test company'

    def test_with_reflected_model(self, dbsession):
        user = User(email="test@user.com")
        dbsession.add(user)
        dbsession.commit()

        retrieved_user = User.get(dbsession, user.id)

        assert retrieved_user.email == "test@user.com"

    def test_get_non_existing(self, dbsession):
        with pytest.raises(exc.NoResultFound):
            Org.get(dbsession, str(uuid4()))


class TestOrg:
    def test_similarity_search_trivial(self, dbsession):
        org = Org(name='test company')
        expected = []
        for i in range(5):
            embedding = [0] * DEFAULT_EMBEDDING_DIM
            embedding[i] = 100
            chunk = Chunk(embedding=embedding)
            org.chunks.append(chunk)
            expected.append(chunk)
        dbsession.add(org)
        dbsession.commit()

        search_embedding = [0] * DEFAULT_EMBEDDING_DIM
        search_embedding[0] = 100
        chunks = org.similarity_search(dbsession, search_embedding)

        assert chunks == expected


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

    def test_create_same_chunks_same_org(self, dbsession):
        embedding = [1.0] * DEFAULT_EMBEDDING_DIM
        org = Org(name='test company')
        chunk_1 = Chunk(embedding=embedding)
        chunk_2 = Chunk(embedding=embedding)
        org.chunks = [chunk_1, chunk_2]
        dbsession.add(org)

        with pytest.raises(exc.IntegrityError):
            dbsession.commit()

    def test_create_different_chunks_same_org(self, dbsession):
        embedding_1 = [1.0] * DEFAULT_EMBEDDING_DIM
        embedding_2 = [2.0] * DEFAULT_EMBEDDING_DIM
        org = Org(name='test company')
        chunk_1 = Chunk(embedding=embedding_1)
        chunk_2 = Chunk(embedding=embedding_2)
        org.chunks = [chunk_1, chunk_2]
        dbsession.add(org)
        dbsession.commit()

        chunks = dbsession.execute(select(Chunk)).all()
        assert len(chunks) == 2

    def test_create_same_chunk_different_orgs(self, dbsession):
        embedding = [1.0] * DEFAULT_EMBEDDING_DIM
        org_1 = Org(name='test company 1')
        org_2 = Org(name='test company 2')
        chunk_1 = Chunk(embedding=embedding)
        chunk_2 = Chunk(embedding=embedding)
        org_1.chunks = [chunk_1]
        org_2.chunks = [chunk_2]
        dbsession.add_all([org_1, org_2])
        dbsession.commit()

        rows = dbsession.execute(select(Chunk)).all()
        assert len(rows) == 2
        assert rows[0].Chunk.org_id != rows[1].Chunk.org_id


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
