import random
import uuid

from langchain.embeddings import OpenAIEmbeddings
from llama_index.constants import DEFAULT_EMBEDDING_DIM
from llama_index.schema import TextNode
from llama_index.vector_stores import VectorStoreQuery
from sqlalchemy import select

from db import db
from db.models import Chunk, Org
from db.tests.factories import OrgFactory
from memory.store import ChunkVectorStore


class TestChunkVectorStore:
    @staticmethod
    def _get_random_embedding():
        return [random.random() for _ in range(DEFAULT_EMBEDDING_DIM)]

    def test_add_nodes(self):
        # Arrange
        org = OrgFactory.create()
        Org.current.set(org)
        nodes = [
            TextNode(id_=str(uuid.uuid4()), embedding=self._get_random_embedding(),
                     text="random text 1",
                     metadata={"key": "value 1"}),
            TextNode(id_=str(uuid.uuid4()), embedding=self._get_random_embedding(),
                     text="random text 2",
                     metadata={"key": "value 2"}),
            TextNode(id_=str(uuid.uuid4()), embedding=self._get_random_embedding(),
                     text="random text 3",
                     metadata={"key": "value 3"}),
        ]
        chunk_vector_store = ChunkVectorStore()

        # Act
        ids = chunk_vector_store.add(nodes)

        # Assert
        chunks = db.session.execute(select(Chunk)).scalars().all()
        assert len(chunks) == 3
        node_texts = ["random text 1", "random text 2", "random text 3"]
        node_metadata_values = ["value 1", "value 2", "value 3"]
        for chunk in chunks:
            assert any(node_texts[i] in chunk.data["_node_content"] for i in range(len(node_texts)))
            assert chunk.data['key'] in node_metadata_values
            assert str(chunk.id) in ids
        assert len(ids) == len(nodes)
        assert all(_id in ids for _id in [node.node_id for node in nodes])

    def test_query(self):
        # Arrange
        org = OrgFactory.create()
        Org.current.set(org)
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
        chunk_vector_store = ChunkVectorStore()
        ids = chunk_vector_store.add(nodes)
        # Now set up the query
        query_str = "Hello World!"
        query_embedding = embeddings_model.embed_query(query_str)
        query = VectorStoreQuery(query_embedding=query_embedding, query_str=query_str,
                                 similarity_top_k=3)

        # Act
        query_results = chunk_vector_store.query(query)

        # Assert
        target_chunk = Chunk.get(ids[4])
        assert len(query_results.nodes) == 3
        assert query_results.nodes[0].text == query_str
        assert query_results.nodes[0].node_id == str(target_chunk.id)
        assert query_results.nodes[1].text == "Hi there!"
        assert query_results.nodes[2].text == "Oh, hello!"

    def test_query_isolates_data(self):
        # Arrange
        real_org = OrgFactory.create(name="real company")
        fake_org = OrgFactory.create(name="fake company")
        embeddings_model = OpenAIEmbeddings()
        text = "Hello World!"

        node = TextNode(
            id_=str(uuid.uuid4()),
            embedding=embeddings_model.embed_query(text),
            text=text,
            metadata={"key": "value 1"}
        )

        Org.current.set(fake_org)
        fake_vector_store = ChunkVectorStore()
        fake_vector_store.add([node])
        # Now set up the query
        query_embedding = embeddings_model.embed_query(text)
        query = VectorStoreQuery(query_embedding=query_embedding, query_str=text,
                                 similarity_top_k=3)
        # And set the vector store to a different org
        Org.current.set(real_org)
        real_vector_store = ChunkVectorStore()

        # Act
        query_results = real_vector_store.query(
            query)  # chunk was added to a different vector store!

        # Assert
        assert query_results.nodes == []

    def test_add_duplicates(self):
        # Arrange
        org = OrgFactory.create()
        Org.current.set(org)
        node_1 = TextNode(id_=str(uuid.uuid4()), embedding=self._get_random_embedding(),
                          text="random text 1",
                          metadata={"key": "value 1"})
        nodes = [
            node_1,
            node_1,
            TextNode(id_=str(uuid.uuid4()), embedding=self._get_random_embedding(),
                     text="random text 2",
                     metadata={"key": "value 3"}),
        ]
        chunk_vector_store = ChunkVectorStore()

        # Act
        ids = chunk_vector_store.add(nodes)

        # Assert
        chunks = db.session.execute(select(Chunk)).scalars().all()
        assert len(chunks) == 2
        node_texts = ["random text 1", "random text 2"]
        for chunk in chunks:
            assert any(node_texts[i] in chunk.data["_node_content"] for i in range(len(node_texts)))
            assert str(chunk.id) in ids
        assert len(ids) == len(nodes)
        assert all(_id in ids for _id in [node.node_id for node in nodes])
