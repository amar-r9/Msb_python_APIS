import os
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Form, File, UploadFile
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.category import CategoryResponse, CategoryCreate, Category
from app.models.subcategory import SubCategoryCreate, SubCategory
from app.services.auth import get_current_user
from app.services.category import create_category_by_data, get_category_by_id, \
    get_all_category_paginated, get_all_sub_category_paginated, get_all_categories, create_sub_category_by_data
from app.models.user import User
from app.utils.common import save_uploaded_file

router = APIRouter()

# @router.get("/get-quiz-category")
# def get_category(id: str, db: Session = Depends(get_db),current_user: User = Depends(get_current_user)):
#     item = get_category_by_id(db, id)
#     if not item:
#         raise HTTPException(status_code=404, detail="Category not found")
#     return item

UPLOAD_DIR = "static/media/category_images/"

UPLOAD_SUB_CATEGORY_DIR = "static/media/sub_category_images/"


@router.post("/create-category")
async def create_category(
    name: str = Form(...),
    is_future: int = Form(...),
    type: int = Form(...),
    icon: UploadFile = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    check_existing = db.query(Category).filter(Category.name == name).first()
    if check_existing:
        raise HTTPException(status_code=400, detail="Category with this name already exists.")

    filename = None
    if icon:
        filename = save_uploaded_file(UPLOAD_DIR, icon, prefix=name)

    model_item = Category(
        name=name,
        icon=filename,
        is_future=is_future,
        type=type
    )
    db.add(model_item)
    db.commit()
    db.refresh(model_item)

    return {
        "id": model_item.id,
        "name": model_item.name,
        "icon": model_item.icon_path
    }







@router.get("/get-categories")
def get_categories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    data = get_all_categories(db)

    return {
        "data": data
    }




@router.post("/create-sub-categories")
async def create_sub_category(
    name: str = Form(..., description="Name of the subcategory"),
    category_id: int = Form(..., description="ID of the parent category"),
    description: Optional[str] = Form(None, description="Optional description"),
    icon: Optional[UploadFile] = File(None, description="Optional icon file"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Check if already exists
    check_existing = (
        db.query(SubCategory)
        .filter(SubCategory.name == name, SubCategory.category_id == category_id)
        .first()
    )
    if check_existing:
        raise HTTPException(
            status_code=400,
            detail="SubCategory already exists in this Category."
        )

    # Save icon if uploaded
    filename = None
    if icon is not None:
        filename = save_uploaded_file(UPLOAD_SUB_CATEGORY_DIR, icon, prefix=name)

    # Create subcategory
    model_item = SubCategory(
        name=name,
        category_id=category_id,
        description=description,
        icon=filename
    )
    db.add(model_item)
    db.commit()
    db.refresh(model_item)

    return {
        "id": model_item.id,
        "name": model_item.name,
        "icon": model_item.icon_path,  # returns full path or None
        "category_id": model_item.category_id,
        "description": model_item.description
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





@router.post("/update-category/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: int,
    name: Optional[str] = Form(None),
    is_future: Optional[int] = Form(None),
    type: Optional[int] = Form(None),
    icon: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Fetch the existing category
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    # Prevent duplicate names if updating the name
    if name and name != category.name:
        existing = db.query(Category).filter(Category.name == name).first()
        if existing:
            raise HTTPException(status_code=400, detail="Category with this name already exists.")
        category.name = name

    # Update fields if provided
    if is_future is not None:
        category.is_future = is_future
    if type is not None:
        category.type = type

    # Handle icon update
    if icon:
        filename = save_uploaded_file(UPLOAD_DIR, icon, prefix=category.name)
        category.icon = filename

    db.commit()
    db.refresh(category)

    # return {
    #     "id": category.id,
    #     "name": category.name,
    #     "icon": category.icon_path
    # }
    return category




@router.put("/update-sub-category/{sub_category_id}")
async def update_sub_category(
    sub_category_id: int,
    name: Optional[str] = Form(None, description="Updated name of the subcategory"),
    category_id: Optional[int] = Form(None, description="Updated parent category ID"),
    description: Optional[str] = Form(None, description="Updated description"),
    icon: Optional[UploadFile] = File(None, description="Updated icon file"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Fetch existing subcategory
    sub_category = db.query(SubCategory).filter(SubCategory.id == sub_category_id).first()
    if not sub_category:
        raise HTTPException(status_code=404, detail="SubCategory not found")

    # Check for duplicate name within the same category (only if name/category_id is updated)
    if name or category_id:
        target_category_id = category_id if category_id is not None else sub_category.category_id
        existing = (
            db.query(SubCategory)
            .filter(
                SubCategory.name == (name or sub_category.name),
                SubCategory.category_id == target_category_id,
                SubCategory.id != sub_category.id
            )
            .first()
        )
        if existing:
            raise HTTPException(
                status_code=400,
                detail="Another SubCategory with this name already exists in the target Category."
            )

    # Update fields if provided
    if name is not None:
        sub_category.name = name
    if category_id is not None:
        sub_category.category_id = category_id
    if description is not None:
        sub_category.description = description

    # Handle icon update
    if icon:
        filename = save_uploaded_file(UPLOAD_SUB_CATEGORY_DIR, icon, prefix=sub_category.name)
        sub_category.icon = filename

    db.commit()
    db.refresh(sub_category)

    return {
        "id": sub_category.id,
        "name": sub_category.name,
        "icon": sub_category.icon_path,
        "category_id": sub_category.category_id,
        "description": sub_category.description
    }


@router.delete("/delete-category/{category_id}")
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    # Optionally, handle cascading deletes or checks for related records here

    db.delete(category)
    db.commit()

    return {"detail": "Category deleted successfully"}