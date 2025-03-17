from typing import Type

from sqlalchemy import desc, func
from sqlalchemy.orm import Session, joinedload

from app.database.connection import get_db
from app.models import Submission, School, UserPoint
from app.models.category import CategoryCreate, Category, CategoryResponse
from app.models.subcategory import SubCategory
from app.models.student import Student, StudentCreate
from app.models.user import User
from app.routes.pre_auth_routes import get_user_student
from app.services.student import get_top_score_students_by_school, get_top_like_submissions_by_school
from app.services.submissions_service import get_submission_count_by_school_id, get_likes_count_by_school_id, \
    get_students_count_by_school_id, get_avg_points_by_school_id




def get_school_dashbaord(user:User, school_id: int):
    db: Session = next(get_db())

    # return user

    students_count = get_students_count_by_school_id(school_id)
    submissions_count = get_submission_count_by_school_id(school_id)
    submissions_likes = get_likes_count_by_school_id(school_id)

    school_avg_points = get_avg_points_by_school_id(school_id)

    top_students = get_top_score_students_by_school(school_id, 3)
    top_like_submissions = get_top_like_submissions_by_school(school_id, user, 5)



    return {
        "students_count": students_count,
        "submissions_count": submissions_count,
        "submissions_likes": submissions_likes,
        "avg_points": school_avg_points,
        'top_students': top_students,
        'top_like_submissions': top_like_submissions
        # "top_submissions_likes": 0,
        # "top_students": 0,
        # "school_rank": 0,
    }


def get_school_top_schools(user: User):
    db: Session = next(get_db())

    # Query the top 5 schools based on average points
    top_schools = (
        db.query(
            School.id,
            School.name,
            func.coalesce(func.sum(Student.points), 0).label("total_points"),
            func.count(Student.id).label("student_count"),
            (
                func.coalesce(func.sum(Student.points), 0) /
                func.nullif(func.count(Student.id), 0)
            ).label("avg_points")  # Calculate average points per student
        )
        .outerjoin(Student, School.id == Student.school_id)
        .group_by(School.id)
        .order_by(desc("avg_points"))  # Order by avg_points in descending order
        .limit(5)
        .all()
    )

    return [
        {
            "id": school.id,
            "name": school.name,
            "avg_points": round(school.avg_points, 2) if school.avg_points else 0,  # Handle null values
            "student_count": school.student_count
        }
        for school in top_schools
    ]


def update_rank_by_school_id(school_id: int):
    db: Session = next(get_db())

    points_count_by_school = (
        db.query(func.sum(UserPoint.points))
        .filter(UserPoint.school_id == school_id)
        .count()
    )

    students_count_by_school = (
        db.query(Student)
        .filter(Student.school_id == school_id)
        .count()
    )
    avg_points = round(points_count_by_school / students_count_by_school, 2) if students_count_by_school else 0

    # return avg_points

    # Update school's rank
    school = db.query(School).filter(School.id == school_id).first()
    if school:
        school.points = avg_points
        db.add(school)
        db.commit()
        return avg_points


    return None

def update_points_to_student_by_user_id(user_id: int):
    db: Session = next(get_db())

    points_count_by_user = (
        db.query(func.sum(UserPoint.points))
        .filter(UserPoint.user_id == user_id)
        .scalar()
    )

    student = get_user_student(db, user_id)

    # Update school's rank
    # user = db.query(User).filter(User.id == user_id).first()
    if student:
        student.points = points_count_by_user
        db.add(student)
        db.commit()

        update_rank_by_school_id(student.school_id)

        return student


    return None