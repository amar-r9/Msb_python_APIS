from typing import Type, Optional

from sqlalchemy import desc, func
from sqlalchemy.orm import Session, joinedload, defer

from app.database.connection import get_db
from app.models import Submission, Comment, Like
from app.models.category import CategoryCreate, Category, CategoryResponse
from app.models.subcategory import SubCategory
from app.models.student import Student, StudentCreate
from app.models.user import User
from app.routes.pre_auth_routes import get_user_student
from fastapi import APIRouter, Depends, HTTPException, status, Request



def get_submission_by_id(submission_id: int, user: Optional[User] = None):
    db: Session = next(get_db())

    # Fetch the student profile associated with the user
    # student = get_user_student(db, user.id)

    # if not student:
    #     raise HTTPException(status_code=404, detail="Student profile not found")

    submission = (
        db.query(Submission)
        .filter(Submission.id == submission_id)
        .join(User, Submission.created_by == User.id)  # Assuming `Submission.created_by` links to `User.id`
        .join(Category,
              Submission.category_id == Category.id)  # Assuming `Submission.category_id` links to `Category.id`
        .join(SubCategory,
              Submission.sub_category_id == SubCategory.id)  # Assuming `Submission.sub_category_id` links to `SubCategory.id`
        .options(
            joinedload(Submission.user),  # Load user relationship
            joinedload(Submission.category),  # Load category relationship
            joinedload(Submission.subcategory),  # Load sub_category relationship
            joinedload(Submission.user).defer(User.password),
            joinedload(Submission.user).joinedload(User.students),
        )
        .order_by(desc(Submission.id))
        .first()
    )

    # Check if the submission exists
    if not submission:
        raise HTTPException(status_code=404, detail="No submission found by id")

    # Format the submission using the existing formatting function
    formatted_submission = formart_submission(submission, user)

    return formatted_submission


def get_auth_school_and_grade(user: User, page: int, limit: int):
    offset = (page - 1) * limit

    db: Session = next(get_db())

    # Fetch the student profile associated with the user
    student = get_user_student(db, user.id)

    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")

    submissions = (
        db.query(Submission)
        .filter(Submission.school_id == student.school_id, Submission.grade_id == student.grade_id)
        .join(User, Submission.created_by == User.id)  # Assuming `Submission.created_by` links to `User.id`
        .join(Category,
              Submission.category_id == Category.id)  # Assuming `Submission.category_id` links to `Category.id`
        .join(SubCategory,
              Submission.sub_category_id == SubCategory.id)  # Assuming `Submission.sub_category_id` links to `SubCategory.id`
        .options(
            joinedload(Submission.user),  # Load user relationship
            joinedload(Submission.category),  # Load category relationship
            joinedload(Submission.subcategory),  # Load sub_category relationship
            joinedload(Submission.user).defer(User.password),
            joinedload(Submission.user).joinedload(User.students),
        )
        .order_by(desc(Submission.id))
        .offset(offset).limit(limit)
        .all()
    )

    # Check if any submissions were found
    if not submissions:
        raise HTTPException(status_code=404, detail="No submissions found ")

    formatted_submissions = [formart_submission(submission, user) for submission in submissions]

    submissions_count = (
        db.query(Submission)
        .filter(Submission.school_id == student.school_id, Submission.grade_id == student.grade_id)
        .join(User, Submission.created_by == User.id)  # Assuming `Submission.created_by` links to `User.id`
        .join(Category,
              Submission.category_id == Category.id)  # Assuming `Submission.category_id` links to `Category.id`
        .join(SubCategory,
              Submission.sub_category_id == SubCategory.id)  # Assuming `Submission.sub_category_id` links to `SubCategory.id`
        .options(
            joinedload(Submission.user),  # Load user relationship
            joinedload(Submission.category),  # Load category relationship
            joinedload(Submission.subcategory),  # Load sub_category relationship
            joinedload(Submission.user).defer(User.password),
            joinedload(Submission.user).joinedload(User.students),
        )
        .count()
    )

    return formatted_submissions, submissions_count


