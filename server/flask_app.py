import supabase
from flask import Flask, request, abort
from flask import g
from flask_cors import CORS
from gotrue.errors import AuthApiError
from sqlalchemy import select
from structlog import get_logger
from supabase import create_client

import memory
from bots.team import call_manager
from db import db
from db.models import User, Chat, Org, Onboarding, OrgUser
from db.utlis import get_or_create
from settings import app_settings

app = Flask(__name__)
CORS(app)

logger = get_logger(__name__)


@app.before_request
def before_request():
    if request.method == "OPTIONS":
        return
    jwt = request.headers.get('Authorization')
    if not jwt:
        abort(401)
    jwt = jwt.split()[1]
    supabase_client: supabase.Client = create_client(
        app_settings.SUPABASE_URL,
        app_settings.SUPABASE_KEY,
    )
    try:
        user_response = supabase_client.auth.get_user(jwt)
    except AuthApiError:
        abort(401)
    g.user_id = user_response["user"]["id"]


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


@app.route('/chats', methods=['POST'])
def create_chat():
    body = request.json_body
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


@app.route('/messages', methods=['POST'])
def add_message():
    body = app.current_request.json_body
    return _add_message(body)


@db.transactional
def _add_message(data: dict):
    org_name = "cryptocom"
    user_message = data["user_message"]

    org = get_or_create(org_name)
    Org.current.set(org)

    chat_memory = memory.load(data["chat_id"])

    manager = call_manager(chat_memory)
    team_response = manager.run(user_message)

    memory.save(data["chat_id"], user_message, team_response)

    logger.info(f"User message: {user_message} \n Support team response: {team_response}")

    response = data
    response["assistant"] = team_response
    return response


@app.route('/chats', methods=['GET'])
def chats():
    return [{"chat_id": "1", "chat_name": "chat1"}]


@app.route('/brains', methods=['GET'])
def brains():
    return [{"name": "default"}]


@app.route('/brains/default', methods=['GET'])
def brains_default():
    return {"name": "default", "description": "Default brain", "version": "1.0.0"}


@app.route('/onboarding', methods=['GET'])
@db.transactional
def onboarding():
    query = (
        select(Onboarding)
        .join(OrgUser, OrgUser.org_id == Onboarding.org_id)
        .where(OrgUser.user_id == g.user_id)
    )
    onboarding_data = db.session.execute(query).scalar_one_or_none()
    return {
        "greeting": onboarding_data.greeting if onboarding_data else "",
        "onboarding_b1": onboarding_data.quick_1 if onboarding_data else "",
        "onboarding_b2": onboarding_data.quick_2 if onboarding_data else "",
        "onboarding_b3": onboarding_data.quick_3 if onboarding_data else "",
    }

@app.route('/prompts', methods=['GET'])
def prompts():
    return [{"name": "default"}]
