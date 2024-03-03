from chalice import Blueprint
from structlog import get_logger

import memory
from bots.team import call_manager
from db import db
from db.models import User, Chat, Org
from db.utlis import get_or_create

logger = get_logger(__name__)
bp = Blueprint(__name__)


@bp.route('/chats', methods=['POST'], cors=True)
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


@bp.route('/messages', methods=['POST'], cors=True)
def add_message():
    body = bp.current_request.json_body
    return _add_message(body)


saved_messages = {
    "What is Quivr?": "it's a chatbot platform",
    "How to use Quivr?": "you can use it to build chatbots",
    "What is a brain?": "Brain is what's inside your head, dude"
}


@db.transactional
def _add_message(data: dict):
    org_name = "cryptocom"
    user_message = data["user_message"]

    org = get_or_create(org_name)
    Org.current.set(org)

    chat_memory = memory.load(data["chat_id"])

    manager = call_manager(chat_memory)
    if user_message not in saved_messages:
        team_response = manager.run(user_message)
    else:
        # TODO: replace with db access
        # onboarding flow, where we have the answer ready
        team_response = saved_messages[user_message]

    memory.save(data["chat_id"], user_message, team_response)

    logger.info(f"User message: {user_message} \n Support team response: {team_response}")

    response = data
    response["assistant"] = team_response
    return response


@bp.route('/chats', methods=['GET'], cors=True)
def chats():
    return [{"chat_id": "1", "chat_name": "chat1"}]


@bp.route('/brains', methods=['GET'], cors=True)
def brains():
    return [{"name": "default"}]


@bp.route('/brains/default', methods=['GET'], cors=True)
def brains_default():
    return {"name": "default", "description": "Default brain", "version": "1.0.0"}


@bp.route('/onboarding', methods=['GET'], cors=True)
def onboarding():
    return {"name": "onboarding", "description": "Onboarding bot", "version": "1.0.0"}


@bp.route('/prompts', methods=['GET'], cors=True)
def prompts():
    return [{"name": "default"}]
