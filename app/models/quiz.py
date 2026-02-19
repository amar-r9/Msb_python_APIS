from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from app.database.connection import Base
from pydantic import BaseModel

from app.models.user import UserResponse
from app.utils.common import CATEGORY_MEDIA_FOLDER


class Quiz(Base):
    __tablename__ = "quizzes"
    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey('categories.id'), index=True)
    sub_category_id = Column(Integer, ForeignKey('sub_categories.id'), nullable=True, index=True)
    grade_id = Column(Integer, ForeignKey('grades.id'), index=True)
    name = Column(String)

    grade = relationship("Grade", back_populates="quiz")
    questions = relationship("Question", back_populates="quiz")

    category = relationship("Category", back_populates="quiz")
    subcategory = relationship("SubCategory", back_populates="quiz")

    question_options = relationship("QuestionOption", back_populates="quiz")
    student_answers = relationship("StudentAnswer", back_populates="quiz")  # Correct reverse relationship


# Pydantic Model for creating/updating students
class QuizCreate(BaseModel):
    name: str
    category_id: int
    sub_category_id: int
    grade_id: int


# Pydantic Model for response with ORM mode enabled
class QuizResponse(BaseModel):
    id: int
    name: str
    category_id: str
    sub_category_id: int
    grade_id: int

    class Config:
        orm_mode = True
        from_attributes = True
