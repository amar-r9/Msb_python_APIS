from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from app.database.connection import Base
from pydantic import BaseModel

from app.models.user import UserResponse
from app.utils.common import SUBMISSIONS_MEDIA_FOLDER


class Submission(Base):
    __tablename__ = 'submissions'
    id = Column(Integer, primary_key=True, index=True)
    created_by = Column(Integer, ForeignKey('users.id'), nullable=True, index=True)  # Add ForeignKey to users table

    category_id  = Column(Integer, ForeignKey('categories.id'), nullable=True, index=True)
    sub_category_id  = Column(Integer, ForeignKey('sub_categories.id'),  nullable=True, index=True)

    grade_id = Column(Integer, ForeignKey('grades.id'), nullable=True)
    school_id = Column(Integer, ForeignKey('schools.id'), nullable=True)

    title  = Column(String, nullable=True)
    description  = Column(String, nullable=True)
    media  = Column(String, nullable=True)
    created_at  = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="submissions")  # Use string reference here
    category = relationship("Category", back_populates="submissions")
    subcategory = relationship("SubCategory", back_populates="submissions")


    grade = relationship("Grade", back_populates="submission")
    school = relationship("School", back_populates="submission")
    user_point = relationship("UserPoint", back_populates="submission")
    comments = relationship("Comment", back_populates="submission")
    likes = relationship("Like", back_populates="submission")



    @property
    def media_path(self):
        # Check if media is present
        if self.media:
            # Access the category_type through the related Category object
            if self.category and self.category.category_type:
                category_type = self.category.category_type.name
                # Set the media folder based on the category type
                category_folder = "images" if category_type == "image" else "videos" if category_type == "video" else "audios"
                return f"{SUBMISSIONS_MEDIA_FOLDER}{category_folder}/{self.media}"
        return None  # Return None if no media is present

# Pydantic Model for creating/updating students
class SubmissionCreate(BaseModel):
    name: int
    country_id: int


# Pydantic Model for response with ORM mode enabled
class SubmissionResponse(BaseModel):
    id: int
    created_by: int
    category_id: int
    sub_category_id: int
    title: str
    description: str
    media: str


    class Config:
        orm_mode = True