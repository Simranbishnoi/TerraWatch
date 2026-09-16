from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.auth import (
    SignupRequest,
    LoginRequest,
    UserResponse,
    TokenResponse
)
from app.services.auth_service import (
    create_user,
    authenticate_user
)
from app.core.security import create_access_token
from app.core.config import settings


router = APIRouter()


@router.post(
    "/signup",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
def signup(
    signup_data: SignupRequest,
    db: Session = Depends(get_db)
):
    return create_user(db, signup_data)


@router.post(
    "/login",
    response_model=TokenResponse
)
def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    user = authenticate_user(
        db,
        login_data.email,
        login_data.password
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    access_token_expires = timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    access_token = create_access_token(
        data={
            "sub": str(user.id),
            "email": user.email,
            "role": user.role
        },
        expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }