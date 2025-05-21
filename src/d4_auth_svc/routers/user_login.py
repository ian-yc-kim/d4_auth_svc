import logging
import secrets
import bcrypt

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.future import select
from sqlalchemy.orm import Session

from d4_auth_svc.models.user import User
from d4_auth_svc.models.base import get_db

router = APIRouter()

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

@router.post("/login")
async def login(login_req: LoginRequest, db: Session = Depends(get_db)):
    try:
        # Query the user by email using SQLAlchemy 2.0 style
        query = select(User).filter_by(email=login_req.email)
        result = db.execute(query)
        user = result.scalars().first()
    except Exception as e:
        logging.error(e, exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    try:
        valid = bcrypt.checkpw(login_req.password.encode('utf-8'), user.hashed_password.encode('utf-8'))
    except Exception as e:
        logging.error(e, exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

    if not valid:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = secrets.token_hex(16)
    return {"access_token": token}
