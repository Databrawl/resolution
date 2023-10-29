import sys

from langchain.document_loaders import WebBaseLoader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma

from config import settings
from src.functions import search_knowledge_base


def populate(url=None):
    """Populates the vector database from the url provided"""
    if not url:
        urls = [
            "https://crypto.com/eea/cards",
            "https://crypto.com/eea/earn",
            "https://crypto.com/eea/about",
            "https://crypto.com/eea/careers",
            "https://crypto.com/eea",
            "https://crypto.com/eea/fftb",
            "https://crypto.com/eea/security",
            "https://crypto.com/eea/partners",
            "https://crypto.com/eea/defi-wallet"
        ]
    else:
        urls = [url]

    loader = WebBaseLoader(urls)
    documents = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=400,
        chunk_overlap=50,
        length_function=len
    )
    texts = text_splitter.split_documents(documents)
    Chroma.from_documents(texts, OpenAIEmbeddings(), persist_directory=settings.CHROMA_DIRECTORY)


def get():
    return Chroma(persist_directory=settings.CHROMA_DIRECTORY, embedding_function=OpenAIEmbeddings())


def retrieve(q, k=5):
    return search_knowledge_base(q, k=k)


if __name__ == '__main__':
    # check first command line argument, if it's query, then query the database
    if len(sys.argv) > 1 and sys.argv[1] == 'query':
        print(retrieve(sys.argv[2]))
    else:
        populate(settings.KNOWLEDGE_URL)
