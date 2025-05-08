from typing import Type, Optional

from sqlalchemy.orm import Session, joinedload

from app.database.connection import get_db
from app.models.question import QuestionCreate, Question
from app.models.quiz import QuizCreate, Quiz
from app.models.category import CategoryCreate, Category, CategoryResponse
from app.models.subcategory import SubCategory
from app.models.student import Student, StudentCreate
from app.models.user import User
from app.utils.common import hash_password, BASE_URL, CATEGORY_MEDIA_FOLDER
from fastapi import APIRouter, Depends, HTTPException, status, Request


def create_quiz_questions_by_data(db: Session, item: QuestionCreate):

    check_existing = (db.query(Question)
                      .filter(Question.name == item.name)
                      .filter(Question.category_id == item.category_id)
                      .filter(Question.sub_category_id == item.sub_category_id)
                      .filter(Question.grade_id == item.grade_id)
                      .filter(Question.quiz_id == item.quiz_id)
                      .first())
    if check_existing:
        raise HTTPException(status_code=400, detail="A user with this name already exists.")

    model_item = Question(
        name=item.name,
        category_id=item.category_id,
        sub_category_id=item.sub_category_id,
        grade_id=item.grade_id,
        quiz_id=item.quiz_id,
    )
    db.add(model_item)
    db.commit()
    db.refresh(model_item)

    return model_item



from sqlalchemy.orm import joinedload

def get_all_quiz_questions_paginated(
    db: Session,
    category_id: int,
    page: int,
    limit: int,
    sub_category_id: Optional[int] = None,
    grade_id: Optional[int] = None,
    quiz_id: Optional[int] = None
):
    offset = (page - 1) * limit

    query = db.query(Question).options(
        joinedload(Question.question_options)
    ).filter(Question.category_id == category_id)

    if sub_category_id:
        query = query.filter(Question.sub_category_id == sub_category_id)

    if grade_id:
        query = query.filter(Question.grade_id == grade_id)

    if quiz_id:
        query = query.filter(Question.quiz_id == quiz_id)

    total = query.count()
    quizzes = query.offset(offset).limit(limit).all()

    return quizzes, total


