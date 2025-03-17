import os
from typing import Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status, Request, Form, File, UploadFile, Query
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload, defer

from app.database.connection import get_db
from app.models import Student, Grade, Submission, Category, SubCategory, Like, Comment, School
from app.models.user import User, UserResponse, LoginRequest, RegisterStudentRequest, TokenStudentResponse
from app.auth import verify_password, create_access_token
from app.models.token import Token  # Correct import for the Token model
from app.routes.pre_auth_routes import get_user_student
from app.services.auth import get_current_user
from app.services.comment_service import make_comment, remove_comment
from app.services.like_service import toggle_like
from app.services.masters import get_all_schools, get_all_schools_count
from app.services.category import get_future_categories
from app.services.student import register_student_by_data, get_all_students_count, get_top_score_students
from app.services.submissions_service import get_auth_school, get_submission_by_auth, get_auth_school_and_grade
from app.services.user import get_user_by_email, get_user_by_id, get_user_submission_comments_count, \
    get_user_submission_like_count

from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer

from app.utils.common import hash_password, BASE_URL, USER_PROFILES_MEDIA_FOLDER


UPLOAD_USER_PROFILES_DIR = "static/media/user_profile_images/"
os.makedirs(UPLOAD_USER_PROFILES_DIR, exist_ok=True)
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5 MB
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png"}  # Allowed MIME types

from PIL import Image  # For validating image files



router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")



@router.get("/me")
def read_users_me(request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    print(request.headers)  # Log all headers for debugging

    user = get_user_by_email(db, current_user.get('email'))


    comments_count = get_user_submission_comments_count(user.id)
    like_count = get_user_submission_like_count(user.id)

    if user.role_id == 2:  # Access `role_id` as a key in a dictionary
        student = get_user_student(db, user.id)

        points = student.points
        likes = student.likes
        score = student.score
    else:
        student = {}
        points = 0
        likes = 0
        score = 0


    return {
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role_id": user.role_id,
            "role_name": user.role.name,
            "image_url": user.image_url,
            "points": points,
            "likes": likes,
            "score": score,
        },
        'student': student,
        'comments_count': comments_count,
        # 'like_count': like_count,
    }






@router.get("/student/dashboard")
def read_users_me(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):

    user = get_user_by_email(db, current_user.get('email'))

    if user.role_id == 2:  # Access `role_id` as a key in a dictionary
        schools_count = get_all_schools_count(db)
        students_count = get_all_students_count(db)
        students_top_score = get_top_score_students(db)
        future_categories = get_future_categories(db)
        return {
            "total_schools": schools_count,
            'total_student': students_count,
            'top_score_students': students_top_score,
            'future_categories': future_categories,
        }
    else:
        return {}



@router.post("/logout")
def logout(token: str = Depends(oauth2_scheme)):
    # Invalidate the token on the client side (for example, by removing it from localStorage/cookies)
    # For now, we'll just return a response indicating successful logout.
    return {
        'token': token,
        "message": "Successfully logged out. Please remove the token from client-side storage."
    }


@router.put("/me/update-profile")
async def update_profile(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    name: str = Form(...),
    grade_id: int = Form(...),
    profile_image: Optional[UploadFile] = File(None),
    school_id: Optional[int] = None,
    school_name: Optional[str] = None
):
    print(request.headers)  # Debugging headers

    # Fetch the logged-in user from the database
    user = get_user_by_email(db, current_user.get('email'))

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Fetch the student profile associated with the user
    student = get_user_student(db, user.id)

    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")

    # Check if grade exists
    grade = db.query(Grade).filter(Grade.id == grade_id).first()
    if not grade:
        raise HTTPException(status_code=404, detail="Grade not found")

    try:
        # Validate and save the image if a new image is provided
        if profile_image:
            # If the user already has an image, delete the old one
            if user.image:
                old_file_path = os.path.join(UPLOAD_USER_PROFILES_DIR, user.image)
                if os.path.exists(old_file_path):
                    os.remove(old_file_path)

            # Validate file type
            if profile_image.content_type not in ALLOWED_IMAGE_TYPES:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid image type. Allowed types: {', '.join(ALLOWED_IMAGE_TYPES)}",
                )

            # Generate a custom file name
            file_extension = profile_image.filename.split(".")[-1]
            custom_file_name = f"{uuid4().hex}.{file_extension}"
            file_path = os.path.join(UPLOAD_USER_PROFILES_DIR, custom_file_name)

            # Save the image to the upload directory
            with open(file_path, "wb") as buffer:
                buffer.write(await profile_image.read())

            # Optionally validate the image file using PIL
            try:
                Image.open(file_path).verify()
            except Exception:
                os.remove(file_path)  # Remove invalid file
                raise HTTPException(status_code=400, detail="Uploaded file is not a valid image")

            # Update user profile with image path
            user.image = custom_file_name

        # Update user profile with name and grade
        user.name = name

        # Update student's grade_id
        student.grade_id = grade_id

        if school_id:
            student.school_id = school_id

        if school_name:
            new_school = School(
                name=school_name,  # Fixed school_name reference
                created_by=user.id,
            )
            db.add(new_school)
            db.flush()
            student.school_id = new_school.id

        db.add(user)
        db.add(student)
        db.commit()
        db.refresh(user)
        db.refresh(student)

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

    if user.image:
        user.image = f"{USER_PROFILES_MEDIA_FOLDER}{user.image}"

    return {
        "message": "Profile updated successfully",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "image": user.image,
        },
        "student": student,
    }



