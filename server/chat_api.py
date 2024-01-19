from chalice import Blueprint
from structlog import get_logger

from db import transactional, session
from db.models import User, Chat

logger = get_logger(__name__)
bp = Blueprint(__name__)


@bp.route('/chats', methods=['POST'])
@transactional
def create_chat():
    body = bp.current_request.json_body
    # TODO: retrieve user from the request
    user = session.query(User).first()
    chat = Chat(
        user=user,
        active=True,
        name=body["name"]
    )
    session.add(chat)
    return {
        "chat_id": chat.id,
        "user_id": user.id,
        "creation_time": chat.created_at,
        "chat_name": body["name"],
    }


@bp.route('/messages', methods=['POST'])
@transactional
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

    # return {"chat_id": body["chat_id"],
    #         "message_id": body["message_id"],
    #         "user_message": body["question"],
    #         "assistant": "Hello, how can I help you?"}
    # return {"assistant": "Hello, how can I help you?"}
