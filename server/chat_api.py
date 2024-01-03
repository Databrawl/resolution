from chalice import Blueprint
from structlog import get_logger

from bots.agent_5 import get_agent

logger = get_logger(__name__)

bp = Blueprint(__name__)


@bp.route('/send', methods=['POST'])
def send():
    body = bp.current_request.json_body
    agent = get_agent()
    response = agent.run(body["user_input"])

    return {"response": response}
