import uuid
from typing import Optional
import os
from PIL import Image
from fastapi import APIRouter, Depends, HTTPException, Form, File, UploadFile, Query
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, joinedload

from app.config.settings import settings
from app.database.connection import get_db
from app.models import Category, SubCategory, UserPoint
from app.models.submission import Submission
from app.models.user import User
from app.routes.pre_auth_routes import get_user_student
from app.services.auth import get_current_user
from app.services.category import get_category_from_id
from app.services.school_service import update_rank_by_school_id,  \
    update_points_to_student_by_user_id
from app.services.submissions_service import get_by_school, get_by_user, get_by_sub_category, \
    get_by_school_with_grade, get_all_category, get_comments_by_submission_id, formart_submission
from app.services.user import get_user_by_email
from app.utils.common import BASE_URL, SUBMISSIONS_MEDIA_FOLDER, USER_PROFILES_MEDIA_FOLDER

router = APIRouter()

# Define the base URL for media files
UPLOAD_DIR = "static/media/submissions/"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Max file size limits in bytes
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5 MB
MAX_VIDEO_SIZE = 50 * 1024 * 1024  # 50 MB
MAX_AUDIO_SIZE = 10 * 1024 * 1024  # 10 MB


@router.post("/create")
async def create_submission(
        category_id: int = Form(...),
        sub_category_id: int = Form(...),
        title: str = Form(...),
        description: str = Form(...),
        media_file: Optional[UploadFile] = File(None),
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    category = get_category_from_id(category_id)

    # Fetch the logged-in user from the database
    user = get_user_by_email(db, current_user.get('email'))

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Fetch the student profile associated with the user
    student = get_user_student(db, user.id)

    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")

    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    category_type = category.category_type.name  # Extract category type (image, video, etc.)

    if media_file:
        # Read file size
        media_file.file.seek(0, os.SEEK_END)
        file_size = media_file.file.tell()
        media_file.file.seek(0)  # Reset file pointer for further processing

    # Category type validation
    if category_type == "image":
        if media_file is None:
            raise HTTPException(status_code=400, detail="Image file is required for this category")
        if media_file.content_type not in ["image/jpeg", "image/png", "image/jpg"]:
            raise HTTPException(status_code=400,
                                detail="Invalid file type for image category. Only jpg, png are allowed.")
        if file_size > MAX_IMAGE_SIZE:
            raise HTTPException(status_code=400, detail="Image file exceeds the maximum size limit of 5MB.")
    elif category_type == "video":
        if media_file is None:
            raise HTTPException(status_code=400, detail="Video file is required for this category")
        if media_file.content_type not in ["video/mp4", "video/quicktime"]:
            raise HTTPException(status_code=400,
                                detail="Invalid file type for video category. Only mp4, quicktime are allowed.")
        if file_size > MAX_VIDEO_SIZE:
            raise HTTPException(status_code=400, detail="Video file exceeds the maximum size limit of 50MB.")
    elif category_type == "audio":
        if media_file is None:
            raise HTTPException(status_code=400, detail="Audio file is required for this category")
        if media_file.content_type not in ["audio/mpeg", "audio/wav"]:
            raise HTTPException(status_code=400,
                                detail="Invalid file type for audio category. Only mp3, wav are allowed.")
        if file_size > MAX_AUDIO_SIZE:
            raise HTTPException(status_code=400, detail="Audio file exceeds the maximum size limit of 10MB.")
    elif category_type == "text":
        media_file = None
    elif category_type == "quiz":
        raise HTTPException(status_code=400, detail="File uploads are not allowed for quiz category.")

    # Prepare the media filename and directory
    media_filename = None
    if media_file:
        category_folder = "images" if category_type == "image" else "videos" if category_type == "video" else "audios"
        category_folder_path = os.path.join(UPLOAD_DIR, category_folder)
        os.makedirs(category_folder_path, exist_ok=True)

        file_extension = media_file.filename.split('.')[-1]
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        file_path = os.path.join(category_folder_path, unique_filename)
        # return unique_filename
        # Save the file
        content = await media_file.read()
        with open(file_path, "wb") as f:
            f.write(content)

        # Validate image file
        if category_type == "image":
            try:
                img = Image.open(file_path)
                img.load()
            except Exception:
                os.remove(file_path)
                raise HTTPException(status_code=400, detail="Uploaded file is not a valid image")

        media_filename = unique_filename

    # Get the user ID of the current user
    created_by = user.id

    # return media_filename

    # Start DB transaction
    try:
        # Create the submission
        new_submission = Submission(
            created_by=created_by,
            category_id=category_id,
            sub_category_id=sub_category_id,
            title=title,
            description=description,
            grade_id=student.grade_id,
            school_id=student.school_id,
            media=media_filename,
        )

        db.add(new_submission)
        db.flush()
        # db.refresh(new_submission)

        new_submission.media_url = new_submission.media_path

        # # Update the media path if a file was uploaded
        # if new_submission.media:
        #     category_folder = "images" if category_type == "image" else "videos" if category_type == "video" else "audios"
        #     new_submission.media_url = f"{SUBMISSIONS_MEDIA_FOLDER}{category_folder}/{new_submission.media}"
        # else:
        #     new_submission.media_url = None

        # Add points to the user
        user_point = UserPoint(
            user_id=new_submission.created_by,
            grade_id=new_submission.grade_id,  # Add 30 points for each submission
            school_id=new_submission.school_id,  # Add 30 points for each submission
            submission_id=new_submission.id,  # Add 30 points for each submission
            points=settings.POINTS_BY_SUBMISSION,  # Add 30 points for each submission
            point_type=1  # Assuming 1 represents the point type for submission
        )

        db.add(user_point)
        db.flush()


        db.commit()



        update_rank_by_school_id(student.school_id)

        update_points_to_student_by_user_id(user.id)

        db.refresh(new_submission)

        return {"message": "Submission created successfully", "submission": new_submission}

    except SQLAlchemyError as e:
        db.rollback()
        print(e)
        raise HTTPException(status_code=500, detail="Error creating submission or adding points.")


@router.post("/all")
async def get_submissions_by_sub_category(
        page: int = Query(1, ge=1, description="Page number (starts from 1)"),
        limit: int = Query(10, ge=1, le=100, description="Number of users per page (max 100)"),
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        category_id: Optional[int] = None,
        sub_category_id: Optional[int] = None,
        submission_id: Optional[int] = None,
        user_id: Optional[int] = None,
        school_id: Optional[int] = None,
        grade_id: Optional[int] = None,
):
    user = get_user_by_email(db, current_user.get('email'))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    submissions, total = get_all_category(page, limit, user, category_id,sub_category_id, submission_id, user_id, school_id, grade_id)
    return {
        "page": page,
        "limit": limit,
        "total": total,
        "total_pages": (total // limit) + (1 if total % limit > 0 else 0),
        "data": submissions
    }
#
# @router.get("/by_sub_category/{sub_category_id}")
# async def get_submissions_by_sub_category(
#         sub_category_id: int,
#         page: int = Query(1, ge=1, description="Page number (starts from 1)"),
#         limit: int = Query(10, ge=1, le=100, description="Number of users per page (max 100)"),
#         db: Session = Depends(get_db),
#         current_user: User = Depends(get_current_user),
# ):
#         # .filter(Submission.sub_category_id == sub_category_id)
#
#         # Fetch the logged-in user from the database
#     user = get_user_by_email(db, current_user.get('email'))
#
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")
#
#     submissions, total = get_by_sub_category(sub_category_id, page, limit, user)
#     return {
#         "page": page,
#         "limit": limit,
#         "total": total,
#         "total_pages": (total // limit) + (1 if total % limit > 0 else 0),
#         "data": submissions
#     }
#
#
@router.get("/by_id/{submission_id}")
async def get_submissions_by_id(
        submission_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
        # .filter(Submission.sub_category_id == sub_category_id)

        # Fetch the logged-in user from the database
    user = get_user_by_email(db, current_user.get('email'))

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    submission = (
        db.query(Submission)
        .filter(Submission.id == submission_id)
        .join(User, Submission.created_by == User.id)  # Assuming `Submission.created_by` links to `User.id`
        .join(Category,
              Submission.category_id == Category.id)  # Assuming `Submission.category_id` links to `Category.id`
        .join(SubCategory,
              Submission.sub_category_id == SubCategory.id)  # Assuming `Submission.sub_category_id` links to `SubCategory.id`
        .options(
            joinedload(Submission.user),  # Load user relationship
            joinedload(Submission.category),  # Load category relationship
            joinedload(Submission.subcategory),  # Load sub_category relationship
            joinedload(Submission.user).defer(User.password),
            joinedload(Submission.user).joinedload(User.students),
        )
        .first()
    )

    formatted_submission = formart_submission(submission, user)

    return {
            "submission": formatted_submission,
        }
#
#
#
# @router.get("/by_user/{user_id}")
# async def get_submissions_by_user(
#         user_id: int,
#         page: int = Query(1, ge=1, description="Page number (starts from 1)"),
#         limit: int = Query(10, ge=1, le=100, description="Number of users per page (max 100)"),
#         db: Session = Depends(get_db),
#         current_user: User = Depends(get_current_user),
# ):
#
#         # Fetch the logged-in user from the database
#     user = get_user_by_email(db, current_user.get('email'))
#
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")
#
#     submissions, total = get_by_user(user_id, page, limit, user)
#     return {
#         "page": page,
#         "limit": limit,
#         "total": total,
#         "total_pages": (total // limit) + (1 if total % limit > 0 else 0),
#         "data": submissions
#     }
#
#
#
#
#
# @router.get("/by_school/{school_id}")
# async def get_submissions_by_school(
#         school_id: int,
#         page: int = Query(1, ge=1, description="Page number (starts from 1)"),
#         limit: int = Query(10, ge=1, le=100, description="Number of users per page (max 100)"),
#         db: Session = Depends(get_db),
#         current_user: User = Depends(get_current_user),
# ):
#
#         # Fetch the logged-in user from the database
#     user = get_user_by_email(db, current_user.get('email'))
#
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")
#
#     submissions, total = get_by_school(school_id, page, limit, user)
#     return {
#         "page": page,
#         "limit": limit,
#         "total": total,
#         "total_pages": (total // limit) + (1 if total % limit > 0 else 0),
#         "data": submissions
#     }
#
# @router.get("/by_school_with_grade/{school_id}/{grade_id}")
# async def get_submissions_by_school(
#         school_id: int,
#         grade_id: int,
#         page: int = Query(1, ge=1, description="Page number (starts from 1)"),
#         limit: int = Query(10, ge=1, le=100, description="Number of users per page (max 100)"),
#         db: Session = Depends(get_db),
#         current_user: User = Depends(get_current_user),
# ):
#
#         # Fetch the logged-in user from the database
#     user = get_user_by_email(db, current_user.get('email'))
#
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")
#
#     submissions, total = get_by_school_with_grade(school_id, grade_id, page, limit, user)
#     return {
#         "page": page,
#         "limit": limit,
#         "total": total,
#         "total_pages": (total // limit) + (1 if total % limit > 0 else 0),
#         "data": submissions
#     }


@router.get("/comments/{submission_id}")
async def get_comment_by_submission_id(
        submission_id: int,
        page: int = Query(1, ge=1, description="Page number (starts from 1)"),
        limit: int = Query(10, ge=1, le=100, description="Number of users per page (max 100)"),
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
        # Fetch the logged-in user from the database
    user = get_user_by_email(db, current_user.get('email'))

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    comments, total = get_comments_by_submission_id(submission_id, page, limit)
    return {
        "page": page,
        "limit": limit,
        "total": total,
        "total_pages": (total // limit) + (1 if total % limit > 0 else 0),
        "data": comments
    }