def get_submission_by_auth(user: User, page: int, limit: int):
    offset = (page - 1) * limit

    db: Session = next(get_db())

    # Fetch the student profile associated with the user
    student = get_user_student(db, user.id)

    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")

    submissions = (
        db.query(Submission)
        .filter(Submission.created_by == user.id)
        .join(User, Submission.created_by == User.id)  # Assuming `Submission.created_by` links to `User.id`
        .join(Category,
              Submission.category_id == Category.id)  # Assuming `Submission.category_id` links to `Category.id`
        .join(SubCategory,
              Submission.sub_category_id == SubCategory.id)  # Assuming `Submission.sub_category_id` links to `SubCategory.id`
        .options(
            joinedload(Submission.user),  # Load user relationship
            joinedload(Submission.category),  # Load category relationship
            joinedload(Submission.subcategory),  # Load sub_category relationship
            joinedload(Submission.user).defer(User.password),
            joinedload(Submission.user).joinedload(User.students),
        )
        .order_by(desc(Submission.id))
        .offset(offset).limit(limit)
        .all()
    )

    # Check if any submissions were found
    if not submissions:
        raise HTTPException(status_code=404, detail="No submissions found ")

    formatted_submissions = [formart_submission(submission, user) for submission in submissions]

    submissions_count = (
        db.query(Submission)
        .filter(Submission.created_by == user.id)
        .join(User, Submission.created_by == User.id)  # Assuming `Submission.created_by` links to `User.id`
        .join(Category,
              Submission.category_id == Category.id)  # Assuming `Submission.category_id` links to `Category.id`
        .join(SubCategory,
              Submission.sub_category_id == SubCategory.id)  # Assuming `Submission.sub_category_id` links to `SubCategory.id`
        .options(
            joinedload(Submission.user),  # Load user relationship
            joinedload(Submission.category),  # Load category relationship
            joinedload(Submission.subcategory),  # Load sub_category relationship
            joinedload(Submission.user).defer(User.password),
            joinedload(Submission.user).joinedload(User.students),
        )
        .count()
    )

    return formatted_submissions, submissions_count


def get_auth_school(user: User, page: int, limit: int):
    offset = (page - 1) * limit

    db: Session = next(get_db())

    # Fetch the student profile associated with the user
    student = get_user_student(db, user.id)

    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")

    submissions = (
        db.query(Submission)
        .filter(Submission.school_id == student.school_id)
        .join(User, Submission.created_by == User.id)  # Assuming `Submission.created_by` links to `User.id`
        .join(Category,
              Submission.category_id == Category.id)  # Assuming `Submission.category_id` links to `Category.id`
        .join(SubCategory,
              Submission.sub_category_id == SubCategory.id)  # Assuming `Submission.sub_category_id` links to `SubCategory.id`
        .options(
            joinedload(Submission.user),  # Load user relationship
            joinedload(Submission.category),  # Load category relationship
            joinedload(Submission.subcategory),  # Load sub_category relationship
            joinedload(Submission.user).defer(User.password),
            joinedload(Submission.user).joinedload(User.students),
        )
        .order_by(desc(Submission.id))
        .offset(offset).limit(limit)
        .all()
    )

    # Check if any submissions were found
    if not submissions:
        raise HTTPException(status_code=404, detail="No submissions found ")

    formatted_submissions = [formart_submission(submission, user) for submission in submissions]

    submissions_count = (
        db.query(Submission)
        .filter(Submission.school_id == student.school_id)
        .join(User, Submission.created_by == User.id)  # Assuming `Submission.created_by` links to `User.id`
        .join(Category,
              Submission.category_id == Category.id)  # Assuming `Submission.category_id` links to `Category.id`
        .join(SubCategory,
              Submission.sub_category_id == SubCategory.id)  # Assuming `Submission.sub_category_id` links to `SubCategory.id`
        .options(
            joinedload(Submission.user),  # Load user relationship
            joinedload(Submission.category),  # Load category relationship
            joinedload(Submission.subcategory),  # Load sub_category relationship
            joinedload(Submission.user).defer(User.password),
            joinedload(Submission.user).joinedload(User.students),
        )
        .count()
    )

    return formatted_submissions, submissions_count


