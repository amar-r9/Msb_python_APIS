from fastapi import Depends
from passlib.context import CryptContext

from app.models.token import TokenData
from app.services.user import get_user_by_email, get_user_by_user_name

from sqlalchemy.orm import Session
from app.database.connection import get_db
from fastapi.security import OAuth2PasswordBearer
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.config.settings import settings
from jose import JWTError, jwt
from fastapi import APIRouter, Depends, HTTPException, status, Request

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


# Dependency to get the current user
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user_by_user_name(db, token_data.username)
    if user is None:
        raise credentials_exception
    return user



