import secrets
import string
from datetime import datetime, timedelta
from email.message import EmailMessage
from random import random

import aiosmtplib
from fastapi_mail import MessageSchema, FastMail, ConnectionConfig
from jinja2 import Environment, FileSystemLoader
from jose import jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr

from app.config.settings import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

BASE_URL = f"{settings.APP_URL}/static"
SUBMISSIONS_MEDIA_FOLDER = f"{BASE_URL}/media/submissions/"
USER_PROFILES_MEDIA_FOLDER = f"{BASE_URL}/media/user_profile_images/"
CATEGORY_MEDIA_FOLDER = f"{BASE_URL}/media/category_images/"



# Utility to generate a random token
def generate_reset_token():
    return secrets.token_urlsafe(32)

# Pydantic models
class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

# Utility: Send email via SMTP
# async def send_email(to_email: str, subject: str, body: str):
#     msg = EmailMessage()
#     msg["From"] = settings.SENDER_EMAIL
#     msg["To"] = to_email
#     msg["Subject"] = subject
#     msg.set_content(body)
#
#     try:
#         async with aiosmtplib.SMTP(hostname=settings.SMTP_SERVER, port=settings.SMTP_PORT, start_tls=True) as smtp:
#             await smtp.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
#             await smtp.send_message(msg)
#     except Exception as e:
#         print(f"Error sending email: {e}")


env = Environment(loader=FileSystemLoader("templates"))

def render_template(template_name: str, context: dict):
    template = env.get_template(template_name)
    return template.render(context)

async def send_email(to_email: str, subject: str, body:str, reset_link: str):
    msg = EmailMessage()
    msg["From"] = settings.SENDER_EMAIL
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(body, subtype="html")

    # Render the HTML template with reset_link
    html_content = render_template("email/reset_password.html", {"reset_link": reset_link})

    # Set email content
    msg.set_content("This is a password reset email.")  # Plain text fallback
    msg.add_alternative(html_content, subtype="html")  # HTML content

    try:
        async with aiosmtplib.SMTP(hostname=settings.SMTP_SERVER, port=settings.SMTP_PORT, start_tls=True) as smtp:
            await smtp.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            await smtp.send_message(msg)
    except Exception as e:
        print(f"Error sending email: {e}")




async def send_verification_email(email: str, token: str):
    msg = EmailMessage()
    msg["From"] = settings.SENDER_EMAIL
    msg["To"] = email
    msg["Subject"] = "Verification Email"
    msg.set_content('', subtype="html")

    verify_url = f"{settings.APP_URL}/verify-email?token={token}"

    # Render the HTML template with reset_link
    html_content = render_template("email/verify_account.html", {"verify_url": verify_url})

    # Set email content
    msg.set_content("This is a verify email.")  # Plain text fallback
    msg.add_alternative(html_content, subtype="html")  # HTML content

    try:
        async with aiosmtplib.SMTP(hostname=settings.SMTP_SERVER, port=settings.SMTP_PORT, start_tls=True) as smtp:
            await smtp.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            await smtp.send_message(msg)
    except Exception as e:
        print(f"Error sending email: {e}")
    # """Send email verification link."""
    # verify_url = f"{settings.APP_URL}/verify-email?token={token}"
    # message = MessageSchema(
    #     subject="Email Verification",
    #     recipients=[email],
    #     body=f"Click the link to verify your email: {verify_url}",
    #     subtype="html",
    # )
    #
    # fm = FastMail(conf)
    # return fm.send_message(message)

def generate_verification_token(email: str):
    """Generate a JWT token for email verification."""
    payload = {
        "sub": email,
        "exp": datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


