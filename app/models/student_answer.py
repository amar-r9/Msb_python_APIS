from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship

from app.database.connection import Base
from pydantic import BaseModel

from app.models.user import UserResponse
from app.utils.common import CATEGORY_MEDIA_FOLDER


class StudentAnswer(Base):
    __tablename__ = "student_answers"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)  # ✅ Add this line

    quiz_id = Column(Integer, ForeignKey("quizzes.id"), index=True)
    category_id = Column(Integer, ForeignKey('categories.id'), index=True)
    sub_category_id = Column(Integer, ForeignKey('sub_categories.id'), nullable=True, index=True)
    grade_id = Column(Integer, ForeignKey('grades.id'), index=True)
    question_id = Column(Integer, ForeignKey("questions.id"))
    question_option_id = Column(Integer, ForeignKey("question_options.id"))
    is_correct = Column(Boolean)


    user = relationship("User", back_populates="student_answers")  # ✅ Add this line
    quiz = relationship("Quiz", back_populates="student_answers")  # Correct reverse relationship
    category = relationship("Category", back_populates="student_answers")
    subcategory = relationship("SubCategory", back_populates="student_answers")
    grade = relationship("Grade", back_populates="student_answers")



# Pydantic Model for creating/updating students
class StudentAnswerCreate(BaseModel):
    question_id: int
    option_id: int  # This should map to question_option_id

    class Config:
        orm_mode = True
        from_attributes = True


class StudentAnswerResponse(BaseModel):
    id: int
    quiz_id: int
    category_id: int
    sub_category_id: int
    grade_id: int
    question_id: int
    question_option_id: int
    is_correct: bool

    class Config:
        orm_mode = True
        from_attributes = True