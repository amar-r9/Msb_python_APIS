from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config.settings import settings
from app.database.connection import Base
from app.models import *  # Import all models from models package

# Create an engine (using SQLite in this example)
from sqlalchemy import String as OriginalString


class StringWithDefaultLength(OriginalString):
    def _init_(self, length=255, *args, **kwargs):
        super()._init_(length, *args, **kwargs)

# Override globally
import sqlalchemy

sqlalchemy.String = StringWithDefaultLength

engine = create_engine(
    settings.DATABASE_URL,
    pool_size=100,  # Increase default pool size
    max_overflow=200,  # Allow more connections if needed
    pool_timeout=600,  # Increase timeout before failure
    pool_recycle=18000,  # Reuse connections to prevent stale ones
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


print("Creating tables for:", Base.metadata.tables.keys())
# Create all tables from all imported models
Base.metadata.create_all(engine)

print("Tables created successfully!")