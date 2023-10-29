from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma

from src.config import settings


def search_knowledge_base(query, k=5):
    """Searches the knowledge base for relevant information"""
    embeddings = OpenAIEmbeddings()
    vdb = Chroma(persist_directory=settings.CHROMA_DIRECTORY, embedding_function=embeddings)
    docs = vdb.similarity_search(query, k=k)

    return '\n'.join([d.page_content for d in docs])


search_knowledge_base_config = {
    "name": "search_knowledge_base",
    "description": "Search over the company's knowledge base for the relevant information",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Search query",
            }
        },
        "required": ["query"],
    },
}
