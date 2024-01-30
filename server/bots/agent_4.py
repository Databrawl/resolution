from __future__ import annotations

import logging

from langchain.agents import AgentType, Tool, initialize_agent
from langchain.memory import ConversationBufferMemory
from langchain.prompts import MessagesPlaceholder
from langchain.prompts import PromptTemplate
from langchain.schema import StrOutputParser, SystemMessage
from langchain.schema.runnable import RunnableSerializable, RunnablePassthrough
from langchain_community.chat_models import ChatOpenAI

from db.models import Org
from memory.retriever import LlamaVectorIndexRetriever, format_docs
from settings import app_settings

logger = logging.getLogger(__name__)


def retrieval_chain() -> RunnableSerializable[str, str]:
    """
    Retrieve relevant documents and produce the response based on that context.

    The chain is initialized with the memory object.
    """

    prompt = PromptTemplate.from_template(app_settings.PROMPTS['retriever'])
    retriever = LlamaVectorIndexRetriever(metadata={"current_org": Org.current.get()})

    llm = ChatOpenAI(temperature=0,
                     openai_api_key=app_settings.OPENAI_API_KEY,
                     model_name=app_settings.GPT_4)
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
    llm = ChatOpenAI(temperature=0,
                     model=app_settings.GPT_35,
                     openai_api_key=app_settings.OPENAI_API_KEY)
    system_message = SystemMessage(content=app_settings.PROMPTS['manager'])

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
