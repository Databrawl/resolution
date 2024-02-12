from uuid import uuid4

import psycopg2.errors
import pytest
from langchain.memory import ConversationBufferWindowMemory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.messages import HumanMessage, AIMessage
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError

from db import db
from db.models import Message
from db.tests.factories import MessageFactory, ChatFactory
from memory import load, save


class TestLoad:
    def test_existing_messages(self):
        """Test that we can correctly load the memory from the Database objects"""
        chat = ChatFactory.create()

        MessageFactory.create(user_message="Hello", ai_message="Hey, how can I help you?", chat=chat)
        MessageFactory.create(user_message="What is the time?", ai_message="It's high time!", chat=chat)
        MessageFactory.create(user_message="Really?", ai_message="Yup, exactly.", chat=chat)

        memory = load(chat.id, k=3)

        assert len(memory.chat_memory.messages) == 6
        assert memory.chat_memory.messages[0].content == "Hello"
        assert memory.chat_memory.messages[1].content == "Hey, how can I help you?"
        assert memory.chat_memory.messages[4].content == "Really?"
        assert memory.chat_memory.messages[5].content == "Yup, exactly."

    def test_empty_history(self):
        chat = ChatFactory.create()

        memory = load(chat.id, k=3)

        assert len(memory.chat_memory.messages) == 0

    def test_non_existing_chat(self):
        memory = load(str(uuid4()), k=3)

        assert len(memory.chat_memory.messages) == 0

    def test_history_longer_than_k(self):
        chat = ChatFactory.create()

        MessageFactory.create(user_message="Hello", ai_message="Hey, how can I help you?", chat=chat)
        MessageFactory.create(user_message="What is the time?", ai_message="It's high time!", chat=chat)
        MessageFactory.create(user_message="Really?", ai_message="Yup, exactly.", chat=chat)

        memory = load(chat.id, k=2)  # here we control the amount of message pairs to include

        assert len(memory.chat_memory.messages) == 4
        assert memory.chat_memory.messages[0].content == "Hello"
        assert memory.chat_memory.messages[1].content == "Hey, how can I help you?"
        assert memory.chat_memory.messages[2].content == "What is the time?"
        assert memory.chat_memory.messages[3].content == "It's high time!"


class TestSave:
    def test_existing_chat(self):
        chat = ChatFactory.create()
        user_message = "Hello, dear REsolution team!"
        ai_message = "Hey, how can I help you?"

        save(chat.id, user_message, ai_message)

        stmt = select(Message)
        messages = list(db.session.execute(stmt).scalars())
        assert len(messages) == 1
        assert messages[0].user_message == user_message
        assert messages[0].ai_message == ai_message

    def test_no_chat(self):
        user_message = "Hello, dear REsolution team!"
        ai_message = "Hey, how can I help you?"

        save(str(uuid4()), user_message, ai_message)
        # this should raise an exception
        with pytest.raises(IntegrityError):
            db.session.flush()
