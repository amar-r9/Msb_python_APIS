from typing import Type

from sqlalchemy import desc, func, case
from sqlalchemy.orm import Session, joinedload

from app.database.connection import get_db
from app.models import School, Submission, Like, Category, SubCategory
from app.models.student import Student, StudentCreate
from app.models.user import User, RegisterStudentRequest
from app.utils.common import hash_password, BASE_URL, USER_PROFILES_MEDIA_FOLDER, generate_verification_token, \
    send_verification_email
from fastapi import APIRouter, Depends, HTTPException, status, Request
from datetime import datetime, date  # Import datetime for Python's built-in datetime type
from starlette.background import BackgroundTasks



def create_student_by_data(db: Session, student: StudentCreate):
    student_role_id = 2  # Replace with the ID of the student role in your database
    default_password = hash_password("password")  # Replace with your default password

    check_existing = db.query(User).filter(User.email == student.email).first()
    if check_existing:
        raise HTTPException(status_code=400, detail="A user with this email already exists.")

    new_user = User(
        name=student.name,
        email=student.email,
        role_id=student_role_id,
        password=default_password,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    new_student = Student(
        user_id=new_user.id,
        grade_id=student.grade_id,
        school_id=student_role_id,
        country_id=student.country_id,
        state_id=student.state_id,
        dob=student.dob,
    )

    db.add(new_student)
    db.commit()
    db.refresh(new_student)

    return new_student


def register_student_by_data(db: Session, student: RegisterStudentRequest, background_tasks: BackgroundTasks):
    student_role_id = 2
    encrypted_password = hash_password(student.password)  # Encrypt the password

    # Check if the email already exists
    existing_user = db.query(User).filter(User.email == student.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="A user with this email already exists.")

    try:
        # Create a new user
        new_user = User(
            name=student.name,
            email=student.email,
            role_id=student_role_id,
            password=encrypted_password,
        )
        db.add(new_user)
        db.flush()

        # Create or fetch the school
        if not student.school_id:
            if not student.school_name:
                raise HTTPException(status_code=400, detail="School name is required to create a new school.")

            # Create a new school if school_id is not provided
            new_school = School(
                name=student.school_name,
                created_by=new_user.id,
            )
            db.add(new_school)
            db.flush()
        else:
            # Fetch the existing school by ID
            new_school = db.query(School).filter(School.id == student.school_id).first()
            if not new_school:
                raise HTTPException(status_code=404, detail="School with the provided ID does not exist.")

        # Create the student record
        new_student = Student(
            user_id=new_user.id,
            grade_id=student.grade_id,
            school_id=new_school.id,
            country_id=student.country_id,
            state_id=student.state_id,
            dob=student.dob,
            score=0,
            points=0,
            likes=0,
            rank=0,
            city=student.city,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        db.add(new_student)
        db.flush()



        student_with_relations = (
            db.query(Student)
            .options(
                joinedload(Student.user).defer(User.password),
                joinedload(Student.school),
                joinedload(Student.grade),
            )
            .filter(Student.id == new_student.id)
            .first()
        )
        db.commit()

        token = generate_verification_token(new_user.email)
        background_tasks.add_task(send_verification_email, new_user.email, token)
        return student_with_relations
    except Exception as e:
        # Rollback the transaction in case of any failure
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# def get_student_by_email(db: Session, email: str):
#     return db.query(User).filter(User.email == email).first()
#
#
def get_student_by_id(db: Session, student_id: str):
    item = db.query(Student).filter(Student.id == student_id).first()

    if item.user.image:
        item.user.image_url = item.user.image_path

    return item


# # Method to get all users
# def get_all_students(db: Session) -> list[Type[User]]:
#     return db.query(User).all()
# # Method to get all users


def get_all_students_count(db: Session):
    return db.query(Student).count()


def get_top_score_students(db: Session):
    limit = 10
    students = (db.query(Student)
                .options(joinedload(Student.user).defer(User.password))
                .order_by(Student.points.desc())
                .limit(limit).all())

    for item in students:
        if item.user:
            item.user.image_url = item.user.image_path

    return students

def get_top_score_students_by_school(school_id: int, limit: int = 3):
    db: Session = next(get_db())

    students = (db.query(Student)
                .options(joinedload(Student.user).defer(User.password))
                .order_by(Student.points.desc())
                .filter(Student.school_id == school_id)
                .limit(limit).all())

    for item in students:
        if item.user:
            item.user.image_url = item.user.image_path

    return students

def get_top_like_submissions_by_school(school_id: int, user:User, limit: int = 3):
    db: Session = next(get_db())
    from app.services.submissions_service import formart_submission


    # return user

    submissions = (
        db.query(Submission, func.count(Like.id).label("like_count"))
        .outerjoin(Like, Like.submission_id == Submission.id)  # Join with likes
        .options(
            joinedload(Submission.user),
            joinedload(Submission.user).defer(User.password),
            joinedload(Submission.user).joinedload(User.students),
        )
        .filter(Submission.school_id == school_id)
        .group_by(Submission.id)  # Group by submission
        .order_by(func.count(Like.id).desc())  # Order by likes count
        .limit(limit)
        .all()
    )

    # Extract IDs and maintain the original order
    submissions_ids = [submission.id for submission, _ in submissions]
    submissions_order_map = {submission.id: index for index, (submission, _) in enumerate(submissions)}

    # Second query, preserving the order
    query = (
        db.query(Submission)
        .filter(Submission.id.in_(submissions_ids))  # ✅ Use `.in_()` for list filtering
        .join(User, Submission.created_by == User.id)
        .join(Category, Submission.category_id == Category.id)
        .join(SubCategory, Submission.sub_category_id == SubCategory.id)
        .options(
            joinedload(Submission.user),
            joinedload(Submission.category),
            joinedload(Submission.subcategory),
            joinedload(Submission.user).defer(User.password),
            joinedload(Submission.user).joinedload(User.students),
        )
        .order_by(case(*[(Submission.id == sid, index) for sid, index in submissions_order_map.items()]))
    # Maintain like count order
    )

    submissions = query.all()


    formatted_submissions_lists = [formart_submission(submission, user) for submission in submissions]

    return formatted_submissions_lists


def get_all_students_paginated(page: int, limit: int):
    db: Session = next(get_db())
    offset = (page - 1) * limit

    # Apply pagination with OFFSET and LIMIT
    students_query = (db.query(Student).options(
        joinedload(Student.user).options(
            joinedload(User.role)  # Load the related Role
        ).defer(User.password)  # Defer the password column
    )
                      .order_by(desc(Student.id))
                      .offset(offset)
                      .limit(limit))

    students = students_query.all()

    for item in students:
        if item.user and item.user.image:
            item.user.image_url = item.user.image_path

    # Count only the filtered records
    total = db.query(Student).count()

    return students, total


def get_students_by_school(school_id: int, page: int, limit: int):
    db: Session = next(get_db())
    offset = (page - 1) * limit

    # Apply pagination with OFFSET and LIMIT
    students_query = (
        db.query(Student)
        .filter(Student.school_id == school_id)
        .options(
            joinedload(Student.user).options(
                joinedload(User.role)  # Load the related Role
            ).defer(User.password)  # Defer the password column
        )
        .order_by(desc(Student.id))
        .offset(offset)
        .limit(limit)
    )

    students = students_query.all()

    for item in students:
        if item.user and item.user.image:
            item.user.image_url = item.user.image_path

    # Count only the filtered records
    total = db.query(Student).count()

    return students, total
