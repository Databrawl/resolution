import json

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


def test_create_message():
    with Client(app) as client:
        response = client.http.post(
            "/messages",
            headers={"Content-Type": "application/json"},
            body=json.dumps({"question": "How are you?"})
        )
        body = response.json_body

        assert "question" in body
        assert "assistant" in body
        assert body["assistant"] == "Hello, how can I help you?"


def test_no_chats():
    assert db.session.query(func.count(Chat.id)).scalar() == 0
