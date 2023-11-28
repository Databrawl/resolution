import random
import uuid

from langchain.embeddings import OpenAIEmbeddings
from llama_index.constants import DEFAULT_EMBEDDING_DIM
from llama_index.schema import TextNode
from llama_index.vector_stores import VectorStoreQuery
from sqlalchemy import select

from db.models import Org, Chunk
from memory.retrievers import ChunkVectorStore


class TestChunkVectorStore:
    @staticmethod
    def _get_random_embedding():
        return [random.random() for _ in range(DEFAULT_EMBEDDING_DIM)]

    def test_add_nodes(self, dbsession):
        # Arrange
        org = Org(name="test company")
        nodes = [
            TextNode(id_=str(uuid.uuid4()), embedding=self._get_random_embedding(), text="random text 1",
                     metadata={"key": "value 1"}),
            TextNode(id_=str(uuid.uuid4()), embedding=self._get_random_embedding(), text="random text 2",
                     metadata={"key": "value 2"}),
            TextNode(id_=str(uuid.uuid4()), embedding=self._get_random_embedding(), text="random text 3",
                     metadata={"key": "value 3"}),
        ]
        dbsession.add(org)
        dbsession.commit()
        chunk_vector_store = ChunkVectorStore(org.id, dbsession)

        # Act
        ids = chunk_vector_store.add(nodes)

        # Assert

        chunks = dbsession.execute(select(Chunk)).scalars().all()
        assert len(chunks) == 3
        node_texts = ["random text 1", "random text 2", "random text 3"]
        node_metadata_values = ["value 1", "value 2", "value 3"]
        for chunk in chunks:
            assert any(node_texts[i] in chunk.data["_node_content"] for i in range(len(node_texts)))
            assert chunk.data['key'] in node_metadata_values
            assert str(chunk.id) in ids
        assert len(ids) == len(nodes)
        assert all(id in ids for id in [node.node_id for node in nodes])

    def test_query(self, dbsession):
        # Arrange
        org = Org(name="test company")
        embeddings_model = OpenAIEmbeddings()
        texts = [
            "Hi there!",
            "Oh, hello!",
            "What's your name?",
            "My friends call me World",
            "Hello World!"
        ]
        nodes = [
            TextNode(id_=str(uuid.uuid4()), embedding=embeddings_model.embed_query(text), text=text,
                     metadata={"key": "value 1"})
            for text in texts
        ]
        dbsession.add(org)
        dbsession.commit()
        chunk_vector_store = ChunkVectorStore(org.id, dbsession)
        ids = chunk_vector_store.add(nodes)
        # Now set up the query
        query_str = "Hello World!"
        query_embedding = embeddings_model.embed_query(query_str)
        query = VectorStoreQuery(query_embedding=query_embedding, query_str=query_str, similarity_top_k=3)

        # Act
        query_results = chunk_vector_store.query(query)

        # Assert
        # target_chunk = dbsession.execute(select(Chunk).where(Chunk.data == query_str)).scalar_one()
        target_chunk = Chunk.get(dbsession, ids[4])
        assert len(query_results.nodes) == 3
        assert query_results.nodes[0].text == query_str
        assert query_results.nodes[0].node_id == str(target_chunk.id)
        assert query_results.nodes[1].text == "Hi there!"
        assert query_results.nodes[2].text == "Oh, hello!"

    def test_query_isolates_data(self, dbsession):
        # Arrange
        real_org = Org(name="real company")
        fake_org = Org(name="fake company")
        embeddings_model = OpenAIEmbeddings()
        text = "Hello World!"

        node = TextNode(
            id_=str(uuid.uuid4()),
            embedding=embeddings_model.embed_query(text),
            text=text,
            metadata={"key": "value 1"}
        )

        dbsession.add_all([real_org, fake_org])
        dbsession.commit()
        fake_vector_store = ChunkVectorStore(fake_org.id, dbsession)
        real_vector_store = ChunkVectorStore(real_org.id, dbsession)
        fake_vector_store.add([node])
        # Now set up the query
        query_embedding = embeddings_model.embed_query(text)
        query = VectorStoreQuery(query_embedding=query_embedding, query_str=text, similarity_top_k=3)

        # Act
        query_results = real_vector_store.query(query)  # chunk was added to a different vector store!

        # Assert
        # target_chunk = dbsession.execute(select(Chunk).where(Chunk.data == query_str)).scalar_one()
        assert query_results.nodes == []
