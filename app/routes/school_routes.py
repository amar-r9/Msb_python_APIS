import uuid
from typing import Optional
import os
from PIL import Image
from fastapi import APIRouter, Depends, HTTPException, Form, File, UploadFile, Query
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, joinedload

from app.database.connection import get_db
from app.models.user import User
from app.services.auth import get_current_user
from app.services.masters import get_all_schools
from app.services.school_service import get_school_dashbaord, get_school_top_schools
from app.services.user import get_user_by_email

router = APIRouter()

# Define the base URL for media files
UPLOAD_DIR = "static/media/submissions/"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Max file size limits in bytes
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5 MB
MAX_VIDEO_SIZE = 50 * 1024 * 1024  # 50 MB
MAX_AUDIO_SIZE = 10 * 1024 * 1024  # 10 MB



@router.get("/dashboard/{school_id}")
async def get_dashboard_dashboard(
        school_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    # Fetch the logged-in user from the database
    # user = db.query(User).filter(User.email == current_user.get('email')).first()
    user = get_user_by_email(db, current_user.get('email'))

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        # .filter(Submission.sub_category_id == sub_category_id)

    # return user.id

    dashboard = get_school_dashbaord(user, school_id)
    return {
        "dashboard": dashboard
    }




@router.get("/all")
async def get_dashboard_dashboard(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    schools = get_all_schools(db)
    return schools


@router.get("/top")
async def get_dashboard_dashboard(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    # Fetch the logged-in user from the database
    user = get_user_by_email(db, current_user.get('email'))

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        # .filter(Submission.sub_category_id == sub_category_id)

    return get_school_top_schools(user)