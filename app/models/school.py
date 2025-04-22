from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from app.database.connection import Base
from pydantic import BaseModel


class School(Base):
    __tablename__ = 'schools'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255))
    points = Column(Integer, nullable=True, index=True)
    created_by = Column(Integer, nullable=True, index=True)

    students = relationship("Student", back_populates="school")
    submission = relationship("Submission", back_populates="school")
    user_point = relationship("UserPoint", back_populates="school")
    comments = relationship("Comment", back_populates="school")
    likes = relationship("Like", back_populates="school")


# Pydantic Model for creating/updating students
class SchoolCreate(BaseModel):
    name: int


# Pydantic Model for response with ORM mode enabled
class SchoolResponse(BaseModel):
    id: int
    name: str
    created_by: int

    class Config:
        orm_mode = True