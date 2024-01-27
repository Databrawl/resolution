import json

from chalice.test import Client

from app import app
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
