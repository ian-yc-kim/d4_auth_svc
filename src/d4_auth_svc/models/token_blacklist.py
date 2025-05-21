from sqlalchemy import Column, String, TIMESTAMP
from d4_auth_svc.models.base import Base

class TokenBlacklist(Base):
    __tablename__ = 'token_blacklist'

    token = Column(String, primary_key=True, nullable=False)
    expires_at = Column(TIMESTAMP, nullable=False)

    def __repr__(self) -> str:
        return f"<TokenBlacklist(token={self.token}, expires_at={self.expires_at})>"