@router.put("/me/update-password")
def update_password(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    old_password: str = Form(...),
    new_password: str = Form(...),
):
    print(request.headers)  # Debugging headers

    # Fetch the logged-in user from the database
    user = get_user_by_email(db, current_user.get('email'))

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Verify the old password
    if not verify_password(old_password, user.password):  # Assuming `verify_password` checks hashed passwords
        raise HTTPException(status_code=400, detail="Old password is incorrect")

    # Hash the new password and update
    user.password = hash_password(new_password)  # Assuming `hash_password` hashes the password

    db.add(user)
    db.commit()

    return {"message": "Password updated successfully"}







@router.get("/submissions/my-school-grade")
async def get_submissions_by_school(

        page: int = Query(1, ge=1, description="Page number (starts from 1)"),
        limit: int = Query(10, ge=1, le=100, description="Number of users per page (max 100)"),
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    user = get_user_by_email(db, current_user.get('email'))

    if not user:
        raise HTTPException(status_code=404, detail="User not found")


    submissions, total = get_auth_school_and_grade(user, page, limit)
    return {
        "page": page,
        "limit": limit,
        "total": total,
        "total_pages": (total // limit) + (1 if total % limit > 0 else 0),
        "data": submissions
    }



@router.get("/submissions/my")
async def get_submissions_by_school(

        page: int = Query(1, ge=1, description="Page number (starts from 1)"),
        limit: int = Query(10, ge=1, le=100, description="Number of users per page (max 100)"),
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    user = get_user_by_email(db, current_user.get('email'))

    if not user:
        raise HTTPException(status_code=404, detail="User not found")


    submissions, total = get_submission_by_auth(user, page, limit)
    return {
        "page": page,
        "limit": limit,
        "total": total,
        "total_pages": (total // limit) + (1 if total % limit > 0 else 0),
        "data": submissions
    }


@router.get("/submissions/my-school")
async def get_submissions_by_school(

        page: int = Query(1, ge=1, description="Page number (starts from 1)"),
        limit: int = Query(10, ge=1, le=100, description="Number of users per page (max 100)"),
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    user = get_user_by_email(db, current_user.get('email'))

    if not user:
        raise HTTPException(status_code=404, detail="User not found")


    submissions, total = get_auth_school(user, page, limit)
    return {
        "page": page,
        "limit": limit,
        "total": total,
        "total_pages": (total // limit) + (1 if total % limit > 0 else 0),
        "data": submissions
    }

@router.post("/submissions/like")
async def get_submissions_by_school(
        submission_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    user = get_user_by_email(db, current_user.get('email'))

    if not user:
        raise HTTPException(status_code=404, detail="User not found")


    return toggle_like(user, submission_id)


@router.post("/submissions/comment")
async def get_submissions_by_school(
        submission_id: int,
        comment: str,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    user = get_user_by_email(db, current_user.get('email'))

    if not user:
        raise HTTPException(status_code=404, detail="User not found")


    return make_comment(user,submission_id,comment)

@router.post("/submissions/comment/remove")
async def get_submissions_by_school(
        submission_id: int,
        comment_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    user = get_user_by_email(db, current_user.get('email'))

    if not user:
        raise HTTPException(status_code=404, detail="User not found")


    return remove_comment(user,submission_id,comment_id)