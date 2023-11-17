import logging
import logging
import sys
from functools import reduce
from pprint import pprint
from typing import Sequence
from typing import Union

from langchain.vectorstores import SupabaseVectorStore
from llama_index import StorageContext, Response, QueryBundle
from llama_index import (
    VectorStoreIndex,
    ServiceContext,
)
from llama_index import download_loader, Document
from llama_index import (
    get_response_synthesizer,
)
from llama_index.query_engine import RetrieverQueryEngine
from llama_index.retrievers import VectorIndexRetriever
from llama_index.schema import NodeWithScore
from llama_index.vector_stores import SupabaseVectorStore
from supabase.client import Client, create_client
from unstructured.cleaners.core import clean_bullets, clean_dashes, clean_extra_whitespace, \
    clean_non_ascii_chars, clean_ordered_bullets, clean_trailing_punctuation, group_broken_paragraphs, \
    replace_unicode_quotes

from config import settings

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

BeautifulSoupWebReader = download_loader("BeautifulSoupWebReader")


def _get_client() -> Client:
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)


def _clean(text: str) -> str:
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

    # Apply each cleaner function to the text in sequence
    return reduce(lambda x, cleaner: cleaner(x), cleaners, text)


def _create_documents(documents: Sequence[Document]) -> None:
    vector_store = SupabaseVectorStore(
        postgres_connection_string=settings.SUPABASE_DB,
        collection_name=settings.SUPABASE_DOCUMENTS_TABLE
    )
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    service_context = ServiceContext.from_defaults(
        chunk_size=settings.CHUNK_SIZE, chunk_overlap=settings.CHUNK_OVERLAP
    )
    VectorStoreIndex.from_documents(documents, storage_context=storage_context, service_context=service_context)


def archive_urls(urls: Union[str, list[str]]) -> None:
    if isinstance(urls, str):
        urls = [urls]

    loader = BeautifulSoupWebReader()
    documents = loader.load_data(urls=urls)
    for document in documents:
        document.text = _clean(document.text)

    _create_documents(documents)


def archive_text(text: str) -> None:
    document = Document(text=_clean(text))

    _create_documents([document])


def get_index() -> VectorStoreIndex:
    vector_store = SupabaseVectorStore(
        postgres_connection_string=settings.SUPABASE_DB,
        collection_name=settings.SUPABASE_DOCUMENTS_TABLE
    )
    return VectorStoreIndex.from_vector_store(vector_store=vector_store)


def retrieve(query: str, retriever_top_k: int = 5) -> list[NodeWithScore]:
    index = get_index()
    query_bundle = QueryBundle(query)

    retriever = VectorIndexRetriever(
        index=index,
        similarity_top_k=retriever_top_k,
    )
    nodes = retriever.retrieve(query_bundle)

    return nodes


def query_llama(query: str, k: int = 5) -> Response:
    index = get_index()

    retriever = VectorIndexRetriever(
        index=index,
        similarity_top_k=k,
    )

    query_engine = RetrieverQueryEngine(
        retriever=retriever,
        response_synthesizer=get_response_synthesizer(),
    )

    return query_engine.query(query)


if __name__ == '__main__':
    # check first command line argument, if it's query, then query the database
    if len(sys.argv) > 1 and sys.argv[1] == 'query':
        results = retrieve(sys.argv[2])
        pprint(results)
    else:
        archive_urls(settings.KNOWLEDGE_URLS)
