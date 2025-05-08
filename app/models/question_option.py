from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship

from app.database.connection import Base
from pydantic import BaseModel

from app.models.user import UserResponse
from app.utils.common import CATEGORY_MEDIA_FOLDER


class QuestionOption(Base):
    __tablename__ = "question_options"
    id = Column(Integer, primary_key=True, index=True)

    quiz_id = Column(Integer, ForeignKey('quizzes.id'), index=True)
    category_id = Column(Integer, ForeignKey('categories.id'), index=True)
    sub_category_id = Column(Integer, ForeignKey('sub_categories.id'),  nullable=True, index=True)
    grade_id = Column(Integer, ForeignKey('grades.id'), index=True)
    question_id = Column(Integer, ForeignKey("questions.id"))
    name = Column(String)
    is_correct = Column(Boolean)

    quiz = relationship("Quiz", back_populates="question_options")
    category = relationship("Category", back_populates="question_options")
    subcategory = relationship("SubCategory", back_populates="question_options")
    grade = relationship("Grade", back_populates="question_options")



# Pydantic Model for creating/updating students
class QuestionOptionCreate(BaseModel):
    name: str
    question_id: int
    quiz_id: int
    category_id: int
    sub_category_id: int
    grade_id: int
    is_correct: bool


# Pydantic Model for response with ORM mode enabled
class QuestionOptionResponse(BaseModel):
    id: int
    name: str
    quiz_id: str
    category_id: str
    sub_category_id: int
    grade_id: int
    question_id: int
    is_correct: bool



    class Config:
        orm_mode = True
        from_attributes = True