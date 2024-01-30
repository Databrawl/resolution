"""
Simple agent with a single Retriever tool, which doesn't do query pre-processing
"""
from __future__ import annotations

import logging

from langchain.agents import AgentType, Tool, initialize_agent
from langchain.memory import ConversationBufferMemory
from langchain.prompts import MessagesPlaceholder
from langchain.prompts import PromptTemplate
from langchain.schema import StrOutputParser, BaseMemory, \
    SystemMessage
from langchain.schema.runnable import RunnableSerializable, RunnablePassthrough
from langchain_community.chat_models import ChatOpenAI

from memory.retriever import LlamaVectorIndexRetriever, format_docs

logger = logging.getLogger(__name__)


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

    prompt = PromptTemplate.from_template(prompt_template)
    retriever = LlamaVectorIndexRetriever(metadata={"db_session": db_session.get(),
                                                    "current_org": current_org.get()})

    llm = ChatOpenAI(temperature=0, model_name=app_settings.GPT_4)
    return (
            {
                "context": RunnablePassthrough() | retriever | format_docs,
                "chat_history": lambda _: memory.buffer_as_str
            }
            | prompt
            | llm
            | StrOutputParser()
    )


def get_agent():
    memory = ConversationBufferMemory(memory_key="memory", return_messages=True)
    llm = ChatOpenAI(temperature=0, model=app_settings.GPT_35)
    system_message = SystemMessage(content=app_settings.PROMPTS['manager'])

    tools = [
        Tool.from_function(
            func=retrieval_chain(memory).invoke,
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
        agent=AgentType.OPENAI_MULTI_FUNCTIONS,
        verbose=True,
        agent_kwargs=agent_kwargs,
        memory=memory,
    )
