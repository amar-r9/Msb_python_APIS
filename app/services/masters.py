from typing import Type

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models import Country, Grade, State, School, Student
from app.services.submissions_service import get_avg_points_by_school_id


# Method to get all users
def get_all_countries(db: Session):
    countries = db.query(Country).all()
    return  countries

# Method to get all users
def get_all_states(db: Session):
    states = db.query(State).all()
    return  states



# Method to get all users
def get_all_grades(db: Session):
    grades = db.query(Grade).all()

    return grades



def get_all_schools(db: Session):
    schools = (
        db.query(
            School.id,
            School.name,
            func.coalesce(func.sum(Student.points), 0).label("total_points"),
            func.count(Student.id).label("student_count")
        )
        .outerjoin(Student, School.id == Student.school_id)
        .group_by(School.id)
        .all()
    )

    return [
        {
            "id": s.id,
            "name": s.name,
            "avg_points": round(s.total_points / s.student_count, 2) if s.student_count > 0 else 0,  # Avoid division by zero
            "student_count": s.student_count
        }
        for s in schools
    ]



# Method to get all users
def get_all_schools_count(db: Session):
    schools = db.query(School).count()
    return schools
