from uuid import uuid4

import pytest
from llama_index.constants import DEFAULT_EMBEDDING_DIM
from sqlalchemy import exc, select

from db import db
from db.models import Chunk, Org, User
from db.tests.factories import OrgFactory, UserFactory, ChunkFactory, OrgUserFactory


class TestBase:
    def test_get_existing(self):
        org = OrgFactory.create(name='test company')

        retrieved_org = Org.get(org.id)

        assert retrieved_org.name == 'test company'

    def test_get_reflected_model(self):
        user = UserFactory.create()

        retrieved_user = User.get(user.id)

        assert retrieved_user.email == user.email

    def test_get_non_existing(self):
        with pytest.raises(exc.NoResultFound):
            Org.get(str(uuid4()))


class TestOrg:
    def test_similarity_search_trivial(self):
        org = OrgFactory.create(name='test company')

        expected_chunks = []
        for i in range(5):
            embedding = [0] * DEFAULT_EMBEDDING_DIM
            embedding[i] = 100
            chunk = ChunkFactory.create(org=org, data={"text": f"Chunk {i}"}, embedding=embedding)
            expected_chunks.append(chunk)

        search_embedding = [0] * DEFAULT_EMBEDDING_DIM
        search_embedding[0] = 100
        chunks_with_similarities = org.similarity_search(search_embedding)

        assert len(chunks_with_similarities) == 5
        assert chunks_with_similarities[0] == (expected_chunks[0], 1.0)
        assert all(chunks_with_similarities[i][1] == 0.0 for i in range(1, 5))


class TestChunk:
    def test_create_chunk_instance_with_valid_values(self):
        org = OrgFactory.create(name='test company')
        chunk = ChunkFactory.create(org=org, data={"text": "Chunk"})

        assert chunk.id is not None
        assert chunk.org_id == org.id

    def test_create_chunk_instance_with_invalid_embedding_length(self):
        wrong_embedding_len = 10
        embedding = [1.0] * wrong_embedding_len
        org = OrgFactory.create(name='test company')
        with pytest.raises(exc.StatementError):
            ChunkFactory.create(org=org, embedding=embedding)

    def test_create_same_chunks_same_org(self):
        org = OrgFactory.create(name='test company')
        ChunkFactory.create(org=org, data={"text": "Chunk"})
        with pytest.raises(exc.IntegrityError):
            ChunkFactory.create(org=org, data={"text": "Chunk"})

    def test_create_different_chunks_same_org(self):
        org = OrgFactory.create(name='test company')

        ChunkFactory.create(org=org, data={"text": "Chunk 1"})
        ChunkFactory.create(org=org, data={"text": "Chunk 2"})

        chunks = db.session.execute(select(Chunk)).all()
        assert len(chunks) == 2

    def test_create_same_chunk_different_orgs(self):
        org_1 = OrgFactory.create(name='test company 1')
        org_2 = OrgFactory.create(name='test company 2')
        ChunkFactory.create(org=org_1, data={"text": "Chunk"})
        ChunkFactory.create(org=org_2, data={"text": "Chunk"})

        rows = db.session.execute(select(Chunk)).all()
        assert len(rows) == 2
        assert rows[0].Chunk.org_id != rows[1].Chunk.org_id


class TestGeneric:
    def test_all_models_together(self):
        """ Test that all models can be created together """
        user = UserFactory.create()
        org = OrgFactory.create(name='test company')
        embedding = [1.0] * DEFAULT_EMBEDDING_DIM
        chunk = ChunkFactory.create(org=org, embedding=embedding)

        OrgUserFactory.create(user=user, org=org)

        assert chunk.id is not None
        assert chunk.org == org
        assert all(chunk.embedding == embedding)
