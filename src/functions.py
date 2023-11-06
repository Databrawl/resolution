import os
from typing import List

import chromadb
from chromadb.utils import embedding_functions
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.pydantic_v1 import BaseModel, Field
from langchain.vectorstores import Chroma

from src.config import settings


class Node(BaseModel):
    """Single text chunk entry in the Vector Database"""
    # model_config = ConfigDict(arbitrary_types_allowed=True)

    uuid: str = Field(..., description="Text chunk identifier in UUID format")
    content: str = Field(..., description="The content itself")

    # class Config:
    #     arbitrary_types_allowed = True


class NodeList(BaseModel):
    """List of nodes, or chunks, from the Vector Database"""
    # model_config = ConfigDict(arbitrary_types_allowed=True)

    nodes: List[Node] = Field(..., description="Set of text chunks, called Nodes",
                              )

    # class Config:
    #     arbitrary_types_allowed = True


def search_knowledge_base(query, k=5, include_ids=False):
    """Searches the knowledge base for relevant information"""
    embeddings = OpenAIEmbeddings()
    vdb = Chroma(persist_directory=settings.CHROMA_DIRECTORY, embedding_function=embeddings)
    docs = vdb.similarity_search(query, k=k)

    return '\n'.join([d.page_content for d in docs])


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
