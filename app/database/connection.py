from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config.settings import settings

engine = create_engine(
    settings.DATABASE_URL,
    pool_size=100,  # Increase default pool size
    max_overflow=200,  # Allow more connections if needed
    pool_timeout=600,  # Increase timeout before failure
    pool_recycle=18000,  # Reuse connections to prevent stale ones
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
