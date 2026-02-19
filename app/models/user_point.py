from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from app.database.connection import Base
from pydantic import BaseModel

from app.models.user import UserResponse

class UserPoint(Base):
    __tablename__ = 'user_points'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), index=True)
    like_user_id = Column(Integer, nullable=True,index=True)

    grade_id = Column(Integer, ForeignKey('grades.id'), nullable=True)
    school_id = Column(Integer, ForeignKey('schools.id'), nullable=True)
    submission_id = Column(Integer, ForeignKey('submissions.id'), nullable=True)

    points = Column(Integer, nullable=True)
    point_type = Column(Integer, nullable=True)

    grade = relationship("Grade", back_populates="user_point")
    school = relationship("School", back_populates="user_point")
    user = relationship("User", back_populates="user_point")
    submission = relationship("Submission", back_populates="user_point")

# Pydantic Model for creating/updating students
class UserPointCreate(BaseModel):
    user_id: str
    user_id: str
    grade_id: int
    school_id: int
    points: int
    type: int



# Pydantic Model for response with ORM mode enabled
class UserPointResponse(BaseModel):
    user_id: str
    like_user_id: str
    grade_id: int
    school_id: int
    points: int
    type: int

    class Config:
        orm_mode = True