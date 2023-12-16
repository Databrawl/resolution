from __future__ import annotations

import logging

from langchain.agents import AgentType, Tool, initialize_agent
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.prompts import MessagesPlaceholder
from langchain.prompts import PromptTemplate
from langchain.schema import StrOutputParser, BaseMemory, \
    SystemMessage
from langchain.schema.runnable import RunnableSerializable

from config import settings
from db.core import current_org
from memory.retriever import LlamaVectorIndexRetriever, format_docs

logger = logging.getLogger(__name__)


def query_builder_chain(memory: BaseMemory) -> RunnableSerializable[str, str]:
    prompt_template = """
    You are an expert Data analyst with 20 years of experience working with Vector Databases.

    Build a search query that will return the answer to the last question in the chat. Don't output
    anything else, just the query.

    # Chat History:

    {chat_history}

    # Search Query:
    """
    prompt = PromptTemplate.from_template(prompt_template)
    llm = ChatOpenAI(temperature=0, model_name=settings.GPT_4)

    return (
            {
                "chat_history": lambda _: memory.buffer_as_str
            }
            | prompt
            | llm
            | StrOutputParser()
    )


def retrieval_chain(memory: BaseMemory) -> RunnableSerializable[str, str]:
    """
    Retrieve relevant documents and produce the response based on that context.

    The chain is initialized with the memory object.
    """
    prompt_template = """You're an expert customer support agent.

    Read the chat history and the relevant Context and provide the answer to the question.
    Answer "I don't know" if the context does not have the answer. 

    # Context:

    {context}

    # Chat History:

    {chat_history}

    # Answer:"""
    # Question: {question}

    prompt = PromptTemplate.from_template(prompt_template)
    retriever = LlamaVectorIndexRetriever(metadata={"current_org": current_org.get()})

    llm = ChatOpenAI(temperature=0, model_name=settings.GPT_4)
    return (
            {
                "context": query_builder_chain(memory) | retriever | format_docs,
                # "question": RunnablePassthrough(),
                "chat_history": lambda _: memory.buffer_as_str
            }
            | prompt
            | llm
            | StrOutputParser()
    )


def get_agent():
    memory = ConversationBufferMemory(memory_key="memory", return_messages=True)
    # read_only_memory = ReadOnlySharedMemory(memory=memory)
    llm = ChatOpenAI(temperature=0, model=settings.GPT_35)
    system_message = SystemMessage(content=settings.PROMPTS['manager'])
    tools = [
        Tool(
            name="Retriever",
            func=retrieval_chain(memory).invoke,
            description="Useful when you need to get the information about the product",
        ),
    ]

    agent_kwargs = {
        "system_message": system_message,
        "extra_prompt_messages": [
            MessagesPlaceholder(variable_name="memory")
        ],
    }

    return initialize_agent(
        tools,
        llm,
        agent=AgentType.OPENAI_MULTI_FUNCTIONS,
        verbose=True,
        agent_kwargs=agent_kwargs,
        memory=memory,
    )
