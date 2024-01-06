from functools import wraps

from db.database import Database
from settings import app_settings

db = Database(app_settings.DATABASE_URI)


from sqlalchemy import create_engine
from sqlalchemy.orm import Session

# an Engine, which the Session will use for connection
# resources
engine = create_engine("postgresql://postgres:postgres@localhost:54322/postgres")

# create session and add objects
session = Session(engine)


def transactional(f):
    @wraps(f)
    def wrapper(*args, **kwds):
        # with db.session as session, session.begin():
        with session.begin():
            return f(*args, **kwds)

    return wrapper
