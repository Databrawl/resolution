from flask import Flask
from flask_cors import CORS
from structlog import get_logger

from db import db
from settings import app_settings
from views import api


def create_app():
    _app = Flask("REsolution API")
    _app.config.update(app_settings.__dict__)
    _app.register_blueprint(api)
    db.init_app(_app)
    CORS(_app)
    return _app


app = create_app()
logger = get_logger(__name__)
