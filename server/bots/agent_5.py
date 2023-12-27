"""
Latest prompt version of the agent Guardian and his team.
To change the product, go to main.py and change the prompt folder.
"""

from __future__ import annotations

import logging

from langchain.agents import AgentType, Tool, initialize_agent
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.prompts import MessagesPlaceholder
from langchain.prompts import PromptTemplate
from langchain.schema import StrOutputParser, SystemMessage
from langchain.schema.runnable import RunnableSerializable, RunnablePassthrough

from db.models import Org
from memory.retriever import LlamaVectorIndexRetriever, format_docs
from settings import app_settings

logger = logging.getLogger(__name__)


def get_agent():
    memory = ConversationBufferMemory(memory_key="memory", return_messages=True)
    llm = ChatOpenAI(temperature=0,
                     model=app_settings.GPT_4,
                     openai_api_key=app_settings.OPENAI_API_KEY)
    system_message = SystemMessage(content=app_settings.PROMPTS['manager'])

    tools = [
        Tool.from_function(
            func=retrieval_chain_1().invoke,
            name="Product_Knowledge_Assistant",
            description="When the query of the customer is related to the product knowledge and any details about it.",
        ),
        Tool.from_function(
            func=retrieval_chain_2().invoke,
            name="Feedback_assistant",
            description="When the customer’s query relates to the feedback, improvements or feature request.",
        ),
        Tool.from_function(
            func=retrieval_chain_3().invoke,
            name="Issues_assistant",
            description="When the query of the customer is related to a bug, a problem or any difficulty that he is struggling with.",
        ),
        # Tool.from_function(
        #    func=retrieval_chain_4().invoke,
        #    name="Account_Management_assistant",
        #    description="When the customer wants to make an account management operation.",
        # ),
        Tool.from_function(
            func=retrieval_chain_5().invoke,
            name="Switch_to_human_assistant",
            description="When the customer wants to transfer the request to the human or you decide it yourself because this is the best solution.",
        ),
        Tool.from_function(
            func=retrieval_chain_6().invoke,
            name="Conversation_finisher",
            description="When you need to manage all types of conversation endings with the customer.",
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


def retrieval_chain_1() -> RunnableSerializable[str, str]:
    """
    Product knowledge assistant. Retrieve relevant documents and produce the response based on that context.
    """

    prompt = PromptTemplate.from_template(app_settings.PROMPTS['product_knowledge'])
    retriever = LlamaVectorIndexRetriever(metadata={"current_org": Org.current.get()})

    llm = ChatOpenAI(temperature=0,
                     openai_api_key=app_settings.OPENAI_API_KEY,
                     model_name=app_settings.GPT_35)
    return (
            {
                "query": RunnablePassthrough(),
                "context": RunnablePassthrough() | retriever | format_docs,
            }
            | prompt
            | llm
            | StrOutputParser()
    )

def retrieval_chain_2() -> RunnableSerializable[str, str]:
    """
    Feedback assistant. Deals with any feedback type queries from the customer.
    """

    prompt = PromptTemplate.from_template(app_settings.PROMPTS['feedback'])

    llm = ChatOpenAI(temperature=0,
                     openai_api_key=app_settings.OPENAI_API_KEY,
                     model_name=app_settings.GPT_35)
    return (
            {
                "query": RunnablePassthrough()
            }
            | prompt
            | llm
            | StrOutputParser()
    )

def retrieval_chain_3() -> RunnableSerializable[str, str]:
    """
    Issuer. Deals with any types of customers' problems.
    """

    prompt = PromptTemplate.from_template(app_settings.PROMPTS['issuer'])
    retriever = LlamaVectorIndexRetriever(metadata={"current_org": Org.current.get()})

    llm = ChatOpenAI(temperature=0,
                     openai_api_key=app_settings.OPENAI_API_KEY,
                     model_name=app_settings.GPT_35)
    return (
            {
                "query": RunnablePassthrough(),
                "context": RunnablePassthrough() | retriever | format_docs,
            }
            | prompt
            | llm
            | StrOutputParser()
    )

# def retrieval_chain_4() -> RunnableSerializable[str, str]:
#     """
#     Account Management assistant. Deals with any account related stuff.
#     """

#     prompt = PromptTemplate.from_template(app_settings.PROMPTS['account'])
#     retriever = LlamaVectorIndexRetriever(metadata={"current_org": Org.current.get()})

#     llm = ChatOpenAI(temperature=0,
#                      openai_api_key=app_settings.OPENAI_API_KEY,
#                      model_name=app_settings.GPT_35)
#     return (
#             {
#                 "query": RunnablePassthrough(),
#                 "context": RunnablePassthrough() | retriever | format_docs,
#             }
#             | prompt
#             | llm
#             | StrOutputParser()
#     )

def retrieval_chain_5() -> RunnableSerializable[str, str]:
    """
    Switch to human. Allows transfer requests and support to the internal team.
    """

    prompt = PromptTemplate.from_template(app_settings.PROMPTS['human'])

    llm = ChatOpenAI(temperature=0,
                     openai_api_key=app_settings.OPENAI_API_KEY,
                     model_name=app_settings.GPT_35)
    return (
            {
                "query": RunnablePassthrough()
            }
            | prompt
            | llm
            | StrOutputParser()
    )

def retrieval_chain_6() -> RunnableSerializable[str, str]:
    """
    Conversation finisher. Knows how to make a nice end to the conversation.
    """

    prompt = PromptTemplate.from_template(app_settings.PROMPTS['finisher'])

    llm = ChatOpenAI(temperature=0,
                     openai_api_key=app_settings.OPENAI_API_KEY,
                     model_name=app_settings.GPT_35)
    return (
            {
                "query": RunnablePassthrough()
            }
            | prompt
            | llm
            | StrOutputParser()
    )
