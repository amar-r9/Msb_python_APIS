from typing import Type, Optional

from sqlalchemy.orm import Session, joinedload

from app.database.connection import get_db
from app.models.quiz import QuizCreate, Quiz
from app.models.category import CategoryCreate, Category, CategoryResponse
from app.models.subcategory import SubCategory
from app.models.student import Student, StudentCreate
from app.models.user import User
from app.utils.common import hash_password, BASE_URL, CATEGORY_MEDIA_FOLDER
from fastapi import APIRouter, Depends, HTTPException, status, Request


def create_quiz_by_data(db: Session, item: QuizCreate):
    student_role_id = 2  # Replace with the ID of the student role in your database
    default_password = hash_password("password")  # Replace with your default password

    check_existing = (db.query(Quiz)
                      .filter(Quiz.name == item.name)
                      .filter(Quiz.category_id == item.category_id)
                      .filter(Quiz.sub_category_id == item.sub_category_id)
                      .filter(Quiz.grade_id == item.grade_id)
                      .first())
    if check_existing:
        raise HTTPException(status_code=400, detail="A user with this name already exists.")

    model_item = Quiz(
        name=item.name,
        category_id=item.category_id,
        sub_category_id=item.sub_category_id,
        grade_id=item.grade_id,
    )
    db.add(model_item)
    db.commit()
    db.refresh(model_item)

    return model_item



def get_all_quizes_paginated(
    db: Session,
    category_id: int,
    page: int,
    limit: int,
    sub_category_id: Optional[int] = None,
    grade_id: Optional[int] = None
):
    offset = (page - 1) * limit

    query = db.query(Quiz).filter(Quiz.category_id == category_id)

    if sub_category_id:
        query = query.filter(Quiz.sub_category_id == sub_category_id)

    if grade_id:
        query = query.filter(Quiz.grade_id == grade_id)

    total = query.count()
    quizzes = query.offset(offset).limit(limit).all()

    return quizzes, total

