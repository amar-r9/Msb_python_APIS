from datetime import datetime

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from app.database.connection import Base
from pydantic import BaseModel

from app.models.user import UserResponse


class Comment(Base):
    __tablename__ = 'comments'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), index=True)

    school_id = Column(Integer, ForeignKey('schools.id'), nullable=True)
    submission_id = Column(Integer, ForeignKey('submissions.id'), nullable=True)
    parent_id = Column(Integer, ForeignKey('comments.id'), nullable=True)

    # grade_id = Column(Integer, ForeignKey('grades.id'), nullable=True)

    comment = Column(Integer, nullable=True)
    created_at = Column(DateTime, nullable=True)

    # grade = relationship("Grade", back_populates="user_point")
    school = relationship("School", back_populates="comments")
    user = relationship("User", back_populates="comments")
    submission = relationship("Submission", back_populates="comments")


# Pydantic Model for creating/updating students
class LikeCreate(BaseModel):
    user_id: str
    school_id: int
    submission_id: int
    parent_id: int
    comment: int


# Pydantic Model for response with ORM mode enabled
class LikeResponse(BaseModel):
    user_id: str
    school_id: int
    submission_id: int
    parent_id: int
    comment: int
    created_at: datetime


    class Config:
        orm_mode = True
