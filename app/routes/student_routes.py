from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.student import StudentCreate, StudentResponse
from app.services.auth import get_current_user
from app.services.student import create_student_by_data, get_student_by_id, get_all_students_paginated, \
    get_students_by_school
from app.services.user import get_user_by_id, get_all_users, get_all_users_paginated
from app.models.user import User

router = APIRouter()

# @router.get("/get-student", response_model=StudentResponse)
# def get_student(id: str, db: Session = Depends(get_db),current_user: User = Depends(get_current_user)):
#     student = get_student_by_id(db, id)
#     if not student:
#         raise HTTPException(status_code=404, detail="Student not found")
#     return student
#
#
# @router.post("/create-student", response_model=StudentResponse)
# def create_user(student: StudentCreate, db: Session = Depends(get_db),current_user: User = Depends(get_current_user)):
#     new_student = create_student_by_data(db, student)
#     return new_student




@router.get("/get-students")
def get_students(
    page: int = Query(1, ge=1, description="Page number (starts from 1)"),
    limit: int = Query(10, ge=1, le=100, description="Number of users per page (max 100)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    users, total = get_all_students_paginated(page, limit)
    return {
        "page": page,
        "limit": limit,
        "total": total,
        "total_pages": (total // limit) + (1 if total % limit > 0 else 0),
        "users": users
    }

@router.get("/get-students-by_school/{school_id}")
def get_students(
    school_id: int,
    page: int = Query(1, ge=1, description="Page number (starts from 1)"),
    limit: int = Query(10, ge=1, le=100, description="Number of users per page (max 100)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    users, total = get_students_by_school(school_id, page, limit)
    return {
        "page": page,
        "limit": limit,
        "total": total,
        "total_pages": (total // limit) + (1 if total % limit > 0 else 0),
        "users": users
    }



