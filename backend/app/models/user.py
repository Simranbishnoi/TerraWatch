from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func

from app.db.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    role = Column(String(50), default="farmer")
    
    # Auth fields from Saaras's backend
    hashed_password = Column(String(255), nullable=True)
    google_id = Column(String(255), unique=True, index=True, nullable=True)
    mfa_secret = Column(String(255), nullable=True)
    is_mfa_enabled = Column(Boolean, default=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
