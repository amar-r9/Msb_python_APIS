from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status, Request, BackgroundTasks
from sqlalchemy.orm import Session, joinedload, defer
from starlette.responses import HTMLResponse
from starlette.templating import Jinja2Templates

from app.config.settings import settings
from app.database.connection import get_db
from app.models import Student
from app.models.user import User, UserResponse, LoginRequest, RegisterStudentRequest, TokenStudentResponse
from app.auth import verify_password, create_access_token
from app.services.student import register_student_by_data
from app.services.user import get_user_by_email, get_user_by_id
from app.utils.common import ForgotPasswordRequest, generate_reset_token, ResetPasswordRequest, hash_password, \
    send_email, generate_verification_token, send_verification_email

router = APIRouter()

templates = Jinja2Templates(directory="templates")

@router.post("/register", )
def register(background_tasks: BackgroundTasks, student: RegisterStudentRequest, db: Session = Depends(get_db)):
    new_student = register_student_by_data(db, student, background_tasks)
    user = new_student.user
    # access_token = create_access_token(data={"sub": user.email})

    new_student.user.image_url = new_student.user.image_path
    return {
        "student": new_student,
        # "access_token": access_token,
        # "token_type": "bearer",
    }


def get_user_student(db: Session, user_id: int):
    user_with_relations_as_student = (
        db.query(Student)
        .options(
            joinedload(Student.school),
            joinedload(Student.grade),
            joinedload(Student.country),
            joinedload(Student.state),

        )
        .filter(Student.user_id == user_id)  # Filter by the current user
        .first()
    )
    return user_with_relations_as_student


@router.post("/login")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = get_user_by_email(db, request.email)

    if not user or not verify_password(request.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not user.is_verified:
        raise HTTPException(status_code=403, detail="User is not verified. Please verify your email before logging in.")

    # Create access token
    access_token = create_access_token(data={"sub": user.email})

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
            "points": points,
            "likes": likes,
            "score": score,
            "profile_url": user.image_path,
            "role_id": user.role_id,
            "role_name": user.role.name,
        },
        'student': student,
        "access_token": access_token,
        "token_type": "bearer",
    }


# Forgot Password API
@router.post("/forgot-password")
async def forgot_password(request: ForgotPasswordRequest, background_tasks: BackgroundTasks,  db: Session = Depends(get_db)):
    email = request.email
    user = get_user_by_email(db, request.email)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Generate reset token
    reset_token = generate_reset_token()

    user.reset_token = reset_token
    user.token_expiry = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    db.add(user)
    db.commit()
    db.refresh(user)
    # user["reset_token"] = reset_token
    # user["token_expiry"] = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    # Construct Reset Password Link
    reset_link = f"{settings.APP_URL}/reset-password?token={reset_token}"

    # Email Content
    subject = "Reset Your MSB Password"

    body = '';

    # Send email in the background
    background_tasks.add_task(send_email, to_email=email, subject=subject, body=body, reset_link=reset_link)

    return {"message": "Password reset link sent to your email"}




@router.post("/resend-verification")
def resend_verification(email: str, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.is_verified:
        raise HTTPException(status_code=400, detail="User is already verified")

    token = generate_verification_token(user.email)
    background_tasks.add_task(send_verification_email, user.email, token)

    return {"message": "Verification email has been resent"}