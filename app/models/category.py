from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from app.database.connection import Base
from pydantic import BaseModel

from app.models.user import UserResponse
from app.utils.common import CATEGORY_MEDIA_FOLDER


class Category(Base):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255))
    icon = Column(String(255))
    is_future = Column(Integer)
    type = Column(Integer, ForeignKey('category_types.id'), index=True)

    subcategories = relationship("SubCategory", back_populates="category")
    submissions = relationship("Submission", back_populates="category")
    category_type = relationship(
        "CategoryType",
        back_populates="categories",
        primaryjoin="Category.type == CategoryType.id"
    )


    @property
    def icon_path(self):
        if self.icon:
            return f"{CATEGORY_MEDIA_FOLDER}{self.icon}"
        return None


# Pydantic Model for creating/updating students
class CategoryCreate(BaseModel):
    name: str
    icon: str
    is_future: int
    type: int


# Pydantic Model for response with ORM mode enabled
class CategoryResponse(BaseModel):
    id: int
    name: str
    icon: str
    is_future: int
    type: int

    @property
    def icon_url(self):
        if self.icon:
            return f"{CATEGORY_MEDIA_FOLDER}{self.icon}"
        return None

    class Config:
        orm_mode = True
        from_attributes = True