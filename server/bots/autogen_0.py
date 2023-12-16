"""
AutoGen, Microsoft tool.

https://microsoft.github.io/autogen/docs/Use-Cases/agent_chat/
https://microsoft.github.io/autogen/docs/getting-started
"""
import os
import sys

from autogen import AssistantAgent, UserProxyAgent, GroupChat, GroupChatManager

SRC_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.dirname(SRC_ROOT)

# setting path
sys.path.append(SRC_ROOT)
sys.path.append(PROJECT_ROOT)



def ask(question: str, chat_messages: list = None):
    # Create assistant agent
    support_agent = AssistantAgent(
        name="customer_support",
        system_message=app_settings.SUPPORT_AGENT_INSTRUCTIONS,
        # system_message="You are a support agent. You are helpful assistant, you answer customer's questions, you always search for the answer in the knowledge base and you wait for the approval from the reviewer; Add TERMINATE to the end of your final response.",
        llm_config={"config_list": app_settings.AUTOGEN_CONFIG_LIST})

    reviewer = AssistantAgent(
        name="reviewer",
        system_message=app_settings.REVIEWER_INSTRUCTIONS,
        # system_message="You are a Senior customer support manager. You review the answers from the customer_support agent and approve them if they conform to the company's knowledge base and are not repetitive; Add TERMINATE to the end when you are satisfied with the agent's answer.",
        llm_config={"config_list": app_settings.AUTOGEN_CONFIG_LIST}
    )

    # Create user proxy agent
    user_proxy = UserProxyAgent(
        name="user_proxy",
        # system_message="A human customer. Interact with customer_support to communicate your request. Ask clarifying questions if the answer does not satisfy you.",
        system_message="""Reply TERMINATE if the task has been solved at full satisfaction. Otherwise, reply CONTINUE, or the reason why the task is not solved yet.""",
        human_input_mode="NEVER",
        max_consecutive_auto_reply=0,
        is_termination_msg=lambda x: x.get("content", "") and x.get(
            "content", "").rstrip().endswith("TERMINATE"),
    )

    groupchat = GroupChat(
        agents=[user_proxy, support_agent, reviewer],
        messages=chat_messages or [],
        max_round=20)
    manager = GroupChatManager(groupchat=groupchat,
                               llm_config={"config_list": app_settings.AUTOGEN_CONFIG_LIST}
                               )

    # manager should just pass the message over to the rest of the team
    # Start the conversation
    user_proxy.initiate_chat(manager, message=question)

    # user_proxy.stop_reply_at_receive(manager)
    messages = user_proxy.chat_messages[manager]
    return messages
