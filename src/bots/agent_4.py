from __future__ import annotations

import logging

from langchain.agents import AgentType, Tool, initialize_agent
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.prompts import MessagesPlaceholder
from langchain.prompts import PromptTemplate
from langchain.schema import StrOutputParser, SystemMessage
from langchain.schema.runnable import RunnableSerializable, RunnablePassthrough

from config import settings
from db.core import db_session, current_org
from memory.retriever import LlamaVectorIndexRetriever, format_docs

logger = logging.getLogger(__name__)


def retrieval_chain() -> RunnableSerializable[str, str]:
    """
    Retrieve relevant documents and produce the response based on that context.

    The chain is initialized with the memory object.
    """

    prompt = PromptTemplate.from_template(settings.PROMPTS['retriever'])
    retriever = LlamaVectorIndexRetriever(metadata={"db_session": db_session.get(),
                                                    "current_org": current_org.get()})

    llm = ChatOpenAI(temperature=0, model_name=settings.GPT_4)
    return (
            {
                "query": RunnablePassthrough(),
                "context": RunnablePassthrough() | retriever | format_docs,
            }
            | prompt
            | llm
            | StrOutputParser()
    )


def get_agent():
    memory = ConversationBufferMemory(memory_key="memory", return_messages=True)
    llm = ChatOpenAI(temperature=0, model=settings.GPT_35)
    system_message = SystemMessage(content=settings.PROMPTS['manager'])

    tools = [
        Tool.from_function(
            func=retrieval_chain().invoke,
            name="Retriever",
            description="Useful when you need to get the information about the product",
        )
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
        agent=AgentType.OPENAI_FUNCTIONS,
        verbose=True,
        agent_kwargs=agent_kwargs,
        memory=memory,
    )
