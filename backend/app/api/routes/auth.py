import os
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from authlib.integrations.starlette_client import OAuth
from dotenv import load_dotenv

from app.db.database import get_db
from app.models.user import User
from app.schemas.auth import UserCreate, UserOut, UserLogin, Token, GoogleLoginRequest
from app.core.security import get_password_hash, verify_password, create_access_token

load_dotenv()

router = APIRouter()

oauth = OAuth()
oauth.register(
    name="google",
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)


@router.post("/signup", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def signup(user_in: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user_in.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    hashed_pwd = get_password_hash(user_in.password)
    new_user = User(
        email=user_in.email,
        name=user_in.name,
        hashed_password=hashed_pwd,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.post("/login", response_model=Token)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == credentials.email).first()

    if not user or not user.hashed_password or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    if user.is_mfa_enabled:
        return Token(access_token="", token_type="bearer", mfa_required=True)

    access_token = create_access_token(data={"sub": user.email})
    return Token(access_token=access_token, token_type="bearer", mfa_required=False)


@router.post("/auth/google", response_model=Token)
async def google_auth(request_data: GoogleLoginRequest, db: Session = Depends(get_db)):
    try:
        token_payload = {"id_token": request_data.token}
        user_info = await oauth.google.parse_id_token(token_payload, nonce=None)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid Google token: {str(e)}")

    email = user_info.get("email")
    if not email:
        raise HTTPException(status_code=400, detail="Google token missing email")

    google_id = user_info.get("sub")
    user = db.query(User).filter(User.email == email).first()
    if not user:
        user = User(email=email, google_id=google_id)
        db.add(user)
        db.commit()
        db.refresh(user)
    elif google_id and not user.google_id:
        user.google_id = google_id
        db.commit()
        db.refresh(user)

    if user.is_mfa_enabled:
        return Token(access_token="", token_type="bearer", mfa_required=True)

    access_token = create_access_token(data={"sub": user.email})
    return Token(access_token=access_token, token_type="bearer", mfa_required=False)
