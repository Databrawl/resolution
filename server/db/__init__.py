from functools import wraps

from db.database import Database
from settings import app_settings

db = Database(app_settings.DATABASE_URI)


def transactional(f):
    @wraps(f)
    def wrapper(*args, **kwds):
        with db.session:
            return f(*args, **kwds)

    return wrapper
