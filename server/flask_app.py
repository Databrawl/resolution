import supabase
from flask import Flask, request, abort
from flask_cors import CORS
from gotrue.errors import AuthApiError
from sqlalchemy import select
from structlog import get_logger
from supabase import create_client

import memory
from bots.team import call_manager
from db import db
from db.models import User, Chat, Org, Onboarding, OrgUser
from settings import app_settings


def create_app():
    _app = Flask("REsolution API")
    _app.config.update(app_settings.__dict__)
    db.init_app(_app)
    CORS(_app)
    return _app


app = create_app()
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
    User.current.set(User.get(user_response.user.id))


@app.route('/chats', methods=['POST'])
def create_chat():
    body = request.json
    chat = _create_chat(body)
    return {
        "chat_id": str(chat.id),
        "user_id": str(User.current.get().id),
        "creation_time": chat.created_at.strftime('%Y-%m-%dT%H:%M:%SZ'),
        "chat_name": body["name"],
    }


def _create_chat(body):
    chat = Chat(
        user=User.current.get(),
        active=True,
        name=body["name"]
    )
    chat.save()
    return chat


@app.route('/messages', methods=['POST'])
def add_message():
    query = (
        select(Org)
        .join(OrgUser, OrgUser.org_id == Org.id)
        .where(OrgUser.user_id == User.current.get().id)
    )
    org = db.session.execute(query).scalar_one_or_none()
    Org.current.set(org)

    chat_memory = memory.load(request.json["chat_id"])

    manager = call_manager(chat_memory)
    user_message = request.json["user_message"]
    team_response = manager.run(user_message)

    memory.save(request.json["chat_id"], user_message, team_response)

    logger.info(f"User message: {user_message} \n Support team response: {team_response}")

    response = request.json.copy()
    response["assistant"] = team_response
    return response


@app.route('/onboarding', methods=['GET'])
def onboarding():
    query = (
        select(Onboarding)
        .join(OrgUser, OrgUser.org_id == Onboarding.org_id)
        .where(OrgUser.user_id == User.current.get().id)
    )
    onboarding_data = db.session.execute(query).scalar_one_or_none()
    return {
        "greeting": onboarding_data.greeting if onboarding_data else "",
        "onboarding_b1": onboarding_data.quick_1 if onboarding_data else "",
        "onboarding_b2": onboarding_data.quick_2 if onboarding_data else "",
        "onboarding_b3": onboarding_data.quick_3 if onboarding_data else ""
    }


@app.route('/chats', methods=['GET'])
def chats():
    return [{"chat_id": "1", "chat_name": "chat1"}]


@app.route('/brains', methods=['GET'])
def brains():
    return [{"name": "default"}]


@app.route('/brains/default', methods=['GET'])
def brains_default():
    return {"name": "default", "description": "Default brain", "version": "1.0.0"}

@app.route('/prompts', methods=['GET'])
def prompts():
    return [{"name": "default"}]
