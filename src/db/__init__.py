from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config import settings

engine = create_engine(settings.SUPABASE_DB)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
