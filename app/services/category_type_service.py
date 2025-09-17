from sqlalchemy.orm import Session
from app.models.category_type import CategoryType

def get_category_type(db: Session, category_type_id: int):
    """
    Retrieves a single category type by its ID.
    """
    return db.query(CategoryType).filter(CategoryType.id == category_type_id).first()

def get_all_category_types(db: Session):
    """
    Retrieves all category types from the database.
    """
    return db.query(CategoryType).all()