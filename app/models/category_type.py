from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from app.database.connection import Base
from pydantic import BaseModel

from app.models.user import UserResponse

class CategoryType(Base):
    __tablename__ = 'category_types'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)

    categories = relationship("Category", back_populates="category_type")



# Pydantic Model for creating/updating students
class CategoryTypeCreate(BaseModel):
    name: str


# Pydantic Model for response with ORM mode enabled
class CategoryTypeResponse(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True