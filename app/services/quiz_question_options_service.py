from typing import Type, Optional

from sqlalchemy.orm import Session, joinedload

from app.database.connection import get_db
from app.models import QuestionOption
from app.models.question_option import QuestionOptionCreate
from app.models.quiz import QuizCreate, Quiz
from app.models.category import CategoryCreate, Category, CategoryResponse
from app.models.subcategory import SubCategory
from app.models.student import Student, StudentCreate
from app.models.user import User
from app.utils.common import hash_password, BASE_URL, CATEGORY_MEDIA_FOLDER
from fastapi import APIRouter, Depends, HTTPException, status, Request


def create_quiz_question_options_by_data(db: Session, item: QuestionOptionCreate):
    student_role_id = 2  # Replace with the ID of the student role in your database
    default_password = hash_password("password")  # Replace with your default password

    check_existing = (db.query(QuestionOption)
                      .filter(QuestionOption.name == item.name)
                      .filter(QuestionOption.category_id == item.category_id)
                      .filter(QuestionOption.sub_category_id == item.sub_category_id)
                      .filter(QuestionOption.grade_id == item.grade_id)
                      .filter(QuestionOption.quiz_id == item.quiz_id)
                      .filter(QuestionOption.question_id == item.question_id)
                      .first())
    if check_existing:
        raise HTTPException(status_code=400, detail="A user with this name already exists.")

    model_item = QuestionOption(
        name=item.name,
        category_id=item.category_id,
        sub_category_id=item.sub_category_id,
        grade_id=item.grade_id,
        quiz_id=item.quiz_id,
        question_id=item.question_id,
        is_correct=item.is_correct,
    )
    db.add(model_item)
    db.commit()
    db.refresh(model_item)

    return model_item



def get_all_quiz_question_options_paginated(
    db: Session,
    category_id: int,
    page: int,
    limit: int,
    sub_category_id: Optional[int] = None,
    grade_id: Optional[int] = None,
    quiz_id: Optional[int] = None,
    question_id: Optional[int] = None
):
    offset = (page - 1) * limit

    query = db.query(QuestionOption).filter(QuestionOption.category_id == category_id)

    if sub_category_id:
        query = query.filter(QuestionOption.sub_category_id == sub_category_id)

    if grade_id:
        query = query.filter(QuestionOption.grade_id == grade_id)

    if quiz_id:
        query = query.filter(QuestionOption.quiz_id == quiz_id)

    if question_id:
        query = query.filter(QuestionOption.question_id == question_id)

    total = query.count()
    quizzes = query.offset(offset).limit(limit).all()

    return quizzes, total