def get_by_school(school_id: int, page: int, limit: int, user: Optional[User] = None):
    offset = (page - 1) * limit

    db: Session = next(get_db())

    submissions = (
        db.query(Submission)
        .filter(Submission.school_id == school_id)
        .join(User, Submission.created_by == User.id)  # Assuming `Submission.created_by` links to `User.id`
        .join(Category,
              Submission.category_id == Category.id)  # Assuming `Submission.category_id` links to `Category.id`
        .join(SubCategory,
              Submission.sub_category_id == SubCategory.id)  # Assuming `Submission.sub_category_id` links to `SubCategory.id`
        .options(
            joinedload(Submission.user),  # Load user relationship
            joinedload(Submission.category),  # Load category relationship
            joinedload(Submission.subcategory),  # Load sub_category relationship
            joinedload(Submission.user).defer(User.password),
            joinedload(Submission.user).joinedload(User.students),
        )
        .order_by(desc(Submission.id))
        .offset(offset).limit(limit)
        .all()
    )

    # Check if any submissions were found
    if not submissions:
        raise HTTPException(status_code=404, detail="No submissions found ")

    formatted_submissions = [formart_submission(submission, user) for submission in submissions]

    submissions_count = (
        db.query(Submission)
        .filter(Submission.school_id == school_id)
        .join(User, Submission.created_by == User.id)  # Assuming `Submission.created_by` links to `User.id`
        .join(Category,
              Submission.category_id == Category.id)  # Assuming `Submission.category_id` links to `Category.id`
        .join(SubCategory,
              Submission.sub_category_id == SubCategory.id)  # Assuming `Submission.sub_category_id` links to `SubCategory.id`
        .options(
            joinedload(Submission.user),  # Load user relationship
            joinedload(Submission.category),  # Load category relationship
            joinedload(Submission.subcategory),  # Load sub_category relationship
            joinedload(Submission.user).defer(User.password),
            joinedload(Submission.user).joinedload(User.students),
        )
        .count()
    )

    return formatted_submissions, submissions_count


def get_by_school_with_grade(school_id: int, grade_id: int, page: int, limit: int, user: Optional[User] = None):
    offset = (page - 1) * limit

    db: Session = next(get_db())

    submissions = (
        db.query(Submission)
        .filter(Submission.school_id == school_id, Submission.grade_id == grade_id)
        .join(User, Submission.created_by == User.id)  # Assuming `Submission.created_by` links to `User.id`
        .join(Category,
              Submission.category_id == Category.id)  # Assuming `Submission.category_id` links to `Category.id`
        .join(SubCategory,
              Submission.sub_category_id == SubCategory.id)  # Assuming `Submission.sub_category_id` links to `SubCategory.id`
        .options(
            joinedload(Submission.user),  # Load user relationship
            joinedload(Submission.category),  # Load category relationship
            joinedload(Submission.subcategory),  # Load sub_category relationship
            joinedload(Submission.user).defer(User.password),
            joinedload(Submission.user).joinedload(User.students),
        )
        .order_by(desc(Submission.id))
        .offset(offset).limit(limit)
        .all()
    )

    # Check if any submissions were found
    if not submissions:
        raise HTTPException(status_code=404, detail="No submissions found ")

    formatted_submissions = [formart_submission(submission, user) for submission in submissions]

    submissions_count = (
        db.query(Submission)
        .filter(Submission.school_id == school_id, Submission.grade_id == grade_id)
        .join(User, Submission.created_by == User.id)  # Assuming `Submission.created_by` links to `User.id`
        .join(Category,
              Submission.category_id == Category.id)  # Assuming `Submission.category_id` links to `Category.id`
        .join(SubCategory,
              Submission.sub_category_id == SubCategory.id)  # Assuming `Submission.sub_category_id` links to `SubCategory.id`
        .options(
            joinedload(Submission.user),  # Load user relationship
            joinedload(Submission.category),  # Load category relationship
            joinedload(Submission.subcategory),  # Load sub_category relationship
            joinedload(Submission.user).defer(User.password),
            joinedload(Submission.user).joinedload(User.students),
        )
        .count()
    )

    return formatted_submissions, submissions_count


