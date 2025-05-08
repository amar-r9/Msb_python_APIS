from typing import Type

from sqlalchemy.orm import Session, joinedload

from app.database.connection import get_db
from app.models.category import CategoryCreate, Category, CategoryResponse
from app.models.subcategory import SubCategory
from app.models.student import Student, StudentCreate
from app.models.user import User
from app.utils.common import hash_password, BASE_URL, CATEGORY_MEDIA_FOLDER
from fastapi import APIRouter, Depends, HTTPException, status, Request


def create_category_by_data(db: Session, item: CategoryCreate):
    student_role_id = 2  # Replace with the ID of the student role in your database
    default_password = hash_password("password")  # Replace with your default password

    check_existing = db.query(Category).filter(Category.name == item.name).first()
    if check_existing:
        raise HTTPException(status_code=400, detail="A user with this name already exists.")

    model_item = Category(
        name=item.name,
    )
    db.add(model_item)
    db.commit()
    db.refresh(model_item)

    return model_item


# def get_student_by_email(db: Session, email: str):
#     return db.query(User).filter(User.email == email).first()
#
#
def get_category_by_id(db: Session, id: str):
    return db.query(Category).filter(Category.id == id).first()


def get_category_from_id(id: str):
    db: Session = next(get_db())
    # return db.query(Category).filter(Category.id == id).first()
    category = db.query(Category).options(joinedload(Category.category_type)).filter(Category.id == id).first()
    return category


# # Method to get all users
# def get_all_students(db: Session) -> list[Type[User]]:
#     return db.query(User).all()


def get_all_category_paginated(db: Session, page: int, limit: int):
    offset = (page - 1) * limit

    item_query = db.query(Category).offset(offset).limit(limit).all()

    # for item in item_query:
    #     if item.icon:
    #         item.icon_url = f"{CATEGORY_MEDIA_FOLDER}{item.icon}"
    # Count only the filtered records
    total = db.query(Category).offset(offset).limit(limit).count()

    return item_query, total


def get_all_categories(db: Session):
    items = (
        db.query(Category)
        .options(
            joinedload(Category.subcategories),
            joinedload(Category.category_type)
        )
        .all()
    )

    # Now you can directly access the icon_url property
    for item in items:
        item.icon_url = item.icon_path

        if item.subcategories:
            for subcategory in item.subcategories:
                if subcategory.icon:
                    subcategory.icon_url = subcategory.icon_path

    return items


def get_future_categories(db: Session):
    items = (db.query(Category)
             .options(
        joinedload(Category.subcategories),
        joinedload(Category.category_type)
    )
             .filter(Category.is_future == 1).all())

    # Now you can directly access the icon_url property
    for item in items:
        item.icon_url = item.icon_path

        if item.subcategories:
            for subcategory in item.subcategories:
                if subcategory.icon:
                    subcategory.icon_url = subcategory.icon_path

    return items


def get_all_sub_category_paginated(db: Session, category_id: int, page: int, limit: int):
    offset = (page - 1) * limit

    # Apply pagination with OFFSET and LIMIT
    items = (db.query(SubCategory)
             .filter(SubCategory.category_id == category_id)
             .offset(offset)
             .limit(limit)
             .all()
             )

    for item in items:
        item.icon_url = item.icon_path

        # if item.subcategories:
        #     for subcategory in item.subcategories:
        #         if subcategory.icon:
        #             subcategory.icon_url = subcategory.icon_path

    total = db.query(SubCategory).filter(SubCategory.category_id == category_id).offset(offset).limit(limit).count()

    return items, total
