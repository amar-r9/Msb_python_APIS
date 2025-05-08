from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from app.database.connection import Base
from pydantic import BaseModel

from app.models.user import UserResponse
from app.utils.common import CATEGORY_MEDIA_FOLDER


class SubCategory(Base):
    __tablename__ = 'sub_categories'
    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey('categories.id'), index=True)
    name = Column(String)
    icon = Column(String, nullable=True)

    category = relationship("Category", back_populates="subcategories")
    submissions = relationship("Submission", back_populates="subcategory")


    quiz = relationship("Quiz", back_populates="subcategory")
    questions = relationship("Question", back_populates="subcategory")
    question_options = relationship("QuestionOption", back_populates="subcategory")
    student_answers = relationship("StudentAnswer", back_populates="subcategory")  # Add this line

    @property
    def icon_path(self):
        if self.icon:
            return f"{CATEGORY_MEDIA_FOLDER}{self.icon}"
        return None

# Pydantic Model for creating/updating students
class SubCategoryCreate(BaseModel):
    name: str
    category_id: int
    icon: str


# Pydantic Model for response with ORM mode enabled
class SubCategoryResponse(BaseModel):
    id: int
    name: str
    icon: str
    category_id: int

    class Config:
        orm_mode = True