def get_by_user(user_id: int, page: int, limit: int, user: Optional[User] = None):
    offset = (page - 1) * limit

    db: Session = next(get_db())

    submissions = (
        db.query(Submission)
        .filter(Submission.created_by == user_id)
        .join(User, Submission.created_by == User.id)  # Assuming `Submission.created_by` links to `User.id`
        .join(Category,
              Submission.category_id == Category.id)  # Assuming `Submission.category_id` links to `Category.id`
        .join(SubCategory,
              Submission.sub_category_id == SubCategory.id)  # Assuming `Submission.sub_category_id` links to `SubCategory.id`
        .options(
            joinedload(Submission.user),  # Load user relationship
            joinedload(Submission.category),  # Load category relationship
            joinedload(Submission.subcategory),  # Load sub_category relationship
            joinedload(Submission.user).defer(User.password),
            joinedload(Submission.user).joinedload(User.students),
        )
        .order_by(desc(Submission.id))
        .offset(offset).limit(limit)
        .all()
    )

    # Check if any submissions were found
    if not submissions:
        raise HTTPException(status_code=404, detail="No submissions found ")

    formatted_submissions = [formart_submission(submission, user) for submission in submissions]

    submissions_count = (
        db.query(Submission)
        .filter(Submission.created_by == user_id)
        .join(User, Submission.created_by == User.id)  # Assuming `Submission.created_by` links to `User.id`
        .join(Category,
              Submission.category_id == Category.id)  # Assuming `Submission.category_id` links to `Category.id`
        .join(SubCategory,
              Submission.sub_category_id == SubCategory.id)  # Assuming `Submission.sub_category_id` links to `SubCategory.id`
        .options(
            joinedload(Submission.user),  # Load user relationship
            joinedload(Submission.category),  # Load category relationship
            joinedload(Submission.subcategory),  # Load sub_category relationship
            joinedload(Submission.user).defer(User.password),
            joinedload(Submission.user).joinedload(User.students),
        )
        .count()
    )

    return formatted_submissions, submissions_count


def get_by_sub_category(sub_category_id: int, page: int, limit: int, user: Optional[User] = None):
    offset = (page - 1) * limit

    db: Session = next(get_db())

    submissions = (
        db.query(Submission)
        .filter(Submission.sub_category_id == sub_category_id)
        .join(User, Submission.created_by == User.id)  # Assuming `Submission.created_by` links to `User.id`
        .join(Category,
              Submission.category_id == Category.id)  # Assuming `Submission.category_id` links to `Category.id`
        .join(SubCategory,
              Submission.sub_category_id == SubCategory.id)  # Assuming `Submission.sub_category_id` links to `SubCategory.id`
        .options(
            joinedload(Submission.user),  # Load user relationship
            joinedload(Submission.category),  # Load category relationship
            joinedload(Submission.subcategory),  # Load sub_category relationship
            joinedload(Submission.user).defer(User.password),
            joinedload(Submission.user).joinedload(User.students),
        )
        .order_by(desc(Submission.id))
        .offset(offset).limit(limit)
        .all()
    )

    # Check if any submissions were found
    if not submissions:
        raise HTTPException(status_code=404, detail="No submissions found for this sub-category")

    formatted_submissions = [formart_submission(submission, user) for submission in submissions]

    submissions_count = (
        db.query(Submission)
        .filter(Submission.sub_category_id == sub_category_id)
        .join(User, Submission.created_by == User.id)  # Assuming `Submission.created_by` links to `User.id`
        .join(Category,
              Submission.category_id == Category.id)  # Assuming `Submission.category_id` links to `Category.id`
        .join(SubCategory,
              Submission.sub_category_id == SubCategory.id)  # Assuming `Submission.sub_category_id` links to `SubCategory.id`
        .options(
            joinedload(Submission.user),  # Load user relationship
            joinedload(Submission.category),  # Load category relationship
            joinedload(Submission.subcategory),  # Load sub_category relationship
            joinedload(Submission.user).defer(User.password),
            joinedload(Submission.user).joinedload(User.students),
        )
        .count()
    )

    return formatted_submissions, submissions_count


