from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv()



class Settings(BaseSettings):
    DATABASE_URL: str
    APP_URL: str = 'http://127.0.0.1:8000'
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    APP_NAME: str = "My FastAPI App"
    DEBUG: bool = True
    POINTS_BY_SUBMISSION: int = 30
    POINTS_BY_LIKE: int = 2

    # SMTP Configuration
    SMTP_SERVER: str= "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = "mysuperbrain@ikonostechnologies.com"
    SMTP_PASSWORD :str = "Ikonos@123"
    SENDER_EMAIL :str = "mysuperbrain@ikonostechnologies.com"

    class Config:
        env_file = ".env"

settings = Settings()


