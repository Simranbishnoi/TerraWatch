from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.auth import SignupRequest
from app.core.security import hash_password, verify_password


def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email.lower()).first()


def create_user(db: Session, signup_data: SignupRequest):
    existing_user = get_user_by_email(db, signup_data.email)

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already registered"
        )

    user = User(
        name=signup_data.name,
        email=signup_data.email.lower(),
        hashed_password=hash_password(signup_data.password),
        role="farmer"
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def authenticate_user(
    db: Session,
    email: str,
    password: str
):
    user = get_user_by_email(db, email)

    if not user:
        return None

    if not verify_password(password, user.hashed_password):
        return None

    return user