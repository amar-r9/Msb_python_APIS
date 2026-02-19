from datetime import datetime
from typing import Type

from sqlalchemy import desc
from sqlalchemy.orm import Session, joinedload

from app.database.connection import get_db
from app.models import Submission
from app.models.category import CategoryCreate, Category, CategoryResponse
from app.models.model_comments import Comment
from app.models.model_likes import Like
from app.models.subcategory import SubCategory
from app.models.student import Student, StudentCreate
from app.models.user import User
from app.routes.pre_auth_routes import get_user_student
from app.utils.common import hash_password, BASE_URL, CATEGORY_MEDIA_FOLDER
from fastapi import APIRouter, Depends, HTTPException, status, Request


from sqlalchemy.orm import Session
from fastapi import HTTPException

def make_comment(user: User, submission_id: int, comment:str, parent_id:int=None):
    db: Session = next(get_db())

    try:

        # Fetch the student profile associated with the user
        student = get_user_student(db, user.id)
        if not student:
            raise HTTPException(status_code=404, detail="Student profile not found")

        # Add a new like
        comment_item = Comment(
            user_id=user.id,
            school_id=student.school_id,
            submission_id=submission_id,
            comment=comment,
            parent_id=parent_id,
            created_at=datetime.now(),
        )
        db.add(comment_item)
        db.commit()
        db.refresh(comment_item)
        return {
            'status': 'success',
            'comment': comment_item,
        }

    except Exception as e:
        db.rollback()
        raise e

    finally:
        db.close()


def remove_comment(user: User, submission_id: int, comment_id:int):
    db: Session = next(get_db())

    try:


        # Check if the like already exists
        existing_comment = (
            db.query(Comment)
            .filter(Comment.user_id == user.id, Comment.submission_id == submission_id and Comment.id == comment_id)
            .first()
        )

        if existing_comment:
            # Remove the like
            db.delete(existing_comment)
            db.commit()

        return {
            'status': 'success',
            'comment': '',
        }

    except Exception as e:
        db.rollback()
        raise e

    finally:
        db.close()

