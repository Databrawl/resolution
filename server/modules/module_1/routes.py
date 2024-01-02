from chalice import Blueprint
from structlog import get_logger

from modules.api_key.repository.api_keys import ApiKeys

logger = get_logger(__name__)

bp = Blueprint(__name__)

api_keys_repository = ApiKeys()


@bp.route('/hello', methods=['GET'])
def hello():
    return {"hello": "world"}


@bp.route('/hello/{name}', methods=['GET'])
def hello_uid(name):
    return {"hello": name}
