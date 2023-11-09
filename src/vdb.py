import logging
import sys
from pprint import pprint

from langchain.document_loaders import WebBaseLoader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import SupabaseVectorStore
from supabase.client import Client, create_client
from unstructured.cleaners.core import clean_bullets, clean_dashes, clean_extra_whitespace, \
    clean_non_ascii_chars, clean_ordered_bullets, clean_trailing_punctuation, group_broken_paragraphs, \
    replace_unicode_quotes

from config import settings


def _get_client() -> Client:
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)


def populate(url=None):
    """Populates the vector database from the url provided"""
    if not url:
        urls = [
            "https://crypto.com/eea/cards",
            # "https://crypto.com/eea/earn",
            # "https://crypto.com/eea/about",
            # "https://crypto.com/eea/careers",
            # "https://crypto.com/eea",
            # "https://crypto.com/eea/fftb",
            # "https://crypto.com/eea/security",
            # "https://crypto.com/eea/partners",
            # "https://crypto.com/eea/defi-wallet"
        ]
    else:
        urls = [url]

    logging.info('Loading documents from URLs')
    loader = WebBaseLoader(urls)
    documents = loader.load()

    cleaners = [
        clean_bullets,
        clean_dashes,
        clean_extra_whitespace,
        clean_non_ascii_chars,
        clean_ordered_bullets,
        clean_trailing_punctuation,
        group_broken_paragraphs,
        replace_unicode_quotes
    ]

    # clean documents
    for document in documents:
        for cleaner in cleaners:
            document.page_content = cleaner(document.page_content)

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=50,
        length_function=len
    )
    texts = text_splitter.split_documents(documents)

    logging.info(f'Populating vector database with {urls} data')
    SupabaseVectorStore.from_documents(
        texts,
        OpenAIEmbeddings(),
        client=_get_client(),
        table_name="documents",
        query_name="match_documents",
    )
    logging.info('Vector database population completed')


def retrieve(q, k=5):
    vector_store = SupabaseVectorStore(
        embedding=OpenAIEmbeddings(),
        client=_get_client(),
        table_name="documents",
        query_name="match_documents",
    )
    return vector_store.similarity_search(q, k=k)


if __name__ == '__main__':
    # check first command line argument, if it's query, then query the database
    if len(sys.argv) > 1 and sys.argv[1] == 'query':
        pprint(retrieve(sys.argv[2]))
    else:
        populate(settings.KNOWLEDGE_URL)
