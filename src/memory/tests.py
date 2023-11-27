import random
import uuid

from llama_index.constants import DEFAULT_EMBEDDING_DIM
from llama_index.schema import TextNode
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
