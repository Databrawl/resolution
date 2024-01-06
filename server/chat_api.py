from chalice import Blueprint
from sqlalchemy import select
from sqlalchemy.orm import exc
from structlog import get_logger

from bots.agent_5 import get_agent
from db import db
from db.models import Org
from db.tests.factories import OrgFactory

logger = get_logger(__name__)
bp = Blueprint(__name__)


@bp.route('/send', methods=['POST'])
def send():
    body = bp.current_request.json_body
    org = body["org"]
    message = body["message"]

    with db.session:
        try:
            org = db.session.execute(select(Org).where(Org.name == org)).scalar_one()
        except exc.NoResultFound:
            org = OrgFactory.create(name=org)
        Org.current.set(org)

    agent = get_agent()
    response = agent.run(message)
    logger.info(f"Message: {message} \n Agent response: {response}", response=response,
                message=message, org=org.name)

    return {"response": response}
