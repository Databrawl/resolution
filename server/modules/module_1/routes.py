from structlog import get_logger

from modules.api_key.repository.api_keys import ApiKeys

logger = get_logger(__name__)

api_keys_repository = ApiKeys()


def hello():
    return {"hello": "world"}


def hello_uid(name):
    return {"hello": name}
