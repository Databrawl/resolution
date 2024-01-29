from chalice import Blueprint
from sqlalchemy import select
from sqlalchemy.orm import exc
from structlog import get_logger

from bots.agent_5 import get_agent
from db import db
from db.models import User, Chat, Org
from db.tests.factories import OrgFactory

logger = get_logger(__name__)
bp = Blueprint(__name__)


@bp.route('/chats', methods=['POST'])
def create_chat():
    body = bp.current_request.json_body
    # TODO: retrieve user from the request
    chat, user = _create_chat(body)
    return {
        "chat_id": str(chat.id),
        "user_id": str(user.id),
        "creation_time": chat.created_at.strftime('%Y-%m-%dT%H:%M:%SZ'),
        "chat_name": body["name"],
    }


@db.transactional
def _create_chat(body):
    user = db.session.query(User).first()
    chat = Chat(
        user=user,
        active=True,
        name=body["name"]
    )
    db.session.add(chat)
    return chat, user


@bp.route('/messages', methods=['POST'])
def add_message():
    body = bp.current_request.json_body

    return _add_message(body)


@db.transactional
def _add_message(data: dict):
    org = "cryptocom"
    user_message = data["user_message"]
    try:
        org = db.session.execute(select(Org).where(Org.name == org)).scalar_one()
    except exc.NoResultFound:
        org = OrgFactory.create(name=org)
    Org.current.set(org)
    agent = get_agent()
    agent_response = agent.run(user_message)
    logger.info(f"User message: {user_message} \n Agent response: {agent_response}")
    response = data
    response["assistant"] = agent_response
    return response
