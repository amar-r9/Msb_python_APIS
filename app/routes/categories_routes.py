from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.category import CategoryResponse, CategoryCreate
from app.services.auth import get_current_user
from app.services.category import create_category_by_data, get_category_by_id, \
    get_all_category_paginated, get_all_sub_category_paginated, get_all_categories
from app.models.user import User


router = APIRouter()

# @router.get("/get-quiz-category")
# def get_category(id: str, db: Session = Depends(get_db),current_user: User = Depends(get_current_user)):
#     item = get_category_by_id(db, id)
#     if not item:
#         raise HTTPException(status_code=404, detail="Category not found")
#     return item


@router.post("/create-category")
def create_category(user: CategoryCreate, db: Session = Depends(get_db),current_user: User = Depends(get_current_user)):
    item = create_category_by_data(db, user)
    return item




@router.get("/get-categories")
def get_categories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    data = get_all_categories(db)

    return {
        "data": data
    }



@router.get("/get-sub-categories")
def get_quiz_sub_categories(
    category_id: int = Query('', ge=1, description="category id"),
    page: int = Query(1, ge=1, description="Page number (starts from 1)"),
    limit: int = Query(10, ge=1, le=100, description="Number of users per page (max 100)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    data, total = get_all_sub_category_paginated(db, category_id,page, limit)

    return {
        "page": page,
        "limit": limit,
        "total": total,
        "total_pages": (total // limit) + (1 if total % limit > 0 else 0),
        # "current_user": current_user,
        "data": data
    }