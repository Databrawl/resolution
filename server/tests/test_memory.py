from uuid import uuid4

from langchain.memory import ConversationBufferWindowMemory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.messages import HumanMessage, AIMessage
from sqlalchemy import select, func

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
    def test_existing_messages(self):
        """Test that we can correctly save existing LangChain memory object to the Database"""
        raw_messages = [
            HumanMessage(content="Hello"),
            AIMessage(content="Hey, how can I help you?"),
            HumanMessage(content="What is the time?"),
            AIMessage(content="It's high time!"),
            HumanMessage(content="Really?"),
            AIMessage(content="Yup, exactly.")
        ]
        retrieved_chat_history = ChatMessageHistory(messages=raw_messages)

        memory = ConversationBufferWindowMemory(k=5, memory_key="memory", return_messages=True,
                                                chat_memory=retrieved_chat_history)
        chat = ChatFactory.create()

        save(chat.id, memory)

        stmt = select(Message).where(Message.chat_id == chat.id).order_by(Message.created_at)
        db_messages = list(db.session.execute(stmt).scalars())

        assert len(list(db_messages)) == 3
        assert db_messages[0].user_message == "Hello"
        assert db_messages[0].ai_message == "Hey, how can I help you?"
        assert db_messages[1].user_message == "What is the time?"
        assert db_messages[1].ai_message == "It's high time!"
        assert db_messages[2].user_message == "Really?"
        assert db_messages[2].ai_message == "Yup, exactly."

    def test_empty_history(self):
        chat = ChatFactory.create()
        memory = ConversationBufferWindowMemory(k=5, memory_key="memory", return_messages=True)

        save(chat.id, memory)

        stmt = select(func.count()).select_from(Message).where(Message.chat_id == chat.id)
        count = db.session.execute(stmt).scalar()
        assert count == 0

    def test_non_existing_chat(self):
        memory = ConversationBufferWindowMemory(k=5, memory_key="memory", return_messages=True)

        save(str(uuid4()), memory)

        stmt = select(func.count()).select_from(Message)
        count = db.session.execute(stmt).scalar()
        assert count == 0

    def test_history_longer_than_k(self):
        pass
