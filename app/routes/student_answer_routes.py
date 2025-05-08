from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.question import QuestionCreate
from app.models.quiz import QuizCreate
from app.models.student_answer import StudentAnswerCreate
from app.services.auth import get_current_user
from app.models.user import User
from app.services.quiz_questions_service import create_quiz_questions_by_data, get_all_quiz_questions_paginated
from app.services.quiz_service import create_quiz_by_data, get_all_quizes_paginated
from app.services.quiz_student_answer_service import get_all_quiz_question_answers_paginated, save_student_answer

router = APIRouter()


@router.get("/lists")
def get_quiz_lists(
    question_id: int = Query(..., description="Question ID"),
    category_id: Optional[int] = Query(None, ge=1, description="Category ID"),
    sub_category_id: Optional[int] = Query(None, description="Subcategory ID"),
    grade_id: Optional[int] = Query(None, description="Grade ID"),
    quiz_id: Optional[int] = Query(None, description="Quiz ID"),

    page: int = Query(1, ge=1, description="Page number (starts from 1)"),
    limit: int = Query(10, ge=1, le=100, description="Number of records per page (max 100)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    data, total = get_all_quiz_question_answers_paginated(db, category_id, page, limit, sub_category_id, grade_id, quiz_id, question_id, user_id=current_user["id"])

    return {
        "page": page,
        "limit": limit,
        "total": total,
        "total_pages": (total // limit) + (1 if total % limit > 0 else 0),
        "data": data
    }


@router.post("/create")
def create_quiz_answer(
    post_item: StudentAnswerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return save_student_answer(db, post_item, current_user)