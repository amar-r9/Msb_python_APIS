
from app.models.country import Country
from app.models.role import Role
from app.models.grade import Grade
from app.models.state import State
from app.models.student import Student
from app.models.user import User
from app.models.school import School
from app.models.submission import Submission
from app.models.category import Category
from app.models.category_type import CategoryType
from app.models.subcategory import SubCategory
from app.models.user_point import UserPoint
from app.models.model_likes import Like
from app.models.model_comments import Comment

# Ensure relationships are established after models are loaded
from sqlalchemy.orm import configure_mappers
configure_mappers()

