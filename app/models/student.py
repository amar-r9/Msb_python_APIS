from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Date
from sqlalchemy.orm import relationship

from datetime import datetime, date  # Import datetime for Python's built-in datetime type


from app.database.connection import Base
from pydantic import BaseModel, ConfigDict

from app.models.grade import GradeResponse
from app.models.school import SchoolResponse
from app.models.user import UserResponse
from app.models.state import State

class Student(Base):
    __tablename__ = 'students'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    grade_id = Column(Integer, ForeignKey('grades.id'), nullable=True)
    school_id = Column(Integer, ForeignKey('schools.id'), nullable=True)
    country_id = Column(Integer, ForeignKey('countries.id'), nullable=True)
    state_id = Column(Integer, ForeignKey("states.id"), nullable=True)
    city = Column(String,nullable=True)
    dob = Column(Date,nullable=True)
    score = Column(Integer,nullable=True)
    points = Column(Integer,nullable=True)
    rank = Column(Integer,nullable=True)
    likes = Column(Integer,nullable=True)
    created_by = Column(Integer, nullable=True, index=True)

    # Additional fields for future reference (you might not need these directly in the Pydantic model)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    user = relationship("User", back_populates="students")
    state = relationship("State", back_populates="students")
    country = relationship("Country", back_populates="students")
    grade = relationship("Grade", back_populates="students")
    school = relationship("School", back_populates="students")


# Pydantic Model for creating/updating students
class StudentCreate(BaseModel):
    name: str
    email: str
    password: str
    grade_id: int
    school_id: int
    country_id: int
    state_id: int
    dob: date
    city: str


# Pydantic Model for response with ORM mode enabled
class StudentResponse(BaseModel):
    id: int
    user_id: int
    grade_id: int
    school_id: int
    country_id: int
    state_id: int
    points: int
    likes: int
    score: int
    city: str
    dob: date
    user: "UserResponse"
    # grade: "GradeResponse"
    # school: "SchoolResponse"


    class Config:
        orm_mode = True
        from_attributes = True