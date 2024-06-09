"""
Latest prompt version of the agent Guardian and his team.
To change the product, go to settings.py and change the default prompt folder.
"""

from __future__ import annotations

import logging
from functools import wraps
from operator import itemgetter

from langchain.agents import AgentType, Tool, initialize_agent, AgentExecutor
from langchain.memory import ConversationBufferWindowMemory
from langchain.prompts import MessagesPlaceholder
from langchain.prompts import PromptTemplate
from langchain.schema import StrOutputParser, SystemMessage
from langchain.schema.runnable import RunnableSerializable, RunnablePassthrough
from langchain_core.tools import StructuredTool
from langchain_openai.chat_models import ChatOpenAI
from pydantic.v1 import BaseModel, Field

from db.models import Org
from vdb.retriever import LlamaVectorIndexRetriever, format_docs
from settings import app_settings, read_prompts_to_dict

logger = logging.getLogger(__name__)


def chain_to_tool(chain):
    @wraps(chain)
    def decorated_function(**kwargs):
        # convert kwargs to a dict
        return chain(kwargs)

    return decorated_function


def call_manager(memory: ConversationBufferWindowMemory) -> AgentExecutor:
    """
    Call your best man: Customer Support Manager. He knows how to resolve any issue, and find the proper solution to any
    problem with the help of his crew.
    """
    # TODO: need to wrap this in LangSmith client to enable logging
    # import openai
    # from langsmith.wrappers import wrap_openai
    # client = wrap_openai(openai.Client(api_key=app_settings.OPENAI_API_KEY))
    #   client = wrap_openai(openai.Client())
    # llm = client.chat.completions.create(temperature=0, model=app_settings.GPT_4)

    llm = ChatOpenAI(temperature=0,
                     model=app_settings.GPT_4,
                     openai_api_key=app_settings.OPENAI_API_KEY)
    org_prompts = read_prompts_to_dict(Org.current.get().name)
    system_message = SystemMessage(content=org_prompts['manager'])

    tools = [
        StructuredTool.from_function(
            func=chain_to_tool(retrieval_chain(org_prompts).invoke),
            name="Product_Knowledge_Assistant",
            description="When the query of the customer is related to the product knowledge and any details about it.",
            args_schema=RetrievalChainInput,
        ),
        Tool.from_function(
            func=feedback_chain(org_prompts).invoke,
            name="Feedback_assistant",
            description="When the query if the customer is related to the feedback, improvements or feature request.\nHow to interact: Provide the details of the customer's query and if this is not the first iteration of the feedback, make sure to provide a context that was already been discussed with the customer to not repeat the same things.",
        ),
        Tool.from_function(
            func=get_agent_issuer(org_prompts).invoke,
            name="Issues_assistant",
            description="When the query of the customer is related to a bug, a problem or any difficulty that he is struggling with.\nHow to interact: Provide the information of what problem does the customer has with the context of previous advice and help that you provided to the customer and what customer has already tried to solve it. It is important for you both to not repeat same questions/advices to the customer. Also try not to ask more than 5 questions in one message.",
        ),
        Tool.from_function(
            func=switch_to_human_chain(org_prompts).invoke,
            name="Switch_to_human_assistant",
            description="When the customer wants to transfer the request to the human or you decide it yourself because this is the only solution.\nHow to interact: Provide the details about the status of the conversation and the level of satisfaction and mood level of the client at this moment.",
        ),
        Tool.from_function(
            func=fatality_chain(org_prompts).invoke,
            name="Conversation_finisher",
            description="When you need to manage all types of conversation endings with the customer.\nHow to interact with this team member: Tell that the customer is ready to finish the conversation and provide his satisfaction level, mood level and the current conversation status.",
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


class RetrievalChainInput(BaseModel):
    user_question: str = Field(description="Forward the current user question")
    query: str = Field(description="keyword search query")


def retrieval_chain(prompts: dict[str, str]):
    """
    Product knowledge assistant.
    Retrieve relevant documents from the knowledge base and produce the response based on that context.
    """

    prompt = PromptTemplate.from_template(prompts['product_knowledge'])
    retriever = LlamaVectorIndexRetriever(metadata={"current_org": Org.current.get()})

    llm = ChatOpenAI(temperature=0,
                     openai_api_key=app_settings.OPENAI_API_KEY,
                     model_name=app_settings.GPT_35)
    return (
            {
                "query": itemgetter("user_question"),
                "context": itemgetter("query") | retriever | format_docs,
            }
            | prompt
            | llm
            | StrOutputParser()
    )


def feedback_chain(prompts: dict[str, str]) -> RunnableSerializable[str, str]:
    """
    Feedback assistant. Deals with any feedback type queries from the customer.
    """

    prompt = PromptTemplate.from_template(prompts['feedback'])

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


def get_agent_issuer(prompts: dict[str, str]) -> AgentExecutor:
    """
    Issuer. Deals with any types of customers' problems.
    """
    memory = ConversationBufferWindowMemory(k=5, memory_key="memory", return_messages=True)
    llm = ChatOpenAI(temperature=0,
                     model=app_settings.GPT_35,
                     openai_api_key=app_settings.OPENAI_API_KEY)
    system_message = SystemMessage(content=prompts['issuer'])

    tools = [
        StructuredTool.from_function(
            func=chain_to_tool(retrieval_chain(prompts).invoke),
            name="Product_Knowledge_Assistant",
            description="When you need to retrieve the information from the product knowledge base",
            args_schema=RetrievalChainInput,
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


def switch_to_human_chain(prompts: dict[str, str]) -> RunnableSerializable[str, str]:
    """
    Switch to human. Allows transfer requests and support to the internal team.
    """

    prompt = PromptTemplate.from_template(prompts['human'])

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


def fatality_chain(prompts: dict[str, str]) -> RunnableSerializable[str, str]:
    """
    Conversation finisher. Knows how to make a nice end to the conversation.
    """

    prompt = PromptTemplate.from_template(prompts['finisher'])

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
