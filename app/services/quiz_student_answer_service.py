from typing import Type, Optional

from sqlalchemy.orm import Session, joinedload

from app.database.connection import get_db
from app.models import QuestionOption
from app.models.question_option import QuestionOptionCreate
from app.models.quiz import QuizCreate, Quiz
from app.models.category import CategoryCreate, Category, CategoryResponse
from app.models.student_answer import StudentAnswerCreate, StudentAnswer
from app.models.subcategory import SubCategory
from app.models.student import Student, StudentCreate
from app.models.user import User
from app.utils.common import hash_password, BASE_URL, CATEGORY_MEDIA_FOLDER
from fastapi import APIRouter, Depends, HTTPException, status, Request


def save_student_answer(db: Session, item: StudentAnswerCreate, current_user: User):
    # Fetch the selected option to get is_correct
    selected_option = db.query(QuestionOption).filter(QuestionOption.id == item.option_id).first()
    if not selected_option:
        raise HTTPException(status_code=404, detail="Option not found")

    # Assuming the `StudentAnswer` table only needs the question_id and option_id
    student_answer = StudentAnswer(
        user_id=current_user['id'],  # Ensure 'current_user' is correctly used
        question_id=item.question_id,
        question_option_id=item.option_id,
        quiz_id=selected_option.quiz_id,
        category_id=selected_option.category_id,
        sub_category_id=selected_option.sub_category_id,
        grade_id=selected_option.grade_id,
        is_correct=selected_option.is_correct
    )

    db.add(student_answer)
    db.commit()
    db.refresh(student_answer)
    return student_answer


def get_all_quiz_question_answers_paginated(
    db: Session,
    category_id: int,
    page: int,
    limit: int,
    sub_category_id: Optional[int] = None,
    grade_id: Optional[int] = None,
    quiz_id: Optional[int] = None,
    question_id: Optional[int] = None,
    user_id: int = None
):
    offset = (page - 1) * limit

    query = db.query(QuestionOption).filter(QuestionOption.question_id == question_id)

    if category_id:
        query = query.filter(QuestionOption.category_id == category_id)

    if sub_category_id:
        query = query.filter(QuestionOption.sub_category_id == sub_category_id)

    if grade_id:
        query = query.filter(QuestionOption.grade_id == grade_id)

    if quiz_id:
        query = query.filter(QuestionOption.quiz_id == quiz_id)

    total = query.count()
    options = query.offset(offset).limit(limit).all()

    # Fetch student answers
    question_ids = list(set([opt.question_id for opt in options]))
    student_answers = db.query(StudentAnswer).filter(
        StudentAnswer.user_id == user_id,
        StudentAnswer.question_id.in_(question_ids)
    ).all()
    answer_map = {ans.question_id: (ans.question_option_id, ans.is_correct) for ans in student_answers}

    enriched_data = []
    for option in options:
        answered = answer_map.get(option.question_id)
        is_answered = answered is not None and answered[0] == option.id
        is_correct_answered = is_answered and answered[1] is True

        enriched_data.append({
            "id": option.id,
            "name": option.name,
            "category_id": option.category_id,
            "sub_category_id": option.sub_category_id,
            "question_id": option.question_id,
            "is_correct": option.is_correct,
            "is_answered": is_answered,
            "is_correct_answered": is_correct_answered
        })

    return enriched_data, total


