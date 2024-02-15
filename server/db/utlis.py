from sqlalchemy import select
from sqlalchemy.orm import exc

from db import db
from db.models import Org


def get_or_create(org_name: str) -> Org:
    try:
        org = db.session.execute(select(Org).where(Org.name == org_name)).scalar_one()
    except exc.NoResultFound:
        org = Org(name=org_name)
        db.session.add(org)
    return org
