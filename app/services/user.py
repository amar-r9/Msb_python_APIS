from typing import Type

from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session, defer

from app.database.connection import get_db
from app.models import Comment, Submission, Like
from app.models.user import User, UserCreate
from app.utils.common import hash_password, BASE_URL, USER_PROFILES_MEDIA_FOLDER


def create_user_by_data(db: Session, user: UserCreate):
    new_user = User(
        name=user.name,
        email=user.email,
        role_id=user.role_id,
        password=hash_password(user.password),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    new_user.image_url = new_user.image_path

    return new_user


def get_user_by_email(db: Session, email: str):
    new_user = db.query(User).filter(User.email == email).first()

    if not new_user:
        raise HTTPException(status_code=404, detail="User not found")

    new_user.image_url = new_user.image_path

    return new_user


def get_user_by_user_name(db: Session, email: str):
    user = db.query(User).options(defer(User.password)).filter(User.email == email).first()

    if user:
        user.image_url = user.image_path
        # Convert result to a dictionary
        return {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role_id": user.role_id,
            "image_url": user.image_url
        }
    return None


def get_user_by_id(user_id: str):
    from app.routes.pre_auth_routes import get_user_student


    db: Session = next(get_db())
    user = db.query(User).filter(User.id == user_id).first()

    user.image_url = user.image_path

    student = get_user_student(db, user.id)

    comments_count = get_user_submission_comments_count(user.id)
    like_count = get_user_submission_like_count(user.id)

    # user.role = user.role
    # user.students = user.students
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role_id": user.role_id,
        "image_url": user.image_url,
        "student": student,
        "role": user.role,
        "submissions_count": len(user.submissions),
        # "user_point_count": len(user.user_point),
        "comments_count": comments_count,
        "likes_count": like_count,
    }



def get_user_submission_comments_count(user_id: int):
    db: Session = next(get_db())
    count = (
        db.query(func.count(Comment.id))
        .join(Submission, Comment.submission_id == Submission.id)
        .filter(Submission.created_by == user_id)
        .scalar()
    )
    return count

def get_user_submission_like_count(user_id: int):
    db: Session = next(get_db())
    count = (
        db.query(func.count(Like.id))
        .join(Submission, Like.submission_id == Submission.id)
        .filter(Submission.created_by == user_id)
        .scalar()
    )
    return count

# Method to get all users
def get_all_users(db: Session) -> list[Type[User]]:
    users = db.query(User).all()
    for item in users:
            item.image_url = item.image_path

    return users


def get_all_users_paginated(db: Session, page: int, limit: int):
    offset = (page - 1) * limit

    # Apply pagination with OFFSET and LIMIT
    users = db.query(User).offset(offset).limit(limit).all()

    for item in users:
            item.image_url = item.image_path

    # Count only the filtered records
    total = db.query(User).offset(offset).limit(limit).count()

    return users, total
