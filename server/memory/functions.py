import os
from typing import List

from langchain.pydantic_v1 import BaseModel, Field

from memory.utils import retrieve
from server.config import settings


class Node(BaseModel):
    """Single text chunk entry in the Vector Database"""
    # model_config = ConfigDict(arbitrary_types_allowed=True)

    uuid: str = Field(..., description="Text chunk identifier in UUID format")
    content: str = Field(..., description="The content itself")


class NodeList(BaseModel):
    """List of nodes, or chunks, from the Vector Database"""
    # model_config = ConfigDict(arbitrary_types_allowed=True)

    nodes: List[Node] = Field(..., description="Set of text chunks, called Nodes")


def search_knowledge_base(query, k=5, include_ids=False):
    """Searches the knowledge base for relevant information"""
    docs = retrieve(query, retriever_top_k=k)

    return '\n'.join([d.text for d in docs])


def search_native(query: str) -> NodeList:
    """Searches the knowledge base for relevant information.

    Args:
        query: str, the query to search for
    """
    client = chromadb.PersistentClient(path=settings.CHROMA_DIRECTORY)
    openai_ef = embedding_functions.OpenAIEmbeddingFunction(
        api_key=os.environ["OPENAI_API_KEY"],
        model_name="text-embedding-ada-002"
    )
    collection = client.get_collection(name="langchain", embedding_function=openai_ef)
    search_results = collection.query(query_texts=[query], n_results=5)

    results = []
    for _id, doc in zip(search_results['ids'][0], search_results['documents'][0]):
        results.append(Node(uuid=_id, content=doc))

    return NodeList(nodes=results)


def search_native_formatted(query: str) -> str:
    node_list = search_native(query)
    return '\n'.join([f'{node.uuid}: {node.content}' for node in node_list.nodes])


def update_documents(nodes: NodeList) -> None:
    """Updates the documents in the Vector Database with new information.

    Args:
        nodes: NodeList, the list of documents to update
    """
    print('we have launched the function')
    if isinstance(nodes, Node):
        nodes = NodeList(nodes=[nodes])
    if not isinstance(nodes, NodeList):
        raise TypeError(f'Expected NodeList, got {type(nodes)}')
    client = chromadb.PersistentClient(path=settings.CHROMA_DIRECTORY)
    openai_ef = embedding_functions.OpenAIEmbeddingFunction(
        api_key=os.environ["OPENAI_API_KEY"],
        model_name="text-embedding-ada-002"
    )
    collection = client.get_collection(name="langchain", embedding_function=openai_ef)
    collection.update(ids=[n.uuid for n in nodes.nodes], documents=[n.content for n in nodes.nodes])


def update_documents_primitive_types(nodes_dict: dict) -> None:
    """Updates the documents in the Vector Database with new information.

    Args:
        nodes_dict: nodes to update, in the format of a dictionary
    """
    nodes = NodeList(nodes=[Node(uuid=n[0], content=n[1]) for n in nodes_dict['nodes'].items()])
    update_documents(nodes)
