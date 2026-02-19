from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from app.database.connection import Base
from pydantic import BaseModel

from app.models.user import UserResponse

class Country(Base):
    __tablename__ = 'countries'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    created_by = Column(Integer, nullable=True, index=True)

    students = relationship("Student", back_populates="country")


# Pydantic Model for creating/updating students
class CountryCreate(BaseModel):
    name: int


# Pydantic Model for response with ORM mode enabled
class CountryResponse(BaseModel):
    id: int
    name: str
    created_by: int

    class Config:
        orm_mode = True