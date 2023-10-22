from langchain.document_loaders import WebBaseLoader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter, RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma

from src.config import settings


def populate(url):
    """Populates the vector database from the url provided"""
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


if __name__ == '__main__':
    populate(settings.KNOWLEDGE_URL)
