import logging
from functools import reduce
from typing import Sequence
from typing import Union

from llama_index import Document
from llama_index import StorageContext, QueryBundle
from llama_index import (
    VectorStoreIndex,
    ServiceContext,
)
from llama_index.retrievers import VectorIndexRetriever
from llama_index.schema import NodeWithScore
from unstructured.cleaners.core import clean_bullets, clean_dashes, clean_extra_whitespace, \
    clean_non_ascii_chars, clean_ordered_bullets, clean_trailing_punctuation, \
    group_broken_paragraphs, \
    replace_unicode_quotes

from vdb.crawler import WebCrawler
from vdb.store import ChunkVectorStore
from settings import app_settings

logger = logging.getLogger(__name__)


def _clean(text: str) -> str:
    cleaners = [
        clean_bullets,
        clean_dashes,
        clean_extra_whitespace,
        clean_non_ascii_chars,  # TODO: test if it removes non-latin characters
        clean_ordered_bullets,
        clean_trailing_punctuation,
        group_broken_paragraphs,
        replace_unicode_quotes
    ]
    # Apply each cleaner function to the text in sequence
    return reduce(lambda x, cleaner: cleaner(x), cleaners, text)


def _create_documents(documents: Sequence[Document]) -> None:
    vector_store = ChunkVectorStore()

    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    service_context = ServiceContext.from_defaults(
        chunk_size=app_settings.CHUNK_SIZE, chunk_overlap=app_settings.CHUNK_OVERLAP
    )
    VectorStoreIndex.from_documents(documents, storage_context=storage_context,
                                    service_context=service_context)


def _get_index() -> VectorStoreIndex:
    vector_store = ChunkVectorStore()
    return VectorStoreIndex.from_vector_store(
        vector_store=vector_store,
        service_context=ServiceContext.from_defaults(llm=None)
    )


def archive_urls(urls: Union[str, list[str]], depth: int = 0) -> None:
    """
    Scrape provided URLs and archive the text content. If depth provided, act as a crawler and
    scrape all links to a given depth.

    :param urls: single URL or a list of URLs divided by commas
    :param depth: integer representing the depth of the crawler, None if no crawling is required
    :return:
    """
    if isinstance(urls, str):
        urls = [urls]

    loader = WebCrawler(depth=depth)
    documents = loader.load_data(urls=urls)
    logger.info(f"Loaded {len(documents)} documents from {len(urls)} URLs.")
    for document in documents:
        document.text = _clean(document.text)

    _create_documents(documents)


def archive_text(text: str) -> None:
    document = Document(text=_clean(text))

    _create_documents([document])


def retrieve(query: str, retriever_top_k: int = 5) -> list[NodeWithScore]:
    index = _get_index()
    query_bundle = QueryBundle(query)

    retriever = VectorIndexRetriever(
        index=index,
        similarity_top_k=retriever_top_k,
    )
    nodes = retriever.retrieve(query_bundle)

    return nodes


def search_knowledge_base(query, k=5):
    """Searches the knowledge base for relevant information"""
    docs = retrieve(query, retriever_top_k=k)

    return '\n'.join([d.text for d in docs])
