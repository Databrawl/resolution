from typing import Dict, List

from langchain.callbacks.manager import CallbackManagerForRetrieverRun
from langchain.pydantic_v1 import Field
from langchain.schema import BaseRetriever, Document

from db.models import Org
from vdb.utils import retrieve


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
        # First, enable the context from the metadata since it was lost in the thread initialization
        Org.current.set(self.metadata['current_org'])

        # Then, retrieve the documents
        nodes = retrieve(query, **self.query_kwargs)

        return [Document(page_content=node.text, metadata=node.metadata)
                for node in nodes]


def format_docs(docs):
    return "\n\n".join(doc.page_content + f"\nURL: {doc.metadata['URL']}" for doc in docs)
