from chalice import Blueprint
from structlog import get_logger

from db import db
from db.models import User, Chat

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
@db.transactional
def add_message():
    body = bp.current_request.json_body

    # chat_id = body["chat_id"]
    # org = body["org"]
    # message = body["message"]
    #
    # try:
    #     org = db.session.execute(select(Org).where(Org.name == org)).scalar_one()
    # except exc.NoResultFound:
    #     org = OrgFactory.create(name=org)
    # Org.current.set(org)
    #
    # agent = get_agent()
    # response = agent.run(message)
    # logger.info(f"Message: {message} \n Agent response: {response}", response=response,
    #             message=message, org=org.name)
    response = body
    response["assistant"] = "Hello, how can I help you?"
    return response
