import logging
import time

import httpx
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr, validator
from sqlalchemy import select
from sqlalchemy.orm import Session

from d4_auth_svc.config import EMAIL_SERVICE_URL, EMAIL_API_KEY
from d4_auth_svc.models.base import get_db
from d4_auth_svc.models.user import User

router = APIRouter()

class UserRegistrationPayload(BaseModel):
    email: EmailStr
    full_name: str
    password: str

    @validator('password')
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(ch.isupper() for ch in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(ch.islower() for ch in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(ch.isdigit() for ch in v):
            raise ValueError('Password must contain at least one number')
        return v


def send_welcome_email(email: str, full_name: str) -> None:
    try:
        # Build email payload
        payload = {
            "recipient": email,
            "full_name": full_name,
            "subject": "Welcome to Our Platform",
            "message": f"Dear {full_name}, welcome to our platform!"
        }
        headers = {
            "Authorization": f"Bearer {EMAIL_API_KEY}",
            "Content-Type": "application/json"
        }

        # Ensure EMAIL_SERVICE_URL is set and uses HTTPS
        if not EMAIL_SERVICE_URL or not EMAIL_SERVICE_URL.startswith("https://"):
            logging.error("EMAIL_SERVICE_URL is not properly configured with HTTPS.")
            return

        # Retry mechanism: try up to 3 times
        for attempt in range(3):
            try:
                response = httpx.post(EMAIL_SERVICE_URL, json=payload, headers=headers, timeout=10.0)
                if response.status_code == 200:
                    return
                else:
                    logging.error(f"Email service responded with status code {response.status_code} on attempt {attempt + 1} of 3")
            except Exception as e:
                logging.error(e, exc_info=True)
            time.sleep(1)
        logging.error(f"Failed to send welcome email to {email} after 3 attempts.")
    except Exception as e:
        logging.error(e, exc_info=True)


@router.post("/register")

def register_user(payload: UserRegistrationPayload, db: Session = Depends(get_db)):
    try:
        # Check for existing user using SQLAlchemy 2.0 style query
        result = db.execute(select(User).where(User.email == payload.email))
        existing_user = result.scalars().first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")
    except HTTPException:
        raise
    except Exception as e:
        logging.error(e, exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")

    # Hash the password using bcrypt
    try:
        import bcrypt
        hashed_password = bcrypt.hashpw(payload.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    except Exception as e:
        logging.error(e, exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")

    # Create and persist the new user
    try:
        new_user = User(email=payload.email, full_name=payload.full_name, hashed_password=hashed_password)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except Exception as e:
        logging.error(e, exc_info=True)
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal Server Error")

    # Trigger email integration
    send_welcome_email(payload.email, payload.full_name)

    return {"message": "User registered successfully"}
