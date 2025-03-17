from sqlalchemy import Column, Integer, String, Boolean
from app.database.connection import Base
from pydantic import BaseModel
from sqlalchemy.orm import relationship
from app.models.role import Role
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from typing import Optional
from datetime import datetime, date  # Import datetime for Python's built-in datetime type

from app.utils.common import USER_PROFILES_MEDIA_FOLDER


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(200), nullable=False)
    image = Column(String(200), nullable=False)

    reset_token = Column(String(200), nullable=False)
    token_expiry = Column(Integer, nullable=False)
    is_verified = Column(Boolean, nullable=False)

    role_id = Column(Integer, ForeignKey("roles.id"), nullable=True)
    role = relationship("Role", back_populates="user")

    students = relationship("Student", back_populates="user")
    submissions = relationship("Submission", back_populates="user")
    user_point = relationship("UserPoint", back_populates="user")
    comments = relationship("Comment", back_populates="user")
    likes = relationship("Like", back_populates="user")

    @property
    def image_path(self):
        if self.image:
            return f"{USER_PROFILES_MEDIA_FOLDER}{self.image}"
        return None

    # points = relationship(
    #     "UserPoint",
    #     back_populates="users",
    #     primaryjoin="User.id == UserPoint.user_id"
    # )

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    image: Optional[str] = None
    role_id: Optional[int] = None

    class Config:
        from_attributes = True
        orm_mode = True


class UserCreate(BaseModel):
    name: str
    email: str
    password: str
    image: str
    role_id: int


class LoginRequest(BaseModel):
    email: str = "monishvd@gmail.com"
    password: str = "1234567890"
    # email: str
    # password: str


class RegisterStudentRequest(BaseModel):
    name: str
    email: str
    password: str
    grade_id: int
    country_id: int
    state_id: Optional[int] = None  # Make state_id optional
    city: str
    school_id: Optional[int] = None  # Make school_id optional
    school_name: Optional[str] = None  # Make school_name optional for existing schools
    dob: date


class TokenStudentResponse(BaseModel):
    student: object
    access_token: str
    token_type: str
