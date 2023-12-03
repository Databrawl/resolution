from uuid import uuid4

import pytest
from llama_index.constants import DEFAULT_EMBEDDING_DIM
from sqlalchemy import exc, select

from db.models import Chunk, Org, User, OrgUser


class TestBase:
    def test_get_existing(self, dbsession):
        org = Org(name='test company')
        dbsession.add(org)
        dbsession.commit()

        retrieved_org = Org.get(dbsession, org.id)

        assert retrieved_org.name == 'test company'

    def test_get_reflected_model(self, dbsession, user_factory):
        user = user_factory()

        retrieved_user = User.get(dbsession, user.id)

        assert retrieved_user.email == user.email

    def test_get_non_existing(self, dbsession):
        with pytest.raises(exc.NoResultFound):
            Org.get(dbsession, str(uuid4()))


class TestOrg:
    def test_similarity_search_trivial(self, dbsession, chunk_factory):
        org = Org(name='test company')
        dbsession.add(org)
        dbsession.commit()

        expected_chunks = []
        for i in range(5):
            embedding = [0] * DEFAULT_EMBEDDING_DIM
            embedding[i] = 100
            chunk = chunk_factory(org=org, data=f"Chunk {i}", embedding=embedding)
            org.chunks.append(chunk)
            expected_chunks.append(chunk)

        search_embedding = [0] * DEFAULT_EMBEDDING_DIM
        search_embedding[0] = 100
        chunks_with_similarities = org.similarity_search(dbsession, search_embedding)

        assert len(chunks_with_similarities) == 5
        assert chunks_with_similarities[0] == (expected_chunks[0], 1.0)
        assert chunks_with_similarities[1] == (expected_chunks[1], 0.0)
        assert chunks_with_similarities[2] == (expected_chunks[2], 0.0)
        assert chunks_with_similarities[3] == (expected_chunks[3], 0.0)
        assert chunks_with_similarities[4] == (expected_chunks[4], 0.0)


# TODO: fix these tests to use chunk_factory
class TestChunk:
    def test_create_chunk_instance_with_valid_values(self, dbsession, chunk_factory):
        org = Org(name='test company')
        # Add that to the OrgFactory
        dbsession.add(org)
        dbsession.commit()
        chunk = chunk_factory(org=org, data=f"Chunk")

        assert chunk.id is not None
        assert chunk.org_id == org.id

    def test_create_chunk_instance_with_invalid_embedding_length(self, dbsession, chunk_factory):
        wrong_embedding_len = 10
        embedding = [1.0] * wrong_embedding_len
        org = Org(name='test company')
        dbsession.add(org)
        dbsession.commit()
        with pytest.raises(exc.StatementError):
            chunk_factory(org=org, embedding=embedding)

    def test_create_same_chunks_same_org(self, dbsession, chunk_factory):
        org = Org(name='test company')
        dbsession.add(org)
        dbsession.commit()
        chunk_factory(org=org, data='test data')
        with pytest.raises(exc.IntegrityError):
            chunk_factory(org=org, data='test data')

    def test_create_different_chunks_same_org(self, dbsession, chunk_factory):
        embedding_1 = [1.0] * DEFAULT_EMBEDDING_DIM
        embedding_2 = [2.0] * DEFAULT_EMBEDDING_DIM
        org = Org(name='test company')
        dbsession.add(org)
        dbsession.commit()

        chunk_factory(org=org, embedding=embedding_1)
        chunk_factory(org=org, embedding=embedding_2)

        chunks = dbsession.execute(select(Chunk)).all()
        assert len(chunks) == 2

    def test_create_same_chunk_different_orgs(self, dbsession, chunk_factory):
        embedding = [1.0] * DEFAULT_EMBEDDING_DIM
        org_1 = Org(name='test company 1')
        org_2 = Org(name='test company 2')
        dbsession.add_all([org_1, org_2])
        dbsession.commit()
        chunk_factory(org=org_1, embedding=embedding)
        chunk_factory(org=org_2, embedding=embedding)
        # chunk_factory = Chunk(embedding=embedding)
        # org_1.chunks = [chunk_1]
        # org_2.chunks = [chunk_2]

        rows = dbsession.execute(select(Chunk)).all()
        assert len(rows) == 2
        assert rows[0].Chunk.org_id != rows[1].Chunk.org_id


class TestGeneric:
    def test_all_models_together(self, dbsession, user_factory, chunk_factory):
        """ Test that all models can be created together """
        user = user_factory()
        org = Org(name='test company')
        dbsession.add(org)
        dbsession.commit()
        embedding = [1.0] * DEFAULT_EMBEDDING_DIM
        chunk = chunk_factory(org=org, data="Chunk 1", embedding=embedding)
        org.chunks.append(chunk)

        org_user = OrgUser(user_id=user.id, org_id=org.id)
        dbsession.add(org_user)
        dbsession.commit()

        assert chunk.id is not None
        assert chunk.org_id == org.id
        assert chunk.org_id == org.id
        assert all(chunk.embedding == embedding)
