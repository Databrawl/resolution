"""
Store the information in the database

The information can be either text or URLs. In case it's URLs, the text is extracted from the page and the linked pages
from the same domain.

* Also keeps the conversation memory, last 8 messages

# TODO: Remove redundant \n, \t, and spaces from the document.page_content
# TODO: Add source (URL or text data) to the VDB entries. Make it work as an ID. This way we can update the information.
# TODO: Add a tool to delete the information from the database
# TODO: Check if the information is already in the database and add update functionality

References:
    * https://python.langchain.com/docs/modules/agents/how_to/custom-functions-with-openai-functions-agent
        defining functions for the agent. It shows how to specify types, so that you don't need to convert list manually
"""
import json
import logging
import os
import sys

import requests
from langchain.agents import initialize_agent, AgentType, Tool
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import WebBaseLoader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.memory import ConversationBufferWindowMemory
from langchain.prompts import MessagesPlaceholder
from langchain.schema import SystemMessage
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma

from src.functions import search_knowledge_base

SRC_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.dirname(SRC_ROOT)

# setting path
sys.path.append(SRC_ROOT)
sys.path.append(PROJECT_ROOT)

from src import vdb

db = vdb.get()
memory = ConversationBufferWindowMemory(memory_key="librarian_memory", return_messages=True, k=8)
tickets = {}

SRC_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.dirname(SRC_ROOT)

# setting path
sys.path.append(SRC_ROOT)
sys.path.append(PROJECT_ROOT)

from src.config import settings

logger = logging.getLogger(__name__)


def archive(data):
    print('Archiving text data:')
    print(data)
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=400,
        chunk_overlap=50,
        length_function=len
    )
    texts = text_splitter.split_text(data)
    Chroma.from_texts(texts, OpenAIEmbeddings(), persist_directory=settings.CHROMA_DIRECTORY)


def scrape_urls(urls):
    urls_decoded = urls.split(';')
    loader = WebBaseLoader(urls_decoded)
    documents = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=400,
        chunk_overlap=50,
        length_function=len
    )
    split_documents = text_splitter.split_documents(documents)
    Chroma.from_documents(split_documents, OpenAIEmbeddings(), persist_directory=settings.CHROMA_DIRECTORY)


def librarian_agent():
    instructions = """
    You are an experienced Data analyst working for Crypto.com. You are chatting with your manager.
    You are being given text data and URLs to store in the Knowledge base or being asked about the data that is
    available in the knowledge base. Therefore, your tasks include either accessing the knowledge base or storing the
    data there.

    If you need to store data, follow this procedure:
    1. First, identify URLs that need to be scraped for text data. Exclude them.
    2. Then, store the text data in the knowledge base using Archive_text_data if there's anything besides the URLs.
    3. Finally, use the Archive_URLs tool to scrape and store the data from the URLs found on step 1. Call this tool
    with all URLs at once. Separate them with a ; (semicolon).

    If you need to retrieve data use the Retrieve_data tool. Don't use any other data if you're being asked a specific
    question. Don't make things up. Use only the data from the knowledge base.
    """
    system_message = SystemMessage(
        content=instructions
    )

    agent_kwargs = {
        "extra_prompt_messages": [MessagesPlaceholder(variable_name="librarian_memory")],
        "system_message": system_message,
    }

    llm = ChatOpenAI(temperature=0, model=settings.GPT_35)
    tools = [
        Tool(
            name="Archive_text_data",
            func=archive,
            description="Store text data in the knowledge base."
        ),
        Tool(
            name="Archive_URLs",
            func=scrape_urls,
            description="Scan provided URLs for text data and save it in the knowledge base."
        ),
        Tool(
            name="Retrieve_data",
            func=search_knowledge_base,
            description="Retrieve data from the knowledge base."
        )
    ]

    agent = initialize_agent(
        tools,
        llm,
        agent=AgentType.OPENAI_FUNCTIONS,
        agent_kwargs=agent_kwargs,
        memory=memory,
        verbose=True,
    )

    return agent


if __name__ == '__main__':
    while True:
        user_input = input('>>> ')
        response = librarian_agent().run(user_input)
        print(response)
