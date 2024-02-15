from chalice import Blueprint
from sqlalchemy import select
from sqlalchemy.orm import exc
from structlog import get_logger

import memory
from bots.team import call_manager
from db import db
from db.models import User, Chat, Org

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
    org_name = "cryptocom"
    user_message = data["user_message"]
    # TODO: replace with get_or_create
    try:
        org = db.session.execute(select(Org).where(Org.name == org_name)).scalar_one()
    except exc.NoResultFound:
        org = Org(name=org_name)
        db.session.add(org)
    Org.current.set(org)
    chat_memory = memory.load(data["chat_id"])
    manager = call_manager(chat_memory)
    team_response = manager.run(user_message)
    memory.save(data["chat_id"], user_message, team_response)
    logger.info(f"User message: {user_message} \n Support team response: {team_response}")
    response = data
    response["assistant"] = team_response
    return response
