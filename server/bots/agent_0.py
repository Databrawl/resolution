"""
Single agent with one tool - knowledge base retrieval
"""
import logging
import os
import sys

from langchain.agents import initialize_agent, AgentType, Tool
from langchain.memory import ConversationBufferWindowMemory
from langchain.prompts import MessagesPlaceholder
from langchain.schema import SystemMessage
from langchain_community.chat_models import ChatOpenAI

SRC_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.dirname(SRC_ROOT)

# setting path
sys.path.append(SRC_ROOT)
sys.path.append(PROJECT_ROOT)


from memory.functions import search_knowledge_base

logger = logging.getLogger(__name__)


def research_agent(id, user_name, ai_name, instructions):
    system_message = SystemMessage(
        content=instructions
    )

    agent_kwargs = {
        "extra_prompt_messages": [MessagesPlaceholder(variable_name="memory")],
        "system_message": system_message,
    }

    memory = ConversationBufferWindowMemory(memory_key="memory", return_messages=True, ai_prefix=ai_name,
                                            user_prefix=user_name)

    llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo-0613")
    tools = [
        Tool(
            name="Knowledge_retrieval",
            func=search_knowledge_base,
            description="This is your knowledge base. Always use this tool first after receiving the query."
        ),
    ]

    agent = initialize_agent(
        tools,
        llm,
        agent=AgentType.OPENAI_FUNCTIONS,
        verbose=True,
        agent_kwargs=agent_kwargs,
        memory=memory
    )

    agents[id] = agent

    return agent


agents = {}


def generate_response(instructions, user_input):
    id = user_input["id"]
    message = user_input["message"]

    if id not in agents:
        user_name = user_input["user_name"]
        ai_name = user_input["ai_name"]
        # agent = create_agent_wrapper(id, user_name, ai_name, instructions)
        agent = research_agent(id, user_name, ai_name, instructions)
    else:
        agent = agents[id]

    response = agent.run(message)

    return response


if __name__ == "__main__":
    while True:
        user_input = input('>>> ')
        response = generate_response(app_settings.SUPPORT_AGENT_INSTRUCTIONS,
                                     {'id': 0, 'message': user_input, 'user_name': 'Tyrael',
                                      'ai_name': 'Guardian'})
        print(response)
