
from .country import Country
from .role import Role
from .grade import Grade
from .state import State
from .student import Student
from .user import User
from .school import School
from .submission import Submission
from .category import Category
from .category_type import CategoryType
from .subcategory import SubCategory
from .user_point import UserPoint
from .model_likes import Like
from .model_comments import Comment
from .quiz import Quiz
from .question import Question
from .question_option import QuestionOption
from .student_answer import StudentAnswer

# Ensure relationships are established after models are loaded
from sqlalchemy.orm import configure_mappers
configure_mappers()

