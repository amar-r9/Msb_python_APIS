from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.services.auth import get_current_user
from app.services.user import create_user_by_data, get_user_by_id, get_all_users, get_all_users_paginated
from app.models.user import User, UserResponse, UserCreate

router = APIRouter()

@router.get("/get-user")
def get_user(id: str, db: Session = Depends(get_db),current_user: User = Depends(get_current_user)):
    user = get_user_by_id(id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/create-user", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db),current_user: User = Depends(get_current_user)):
    new_user = create_user_by_data(db, user)
    return new_user




@router.get("/get-users")
def get_users(
    page: int = Query(1, ge=1, description="Page number (starts from 1)"),
    limit: int = Query(10, ge=1, le=100, description="Number of users per page (max 100)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    users, total = get_all_users_paginated(db, page, limit)
    return {
        "page": page,
        "limit": limit,
        "total": total,
        "total_pages": (total // limit) + (1 if total % limit > 0 else 0),
        "current_user": current_user,
        "users": users
    }