def get_all_category(page: int, limit: int, user: User,
                     category_id: Optional[int] = None,
                     sub_category_id: Optional[int] = None,
                     submission_id: Optional[int] = None,
                     user_id: Optional[int] = None,
                     school_id: Optional[int] = None,
                     grade_id: Optional[int] = None):
    offset = (page - 1) * limit

    db: Session = next(get_db())

    query = db.query(Submission).join(User, Submission.created_by == User.id) \
        .join(Category, Submission.category_id == Category.id) \
        .join(SubCategory, Submission.sub_category_id == SubCategory.id) \
        .options(
        joinedload(Submission.user),
        joinedload(Submission.category),
        joinedload(Submission.subcategory),
        joinedload(Submission.user).defer(User.password),
        joinedload(Submission.user).joinedload(User.students),
    ) \
        .order_by(desc(Submission.id))

    # **Apply Filters Dynamically**
    if sub_category_id:
        query = query.filter(Submission.sub_category_id == sub_category_id)
    # **Apply Filters Dynamically**
    if category_id:
        query = query.filter(Submission.category_id == category_id)
    if submission_id:
        query = query.filter(Submission.id == submission_id)
    if user_id:
        query = query.filter(Submission.created_by == user_id)

    if school_id or grade_id:
        query = query.join(Student, Student.user_id == User.id)

    if school_id:
        query = query.filter(Student.school_id == school_id)

    if grade_id:
        query = query.filter(Student.grade_id == grade_id)

    # **Pagination**
    submissions = query.offset(offset).limit(limit).all()

    for submission in submissions:
        submission.comments_count = len(submission.comments)

    if not submissions:
        raise HTTPException(status_code=404, detail="No submissions found for the given criteria")

    formatted_submissions = [formart_submission(submission, user) for submission in submissions]

    # **Count Query**
    total = query.count()

    return formatted_submissions, total


def formart_submission(submission, user: Optional[User] = None):
    from app.services.like_service import get_comment_from_submission, get_likes_from_submission, get_is_liked_from_submission_and_user

    if not submission:
        return submission

    if  submission.user and submission.user.image:
        if submission.user.password:
            del submission.user.password
        submission.user.image_url = submission.user.image_path

    submission.media_url = submission.media_path
    if submission.category:
        submission.category.icon_url = submission.category.icon_path

    submission.likes_count = get_likes_from_submission(submission.id)
    submission.comment_counts = get_comment_from_submission(submission.id)

    # Only process likes if the user is provided
    if user:
        submission.is_liked = get_is_liked_from_submission_and_user(submission.id, user.id)

    return submission


def get_comments_by_submission_id(submission_id: int, page: int, limit: int):
    offset = (page - 1) * limit

    db: Session = next(get_db())

    comments = (
        db.query(Comment)
        .filter(Comment.submission_id == submission_id)
        .join(User,
              Comment.user_id == User.id)  # Assuming `Submission.category_id` links to `Category.id`
        .options(
            joinedload(Comment.user).options(defer(User.password)),  # Load user relationship
        )
        .order_by(desc(Comment.id))
        .offset(offset).limit(limit)
        .all()
    )

    # Check if any submissions were found
    if not comments:
        raise HTTPException(status_code=404, detail="No Comments found for this submissions")

    comments_count = (
        db.query(Comment)
        .filter(Comment.submission_id == submission_id)
        .join(User,
              Comment.user_id == User.id)  # Assuming `Submission.category_id` links to `Category.id`
        .options(
            joinedload(Comment.user),  # Load user relationship
        )
        .count()
    )

    # Loop through the submissions and append the media URL
    for comment in comments:
        if comment.user:
            comment.user.image_url = comment.user.image_path

    return comments, comments_count


def get_submission_count_by_school_id(school_id: int):
    db: Session = next(get_db())

    submission_count_by_school = (
        db.query(Submission)
        .filter(Submission.school_id == school_id)
        .count()
    )

    return submission_count_by_school


def get_likes_count_by_school_id(school_id: int):
    db: Session = next(get_db())

    likes_count_by_school = (
        db.query(Like)
        .filter(Like.school_id == school_id)
        .count()
    )

    return likes_count_by_school


def get_avg_points_by_school_id(school_id: int):
    db: Session = next(get_db())

    points_count_by_school = (
        db.query(func.sum(Student.points))
        .filter(Student.school_id == school_id)
        .scalar()
    ) or 0  # Ensure None is treated as 0

    students_count_by_school = (
        db.query(Student)
        .filter(Student.school_id == school_id)
        .count()
    )

    # Avoid division by zero
    if students_count_by_school == 0:
        return 0  # Return 0 when no students exist

    avg_points = round(points_count_by_school / students_count_by_school, 2)
    return avg_points



def get_students_count_by_school_id(school_id: int):
    db: Session = next(get_db())

    student_count_by_school = (
        db.query(Student)
        .filter(Student.school_id == school_id)
        .count()
    )

    return student_count_by_school
