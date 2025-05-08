import os
from datetime import datetime
from http.client import HTTPException

import fastapi
from fastapi import FastAPI, Request, Depends
from jose import jwt
from sqlalchemy.orm import Session
from starlette.responses import HTMLResponse
from starlette.templating import Jinja2Templates

from app.config.settings import settings
from app.database.connection import get_db
from app.models import User
from app.routes import auth_routes, user_routes, swagger_routes, student_routes, categories_routes, masters_routes, \
    pre_auth_routes, submissions_routes, school_routes, quiz_routes, quiz_questions_routes, \
    quiz_question_options_routes, student_answer_routes
from fastapi.openapi.utils import get_openapi
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from fastapi.staticfiles import StaticFiles

from app.utils.common import ResetPasswordRequest, hash_password

os.makedirs("static/media/images", exist_ok=True)
os.makedirs("static/media/videos", exist_ok=True)
os.makedirs("static/media/audios", exist_ok=True)
os.makedirs("static/media/user_profile_images", exist_ok=True)
os.makedirs("static/media/category_images", exist_ok=True)
app = FastAPI()

app.mount("/static/media/images", StaticFiles(directory="static/media/images"), name="images")
app.mount("/static/media/videos", StaticFiles(directory="static/media/videos"), name="videos")
app.mount("/static/media/audios", StaticFiles(directory="static/media/audios"), name="audios")
app.mount("/static/media/user_profile_images", StaticFiles(directory="static/media/user_profile_images"), name="user_profile_images")
app.mount("/static/media/category_images", StaticFiles(directory="static/media/category_images"), name="category_images")
app.mount("/static/media/submissions", StaticFiles(directory="static/media/submissions"), name="submissions")


templates = Jinja2Templates(directory="templates")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update with specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="FastAPI Authentication MSB",
        version="1.0.1",
        description="An MSB FastAPI app with authentication and Swagger integration.",
        routes=app.routes,
    )

    # Define OAuth2 flow
    openapi_schema['components']['securitySchemes'] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }

    # Apply BearerAuth globally to all routes
    for path in openapi_schema["paths"]:
        for method in openapi_schema["paths"][path]:
            openapi_schema["paths"][path][method]["security"] = [{"BearerAuth": []}]

    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi


# Include routes
app.include_router(masters_routes.router, prefix="/masters", tags=["Masters"])
app.include_router(pre_auth_routes.router, prefix="/pre", tags=["PreAuth"])
app.include_router(auth_routes.router, prefix="/auth", tags=["Auth"])
app.include_router(user_routes.router, prefix="/users", tags=["Users"])
app.include_router(student_routes.router, prefix="/student", tags=["Students"])
app.include_router(categories_routes.router, prefix="/category", tags=["Category"])
app.include_router(submissions_routes.router, prefix="/submission", tags=["Submissions"])
app.include_router(school_routes.router, prefix="/school", tags=["School"])
app.include_router(quiz_routes.router, prefix="/quiz", tags=["Quiz"])
app.include_router(quiz_questions_routes.router, prefix="/quiz_questions", tags=["QuizQuestions"])
app.include_router(quiz_question_options_routes.router, prefix="/quiz_question_options", tags=["QuizQuestionsOptions"])
app.include_router(student_answer_routes.router, prefix="/student_answer", tags=["QuizStudentAnswer"])

app.include_router(swagger_routes.router)


# The root endpoint that renders the landing page with dynamic data
@app.get("/", response_class=HTMLResponse)
async def read_landing_page(request: Request):
    # Example dynamic data to send to the template
    context = {
        "request": request,  # required by Jinja2 template renderer
        "greeting": "Hello, Welcome to MSB API'S!",
    }
    return templates.TemplateResponse("index.html", context)

@app.get("/force-update")
def force_update():
    # Rebuild OpenAPI schema manually
    app.openapi_schema = get_openapi(
        title="FastAPI Authentication MSB",
        version="1.0.1",
        description="An MSB FastAPI app with authentication and Swagger integration.",
        routes=app.routes,
    )
    return {"message": "OpenAPI schema updated!"}



@app.get("/reset-password", response_class=HTMLResponse, include_in_schema=False)
async def reset_password_page(request: Request, token: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.reset_token == token).first()

    if not user or user.token_expiry < datetime.utcnow():
        return HTMLResponse("<h3>Invalid or expired token</h3>", status_code=400)

    return templates.TemplateResponse("reset_password.html", {"request": request, "token": token})



# Reset Password API
@app.post("/reset-password")
async def reset_password(request: ResetPasswordRequest):
    token = request.token
    new_password = request.new_password

    db: Session = next(get_db())

    user = db.query(User).filter(User.reset_token == token).first()
    # Find user with the given reset token
    # user = next((u for u in users_db.values() if u["reset_token"] == token), None)

    if not user or user.token_expiry < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    # Hash and update new password
    user.password = hash_password(new_password)
    user.reset_token = None  # Invalidate the token

    db.add(user)
    db.commit()
    db.refresh(user)

    return {"message": "Password has been reset successfully"}

@app.get("/verify-email")
def verify_email(token: str, db: Session = Depends(get_db)):
    """Verify email using the token."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email = payload.get("sub")

        if email is None:
            raise HTTPException(status_code=400, detail="Invalid token.")

        user = db.query(User).filter(User.email == email).first()

        if not user:
            raise HTTPException(status_code=404, detail="User not found.")

        if user.is_verified:
            return {"message": "Email is already verified."}

        # Update the user verification status
        user.is_verified = True
        db.commit()

        return {"message": "Email verified successfully."}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=400, detail="Verification token expired.")
    except jwt.JWTError:
        raise HTTPException(status_code=400, detail="Invalid token.")






if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)