
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

# Import the new service and the Pydantic response model
from app.services import category_type_service
from app.models.category_type import CategoryTypeResponse
from app.database.connection import get_db

router = APIRouter(
    prefix="/category-types",
    tags=["Category Types"]
)

@router.get("/", response_model=List[CategoryTypeResponse])
def read_all_category_types(db: Session = Depends(get_db)):
    """
    Retrieve all category types.
    """
    category_types = category_type_service.get_all_category_types(db)
    return category_types

@router.get("/{category_type_id}", response_model=CategoryTypeResponse)
def read_category_type(category_type_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a specific category type by its ID.
    """
    db_category_type = category_type_service.get_category_type(db, category_type_id=category_type_id)
    if db_category_type is None:
        raise HTTPException(status_code=404, detail="CategoryType not found")
    return db_category_type