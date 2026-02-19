from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.quiz import QuizCreate
from app.services.auth import get_current_user
from app.models.user import User
from app.services.quiz_service import create_quiz_by_data, get_all_quizes_paginated

router = APIRouter()


@router.get("/lists")
def get_quiz_lists(
    category_id: int = Query(..., ge=1, description="Category ID"),
    sub_category_id: Optional[int] = Query(None, description="Subcategory ID"),
    grade_id: Optional[int] = Query(None, description="Grade ID"),
    page: int = Query(1, ge=1, description="Page number (starts from 1)"),
    limit: int = Query(10, ge=1, le=100, description="Number of records per page (max 100)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    data, total = get_all_quizes_paginated(db, category_id, page, limit, sub_category_id, grade_id)

    return {
        "page": page,
        "limit": limit,
        "total": total,
        "total_pages": (total // limit) + (1 if total % limit > 0 else 0),
        "data": data
    }

@router.post("/create")
def create_quiz(post_item: QuizCreate, db: Session = Depends(get_db),current_user: User = Depends(get_current_user)):
    item = create_quiz_by_data(db, post_item)
    return item
