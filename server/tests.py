import json
from unittest.mock import patch

from chalice.test import Client
from sqlalchemy import func

from app import app
from db import db
from db.models import Chat
from db.tests.factories import UserFactory


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


@patch("chat_api.get_agent")
def test_create_message(mock_get_agent):
    agent_message = "Hello, how can I help you?"

    mock_get_agent.return_value.run.return_value = agent_message

    with Client(app) as client:
        response = client.http.post(
            "/messages",
            headers={"Content-Type": "application/json"},
            body=json.dumps({"question": "How are you?"})
        )
        body = response.json_body

        assert "question" in body
        assert "assistant" in body
        assert body["assistant"] == agent_message


def test_no_chats():
    assert db.session.query(func.count(Chat.id)).scalar() == 0
