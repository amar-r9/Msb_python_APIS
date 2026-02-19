from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from app.database.connection import Base
from pydantic import BaseModel

from app.models.user import UserResponse

class State(Base):
    __tablename__ = 'states'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    country_id = Column(Integer, nullable=True, index=True)
    created_by = Column(Integer, nullable=True, index=True)

    students = relationship("Student", back_populates="state")


# Pydantic Model for creating/updating students
class StateCreate(BaseModel):
    name: int
    country_id: int


# Pydantic Model for response with ORM mode enabled
class StateResponse(BaseModel):
    id: int
    name: str
    country_id: int
    created_by: int

    class Config:
        orm_mode = True