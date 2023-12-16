from server.db.database import Database
from server.settings import app_settings

db = Database(app_settings.DATABASE_URI)
