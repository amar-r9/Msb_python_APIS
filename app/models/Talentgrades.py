# In a new file: app/models/talent_grade.py

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.types import JSON
from app.database.connection import Base
from pydantic import BaseModel
from typing import List

# --- SQLAlchemy Model ---
class TalentGrade(Base):
    __tablename__ = 'Talentgrades' # Using singular 'TalentGrade' for the class name
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    grades_array = Column(JSON)
    subcategories = relationship("SubCategory", back_populates="talent_grade")


# --- Pydantic Model ---
class TalentGradeResponse(BaseModel):
    id: int # It's good practice to include the ID
    name: str
    grades_array: List[int]

    # The Config class must be an INNER class of the Pydantic model
    class Config:
        from_attributes = True