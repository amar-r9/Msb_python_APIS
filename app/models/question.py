from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from app.database.connection import Base
from pydantic import BaseModel

from app.models.user import UserResponse
from app.utils.common import CATEGORY_MEDIA_FOLDER
from typing import List


class Question(Base):
    __tablename__ = "questions"
    id = Column(Integer, primary_key=True, index=True)
    quiz_id = Column(Integer, ForeignKey("quizzes.id"), index=True)
    category_id = Column(Integer, ForeignKey('categories.id'), index=True)
    sub_category_id = Column(Integer, ForeignKey('sub_categories.id'),  nullable=True, index=True)
    grade_id = Column(Integer, ForeignKey('grades.id'), index=True)
    name = Column(String)

    quiz = relationship("Quiz", back_populates="questions")
    category = relationship("Category", back_populates="questions")
    subcategory = relationship("SubCategory", back_populates="questions")
    grade = relationship("Grade", back_populates="question")
    question_options = relationship("QuestionOption", backref="question")  # or back_populates


# Pydantic Model for creating/updating students
class QuestionCreate(BaseModel):
    name: str
    quiz_id: int
    category_id: int
    sub_category_id: int
    grade_id: int


# Pydantic Model for response with ORM mode enabled
class QuestionResponse(BaseModel):
    id: int
    name: str
    quiz_id: str
    category_id: str
    sub_category_id: int
    grade_id: int


    class Config:
        orm_mode = True
        from_attributes = True


class QuestionOptionCreate(BaseModel):
    name: str
    is_correct: bool


class QuestionWithOptionsCreate(BaseModel):
    name: str
    quiz_id: int
    category_id: int
    sub_category_id: int
    grade_id: int
    options: List[QuestionOptionCreate]