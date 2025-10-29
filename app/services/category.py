from typing import Type

from sqlalchemy import text
from sqlalchemy.orm import Session, joinedload, selectinload

from app.database.connection import get_db
from app.models.category import CategoryCreate, Category, CategoryResponse
from app.models.subcategory import SubCategory, SubCategoryCreate
from app.models.submission import Submission
from app.models.student import Student, StudentCreate
from app.models.user import User
from app.utils.common import hash_password, BASE_URL, CATEGORY_MEDIA_FOLDER
from fastapi import APIRouter, Depends, HTTPException, status, Request


def create_category_by_data(db: Session, name: str):
    # Check duplicate
    check_existing = db.query(Category).filter(Category.name == name).first()
    if check_existing:
        raise HTTPException(status_code=400, detail="Category with this name already exists.")

    model_item = Category(
        name=name,
    )
    db.add(model_item)
    db.commit()
    db.refresh(model_item)

    return model_item



def create_sub_category_by_data(db: Session, item: SubCategoryCreate):
    # Check if subcategory with same name exists in the same category
    check_existing = (
        db.query(SubCategory)
        .filter(
            SubCategory.name == item.name,
            SubCategory.category_id == item.category_id
        )
        .first()
    )
    if check_existing:
        raise HTTPException(
            status_code=400,
            detail="SubCategory with this name already exists in the same Category."
        )

    model_item = SubCategory(
        name=item.name,
        category_id=item.category_id,
        icon=item.icon  # Don't forget to set icon if passed
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
            selectinload(Category.subcategories),
            joinedload(Category.category_type)
        )
        .all()
    )

    # Now you can directly access the icon_url property
    # for item in items:
    #     item.icon_url = item.icon_path

    #     if item.subcategories:
    #         for subcategory in item.subcategories:
    #             if subcategory.icon:
    #                 subcategory.icon_url = subcategory.icon_path

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


def get_grade_based_sub_category(
    db: Session, 
    category_id: int, 
    page: int, 
    limit: int, 
    user_id: int
):
    
    offset = (page - 1) * limit

    # --- Query 1: Get the TOTAL count of matching subcategories ---
    # This query finds the total number of items for pagination
    # *before* applying any limit or offset.
    
    total_query_sql = text("""
        SELECT
            COUNT(DISTINCT sc.id)
        FROM
            sub_categories sc 
        JOIN
            talentgrades t ON sc.Talentgrade_id = t.id 
        JOIN
            students s ON JSON_CONTAINS(t.grades_array, s.grade_id)
        WHERE
            sc.category_id = :category_id
            AND s.user_id = :user_id;
    """)
    
    # Execute the count query
    total_result = db.execute(
        total_query_sql, 
        {"category_id": category_id, "user_id": user_id}
    )
    total = total_result.scalar_one_or_none() or 0
    
    if total == 0:
        return [], 0 # No items match, return early

    # --- Query 2: Get the DATA for the current page ---
    # This is your SQL query, now with LIMIT and OFFSET for pagination.
    
    data_query_sql = text("""
        SELECT
            sc.* FROM
            sub_categories sc 
        JOIN
            talentgrades t ON sc.Talentgrade_id = t.id 
        JOIN
            students s ON JSON_CONTAINS(t.grades_array, s.grade_id)
        WHERE
            sc.category_id = :category_id
            AND s.user_id = :user_id
        GROUP BY
            sc.id
        LIMIT :limit OFFSET :offset;
    """)
    
    # This is the "hybrid" part. We run raw SQL, but map the results
    # back to your SubCategory model.
    items = db.query(SubCategory).from_statement(data_query_sql).params(
        category_id=category_id, 
        user_id=user_id, 
        limit=limit, 
        offset=offset
    ).all()



    #checkign the subcategory submissions and making sure the the user has not submitted already

    subcategory_ids_on_page = [item.id for item in items]

    submitted_rows = db.query(Submission.sub_category_id).filter(
        Submission.created_by == user_id,
        Submission.sub_category_id.in_(subcategory_ids_on_page)
    )


    submitted_set = {row[0] for row in submitted_rows}


    # This part still works because 'items' is a list of SubCategory objects
    for item in items:
        item.icon_url = item.icon_path
        item.isSubmitted = item.id in submitted_set
    return items, total