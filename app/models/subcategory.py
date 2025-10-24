import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from app.database.connection import Base
from pydantic import BaseModel

from app.models.user import UserResponse
from app.utils.common import SUB_CATEGORY_MEDIA_FOLDER
from app.models.talentgrades import TalentGrade,TalentGradeResponse

class SubCategory(Base):
    __tablename__ = 'sub_categories'
    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey('categories.id'), index=True)
    name = Column(String)
    icon = Column(String, nullable=True)
    description = Column(String, nullable=True)
    #added these fields as frontend expecting them
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    Talentgrade_id = Column(Integer, ForeignKey('talentgrades.id'), nullable=True)

    # grade = relationship("TalentGrade", back_populates="subcategories")
    category = relationship("Category", back_populates="subcategories")
    submissions = relationship("Submission", back_populates="subcategory")
    talent_grade = relationship("TalentGrade", back_populates="subcategories")


    quiz = relationship("Quiz", back_populates="subcategory")
    questions = relationship("Question", back_populates="subcategory")
    question_options = relationship("QuestionOption", back_populates="subcategory")
    student_answers = relationship("StudentAnswer", back_populates="subcategory")  # Add this line

    @property
    def icon_path(self):
        if self.icon:
            return f"{SUB_CATEGORY_MEDIA_FOLDER}{self.icon}"
        return None

# Pydantic Model for creating/updating students
class SubCategoryCreate(BaseModel):
    name: str
    category_id: int
    icon: str
    start_date: Optional[datetime.datetime] = None
    end_date: Optional[datetime.datetime] = None

# Pydantic Model for response with ORM mode enabled
class SubCategoryResponse(BaseModel):
    id: int
    name: str
    icon: Optional[str] = None
    category_id: int
    start_date: Optional[datetime.datetime] = None
    end_date: Optional[datetime.datetime] = None
    talent_grade: Optional[TalentGradeResponse] = None
    class Config:
        orm_mode = True