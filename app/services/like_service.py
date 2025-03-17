from typing import Type

from sqlalchemy import desc, func
from sqlalchemy.orm import Session, joinedload

from app.config.settings import settings
from app.database.connection import get_db
from app.models import Submission, UserPoint, Comment
from app.models.model_likes import Like
from app.models.user import User
from app.routes.pre_auth_routes import get_user_student
from app.services.school_service import update_rank_by_school_id
from app.services.user import get_user_by_id, get_user_submission_like_count

from sqlalchemy.orm import Session
from fastapi import HTTPException


def toggle_like(user: User, submission_id: int):
    db: Session = next(get_db())

    submission = db.query(Submission).filter(Submission.id == submission_id).first()

    if not submission:
        raise HTTPException(status_code=401, detail="Invalid submission")

    try:
        # Check if the like already exists
        existing_like = (
            db.query(Like)
            .filter(Like.user_id == user.id, Like.submission_id == submission_id)
            .first()
        )

        if existing_like:
            # Fetch and remove points associated with the like
            existing_points = (
                db.query(UserPoint)
                .filter(
                    UserPoint.like_user_id == existing_like.user_id,
                    UserPoint.submission_id == existing_like.submission_id,
                    UserPoint.point_type == 2
                )
                .all()
            )

            if existing_points:
                for point in existing_points:
                    db.delete(point)  # Delete each matching record
                db.flush()

            # Remove the like
            db.delete(existing_like)
            db.flush()
            db.commit()
            # Update the user's likes count

            # return update_likes_to_user(submission.created_by)
            likes_count =update_likes_to_user(submission.created_by)


            return {'action': 'unliked', 'liked': False, 'likes':likes_count}

        # Fetch the student profile associated with the user
        student = get_user_student(db, user.id)
        if not student:
            raise HTTPException(status_code=404, detail="Student profile not found")

        # Add a new like
        like_item = Like(
            user_id=user.id,
            submission_id=submission_id,
            likes=1,
            like_type=1,
            school_id=student.school_id,
        )
        db.add(like_item)
        db.flush()

        # Check if points already exist for this user and submission
        existing_points = (
            db.query(UserPoint)
            .filter(
                UserPoint.like_user_id == like_item.user_id,
                UserPoint.submission_id == like_item.submission_id,
                UserPoint.point_type == 2
            )
            .first()
        )

        # If points do not exist, add them
        if existing_points is None:
            user_point = UserPoint(
                like_user_id=like_item.user_id,
                user_id=submission.created_by,
                grade_id=student.grade_id,  # Grade ID of the student
                school_id=student.school_id,  # School ID of the student
                submission_id=like_item.submission_id,  # Submission ID
                points=settings.POINTS_BY_LIKE,  # Points to add
                point_type=2  # Point type (2 represents like points)
            )
            db.add(user_point)
            db.flush()

        db.commit()
        # Update the user's likes count
        # return update_likes_to_user(submission.created_by)
        likes_count = update_likes_to_user(submission.created_by)


        return {'action': 'liked', 'liked': True, 'likes': likes_count}

    except Exception as e:
        db.rollback()
        raise e

    finally:
        db.close()


def update_likes_to_user(user_id: int):
    db: Session = next(get_db())

    try:
        # Fetch the logged-in user from the database
        user = db.query(User).filter(User.id == user_id).first()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Fetch the student profile associated with the user
        student = get_user_student(db, user.id)


        if not student:
            raise HTTPException(status_code=404, detail="Student profile not found")


        # Count the number of likes associated with the user
        # existing_like_count_by_user = (
        #     db.query(func.sum(Like.likes))
        #     .filter(Like.user_id == user.id)
        #     .scalar()
        # )

        existing_like_count_by_user = get_user_submission_like_count(user.id)

        likes_count =existing_like_count_by_user or 0
        # Update the student's likes count
        student.likes = likes_count

        # Save changes to the database
        db.add(student)

        db.flush()
        db.commit()

        update_rank_by_school_id(student.school_id)

        update_points_to_user(student.user_id)

        return likes_count

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

    finally:
        db.close()


def update_points_to_user(user_id: int):
    db: Session = next(get_db())

    # return user_id

    try:
        # Fetch the user from the database
        user = get_user_by_id(user_id)

        # return user['id']

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Fetch the student profile associated with the user
        student = get_user_student(db, user['id'])
        if not student:
            raise HTTPException(status_code=404, detail="Student profile not found")

        # Sum up the points for the user
        existing_points_sum_by_user = (
            db.query(func.sum(UserPoint.points))
            .filter(UserPoint.user_id == user['id'])
            .scalar()
        )

        # Update student's total points
        student.points = existing_points_sum_by_user or 0  # Default to 0 if no points found

        # Commit the changes to the database
        db.add(student)
        db.flush()

        db.commit()
        return student

    except Exception as e:
        db.rollback()
        raise e

    finally:
        db.close()


def get_likes_from_submission(submission_id: int):
    db: Session = next(get_db())

    # Count the number of likes for the given submission
    existing_like_count_by_submission = (
        db.query(Like)
        .filter(Like.submission_id == submission_id)
        .count()
    )

    return existing_like_count_by_submission
def get_comment_from_submission(submission_id: int):
    db: Session = next(get_db())

    # Count the number of likes for the given submission
    existing_comment_count_by_submission = (
        db.query(Comment)
        .filter(Comment.submission_id == submission_id)
        .count()
    )

    return existing_comment_count_by_submission


def get_is_liked_from_submission_and_user(submission_id: int, user_id: int):
    db: Session = next(get_db())

    # Check if the user has liked the submission
    existing_like_by_user = (
        db.query(Like)
        .filter(Like.submission_id == submission_id, Like.user_id == user_id)
        .first()  # Use first() to check existence
    )

    return existing_like_by_user is not None  # True if exists, False if not
