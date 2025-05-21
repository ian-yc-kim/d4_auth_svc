import datetime
import logging
from fastapi import APIRouter, Depends, Request, HTTPException, status
from sqlalchemy.orm import Session

from d4_auth_svc.models.token_blacklist import TokenBlacklist
from d4_auth_svc.models.base import get_db

router = APIRouter()

@router.post("/logout")
def logout(request: Request, db: Session = Depends(get_db)):
    # Extract Authorization header
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=400, detail="Missing or malformed Authorization header")
    
    token = auth_header.split(" ")[1]
    
    try:
        # Check if token is already blacklisted
        existing_token = db.get(TokenBlacklist, token)
        if existing_token:
            raise HTTPException(status_code=401, detail="Token already invalidated")

        # Compute expiration timestamp (default TTL: 1 hour from now)
        expires_at = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        new_blacklist_entry = TokenBlacklist(token=token, expires_at=expires_at)
        
        db.add(new_blacklist_entry)
        db.commit()
        
        return {"message": "Logout successful, token invalidated."}
    except HTTPException as he:
        raise he
    except Exception as e:
        logging.error(e, exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
