from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models import CategoryType, Role, Category
from app.models.user import User, UserResponse, LoginRequest
from app.auth import verify_password, create_access_token
from app.models.token import Token  # Correct import for the Token model
from app.services.auth import get_current_user
from app.services.masters import get_all_countries, get_all_states, get_all_grades, get_all_schools
from app.services.user import get_user_by_email, get_user_by_id
from fastapi.openapi.utils import get_openapi

router = APIRouter()




@router.get("/all")
def masters(db: Session = Depends(get_db)):
    countries = get_all_countries(db)
    states = get_all_states(db)
    grades = get_all_grades(db)
    schools = get_all_schools(db)

    return {
        'countries': jsonable_encoder(countries),
        'states': jsonable_encoder(states),
        'grades': jsonable_encoder(grades),
        'schools': jsonable_encoder(schools),
    }
