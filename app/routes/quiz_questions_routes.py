from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models import QuestionOption
from app.models.question import QuestionCreate, QuestionWithOptionsCreate, Question
from app.models.quiz import QuizCreate
from app.services.auth import get_current_user
from app.models.user import User
from app.services.quiz_questions_service import create_quiz_questions_by_data, get_all_quiz_questions_paginated
from app.services.quiz_service import create_quiz_by_data, get_all_quizes_paginated

router = APIRouter()


@router.get("/lists")
def get_quiz_lists(
    category_id: int = Query(..., ge=1, description="Category ID"),
    sub_category_id: Optional[int] = Query(None, description="Subcategory ID"),
    grade_id: Optional[int] = Query(None, description="Grade ID"),
    quiz_id: Optional[int] = Query(None, description="Quiz ID"),
    page: int = Query(1, ge=1, description="Page number (starts from 1)"),
    limit: int = Query(10, ge=1, le=100, description="Number of records per page (max 100)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    data, total = get_all_quiz_questions_paginated(db, category_id, page, limit, sub_category_id, grade_id, quiz_id)

    return {
        "page": page,
        "limit": limit,
        "total": total,
        "total_pages": (total // limit) + (1 if total % limit > 0 else 0),
        "data": data
    }

@router.post("/create")
def create_quiz(post_item: QuestionCreate, db: Session = Depends(get_db),current_user: User = Depends(get_current_user)):
    item = create_quiz_questions_by_data(db, post_item)
    return item



@router.post("/create_with_options", response_model=dict)
def create_question_with_options(payload: QuestionWithOptionsCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Create the Question
    question = Question(
        name=payload.name,
        quiz_id=payload.quiz_id,
        category_id=payload.category_id,
        sub_category_id=payload.sub_category_id,
        grade_id=payload.grade_id,
    )
    db.add(question)
    db.commit()
    db.refresh(question)

    # Create associated QuestionOptions
    options = [
        QuestionOption(
            name=option.name,
            is_correct=option.is_correct,
            quiz_id=payload.quiz_id,
            category_id=payload.category_id,
            sub_category_id=payload.sub_category_id,
            grade_id=payload.grade_id,
            question_id=question.id
        )
        for option in payload.options
    ]
    db.bulk_save_objects(options)
    db.commit()

    return {"message": "Question and options created successfully", "question_id": question.id}