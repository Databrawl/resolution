"""
The agent that properly fills the chat history: adds human message before sending it to the tools.
"""
from __future__ import annotations

import logging

from langchain.agents import Tool, AgentExecutor
from langchain.agents.format_scratchpad import format_to_openai_function_messages
from langchain.agents.output_parsers import OpenAIFunctionsAgentOutputParser
from langchain.memory import ConversationBufferMemory
from langchain.prompts import MessagesPlaceholder
from langchain.prompts import PromptTemplate, ChatPromptTemplate
from langchain.schema import BaseMemory, \
    AIMessage
from langchain.schema import HumanMessage, StrOutputParser
from langchain.schema.runnable import RunnableLambda, RunnablePassthrough
from langchain.schema.runnable import RunnableSerializable
from langchain.tools.render import format_tool_to_openai_function
from langchain_community.chat_models import ChatOpenAI

from bots.chain_s2 import save_message
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

    def save_message_passthrough(payload):
        memory.chat_memory.add_message(payload["input"])
        # passing through the whole input
        return payload

    llm = ChatOpenAI(temperature=0, model=app_settings.GPT_35)

    tools = [
        Tool.from_function(
            func=retrieval_chain(memory).invoke,
            name="Retriever",
            description="Useful when you need to get the information about the product",
        )
    ]
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", app_settings.PROMPTS['manager']),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
    )
    llm_with_tools = llm.bind(functions=[format_tool_to_openai_function(t) for t in tools])

    agent = (  # TODO: change to save human message + save agent message
            RunnableLambda(lambda m: save_message_passthrough(HumanMessage(content=m["input"])))
            | {
                "input": lambda x: x["input"],
                "agent_scratchpad": lambda x: format_to_openai_function_messages(
                    x["intermediate_steps"]
                ),
            }
            | prompt
            | llm_with_tools
            | OpenAIFunctionsAgentOutputParser()
            | RunnableLambda(lambda m: save_message(AIMessage(content=m)))
    )

    return AgentExecutor(agent=agent, tools=tools, verbose=True)
