import copy
from typing import Any

from langchain.memory import ConversationBufferWindowMemory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.messages import messages_to_dict, BaseMessage, messages_from_dict
from sqlalchemy import select, desc

from db import db
from db.models import Message
from settings import app_settings


def _deserialize_messages(messages: list[Message]) -> list[BaseMessage]:
    msg_template = {
        'data': {
            'additional_kwargs': {},
            'content': "",  # message content goes here
            'example': False,
            'type': 'ai'
        },
        'type': 'ai'
    }

    result: list[dict[str, Any]] = []
    for message in messages:
        user_msg = copy.deepcopy(msg_template)
        ai_msg = copy.deepcopy(msg_template)
        user_msg["data"]["content"] = message.user_message
        user_msg["type"] = user_msg["data"]["type"] = "human"
        ai_msg["data"]["content"] = message.ai_message
        result.extend([user_msg, ai_msg])

    return messages_from_dict(result)


def load(chat_id: str, k: int = app_settings.DEFAULT_CHAT_MEMORY_SIZE) -> ConversationBufferWindowMemory:
    """Deserialize messages from the Database and return memory object in LangChain format"""
    stmt = select(Message).where(Message.chat_id == chat_id).order_by(desc(Message.created_at)).limit(k)
    messages = list(db.session.execute(stmt).scalars())

    retrieved_messages = _deserialize_messages(messages)
    retrieved_chat_history = ChatMessageHistory(messages=retrieved_messages)

    memory = ConversationBufferWindowMemory(k=5, memory_key="memory", return_messages=True,
                                            chat_memory=retrieved_chat_history)

    return memory


def save(chat_id: str, user_message: str, team_response: str):
    msg = Message(user_message=user_message, ai_message=team_response, chat_id=chat_id)
    msg.save()
