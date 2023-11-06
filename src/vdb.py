import sys
from pprint import pprint

from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import WebBaseLoader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.schema import SystemMessage, HumanMessage
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from unstructured.cleaners.core import clean_bullets, clean_dashes, clean_extra_whitespace, \
    clean_non_ascii_chars, clean_ordered_bullets, clean_trailing_punctuation, group_broken_paragraphs, \
    replace_unicode_quotes

from config import settings
from src.functions import search_knowledge_base

COMPRESS_PROMPT = """
You are an expert Data Analyst that knows how to clean the unstructured data and distill the important information from any text input.

# Methodology
- Understand the structure of the text
- Extract the information in short sentences that make sense for another LLM that can read your output.
- No data loss should happen during this process. All the details, numbers, contacts, places, etc. should be preserved.
- Verbose wording, filler words, and noisy information can be omitted

# Output format
Output the sentences one in a line, after a dash (-). For table data, use a format that is most clear for you.
"""


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

    compressor_llm = ChatOpenAI(
        temperature=0,
        model=settings.GPT_4,
    )

    for document in documents:
        for cleaner in cleaners:
            document.page_content = cleaner(document.page_content)

        messages = [
            SystemMessage(
                content=COMPRESS_PROMPT
            ),
            HumanMessage(
                content=document.page_content
            ),
        ]
        compressed = compressor_llm(messages)
        print('this is what we got')
        pprint(compressed)

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
