from typing import Dict, List, Any

from langchain.callbacks.manager import CallbackManagerForRetrieverRun
from langchain.pydantic_v1 import Field
from langchain.schema import BaseRetriever, Document
from llama_index.schema import BaseNode
from llama_index.vector_stores.types import VectorStore, VectorStoreQuery, VectorStoreQueryResult
from llama_index.vector_stores.utils import node_to_metadata_dict, metadata_dict_to_node
from sqlalchemy import delete
from sqlalchemy.orm import Session

from db import db_session
from db.models import Chunk, Org
from src.vdb import retrieve


class ChunkVectorStore(VectorStore):
    def __init__(self, org_id: str) -> None:
        self.dbsession: Session = db_session.get()
        self.org: Org = Org.get(org_id)

    def client(self) -> Any:
        return

    def add(
            self,
            nodes: List[BaseNode],
            **add_kwargs: Any,
    ) -> List[str]:
        """Add nodes with embedding to vector store."""
        ids = []
        for node in nodes:
            node_data = node_to_metadata_dict(
                node, remove_text=False, flat_metadata=False
            )
            chunk = Chunk(
                id=node.node_id,
                org_id=self.org.id,
                hash_value=node.hash,
                embedding=node.embedding,
                data=node_data
            )
            self.dbsession.add(chunk)
            ids.append(node.node_id)
        self.dbsession.commit()
        return ids

    def delete(self, ref_doc_id: str, **delete_kwargs: Any) -> None:
        """Delete node from vector store."""
        stmt = delete(Chunk).where(Chunk.id == ref_doc_id)
        self.dbsession.execute(stmt)
        self.dbsession.commit()

    def query(self, query: VectorStoreQuery, **kwargs: Any) -> VectorStoreQueryResult:
        """Query vector store."""
        # Filters are not supported yet
        chunks_with_similarities = self.org.similarity_search(
            embedding=query.query_embedding,
            k=query.similarity_top_k
        )

        similarities = []
        ids = []
        nodes = []
        for chunk, similarity in chunks_with_similarities:
            node = metadata_dict_to_node(chunk.data)

            nodes.append(node)
            similarities.append(similarity)
            ids.append(node.node_id)

        return VectorStoreQueryResult(nodes=nodes, similarities=similarities, ids=ids)


class LlamaVectorIndexRetriever(BaseRetriever):
    """`LlamaIndex` retriever.

    It is used for the question-answering with sources over
    an LlamaIndex data structure."""

    query_kwargs: Dict = Field(default_factory=dict)
    """Keyword arguments to pass to the query method."""

    def _get_relevant_documents(
            self, query: str, *, run_manager: CallbackManagerForRetrieverRun
    ) -> List[Document]:
        """Get documents relevant for a query."""
        nodes = retrieve(query, **self.query_kwargs)

        return [Document(page_content=node.text, metadata=node.metadata)
                for node in nodes]


def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)
