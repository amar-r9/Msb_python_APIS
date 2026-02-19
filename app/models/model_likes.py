from datetime import datetime

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from app.database.connection import Base
from pydantic import BaseModel

from app.models.user import UserResponse


class Like(Base):
    __tablename__ = 'likes'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), index=True)

    school_id = Column(Integer, ForeignKey('schools.id'), nullable=True)
    submission_id = Column(Integer, ForeignKey('submissions.id'), nullable=True)

    # grade_id = Column(Integer, ForeignKey('grades.id'), nullable=True)

    like_type = Column(Integer, nullable=True)
    likes = Column(Integer, nullable=True)

    # grade = relationship("Grade", back_populates="user_point")
    school = relationship("School", back_populates="likes")
    user = relationship("User", back_populates="likes")
    submission = relationship("Submission", back_populates="likes")


# Pydantic Model for creating/updating students
class LikeCreate(BaseModel):
    user_id: str
    school_id: int
    submission_id: int
    likes: int
    like_type: int


# Pydantic Model for response with ORM mode enabled
class LikeResponse(BaseModel):
    user_id: str
    school_id: int
    submission_id: int
    likes: int
    like_type: int
    created_at: datetime


    class Config:
        orm_mode = True
