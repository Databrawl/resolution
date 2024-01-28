from db.database import Database
from settings import app_settings

db = Database(app_settings.DATABASE_URI)
