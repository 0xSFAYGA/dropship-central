from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import BaseModel

class User(BaseModel):
    """
    Represents a user in the system.
    """
    __tablename__ = "users"

    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    tier = Column(String, default="free", nullable=False) # free, pro, enterprise
    api_key = Column(String, unique=True, index=True, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    sessions = relationship("Session", back_populates="user", cascade="all, delete-orphan")

class Session(BaseModel):
    """
    Represents a user session (e.g., for JWT tokens).
    """
    __tablename__ = "sessions"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    token = Column(String, index=True, nullable=False) # JWT token
    refresh_token = Column(String, index=True, nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    revoked_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", back_populates="sessions")
