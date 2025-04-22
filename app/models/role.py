from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from app.database.connection import Base
from pydantic import BaseModel

class Role(Base):
    __tablename__ = 'roles'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255))
    created_by = Column(Integer, nullable=True, index=True)

    user = relationship("User", back_populates="role")


# Pydantic Model for creating/updating students
class RoleCreate(BaseModel):
    name: int


# Pydantic Model for response with ORM mode enabled
class RoleResponse(BaseModel):
    id: int
    name: str
    created_by: int

    class Config:
        orm_mode = True