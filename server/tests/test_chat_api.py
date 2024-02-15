import json
from unittest.mock import patch
from uuid import uuid4

from chalice.test import Client
from sqlalchemy import func

from app import app
from db import db
from db.models import Chat
from db.tests.factories import UserFactory, ChatFactory


def test_create_chat():
    UserFactory.create()

    with Client(app) as client:
        response = client.http.post(
            "/chats",
            headers={"Content-Type": "application/json"},
            body=json.dumps({"name": "Test Chat"})
        )
        body = response.json_body

        assert "chat_id" in body
        assert "user_id" in body
        assert "creation_time" in body
        assert body["chat_name"] == "Test Chat"


@patch("chat_api.call_manager")
def test_create_message(mock_call_manager):
    agent_message = "Hello, how can I help you?"
    chat = ChatFactory.create()

    mock_call_manager.return_value.run.return_value = agent_message

    with Client(app) as client:
        response = client.http.post(
            "/messages",
            headers={"Content-Type": "application/json"},
            body=json.dumps({"user_message": "How are you?", "chat_id": str(chat.id)})
        )
        body = response.json_body

        assert "user_message" in body
        assert body["assistant"] == agent_message


def test_no_chats():
    assert db.session.query(func.count(Chat.id)).scalar() == 0
