import os
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from authlib.integrations.starlette_client import OAuth

load_dotenv()

import models
import schemas
from database import engine, get_db
from security import get_password_hash, verify_password, create_access_token

# Automatically create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="TerraWatch API",
    description="Backend API service for the TerraWatch hackathon project",
    version="1.0.0",
)

# CORS middleware configuration
origins = [
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OAuth setup
oauth = OAuth()
oauth.register(
    name="google",
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok"}


@app.post("/signup", response_model=schemas.UserOut, status_code=status.HTTP_201_CREATED, tags=["Authentication"])
def signup(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    # Check if a user with the given email already exists
    existing_user = db.query(models.User).filter(models.User.email == user_in.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Hash the password and create the user
    hashed_pwd = get_password_hash(user_in.password)
    new_user = models.User(
        email=user_in.email,
        hashed_password=hashed_pwd,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@app.post("/login", response_model=schemas.Token, tags=["Authentication"])
def login(credentials: schemas.UserLogin, db: Session = Depends(get_db)):
    # Look up user by email
    user = db.query(models.User).filter(models.User.email == credentials.email).first()

    # Validate user existence and password
    if not user or not user.hashed_password or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    # MFA handling
    if user.is_mfa_enabled:
        return schemas.Token(
            access_token="",
            token_type="bearer",
            mfa_required=True,
        )

    # Generate full access token if MFA is not enabled
    access_token = create_access_token(data={"sub": user.email})
    return schemas.Token(
        access_token=access_token,
        token_type="bearer",
        mfa_required=False,
    )


@app.post("/auth/google", response_model=schemas.Token, tags=["Authentication"])
async def google_auth(request_data: schemas.GoogleLoginRequest, db: Session = Depends(get_db)):
    try:
        token_payload = {"id_token": request_data.token}
        user_info = await oauth.google.parse_id_token(token_payload, nonce=None)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid Google token: {str(e)}",
        )

    email = user_info.get("email")
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Google token missing email",
        )

    google_id = user_info.get("sub")

    # Check if a user with this email exists in the database
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        # Create a new user record with email and google_id, but no password
        user = models.User(
            email=email,
            google_id=google_id,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    elif google_id and not user.google_id:
        user.google_id = google_id
        db.commit()
        db.refresh(user)

    # MFA handling
    if user.is_mfa_enabled:
        return schemas.Token(
            access_token="",
            token_type="bearer",
            mfa_required=True,
        )

    # Create a JWT access token for this user
    access_token = create_access_token(data={"sub": user.email})
    return schemas.Token(
        access_token=access_token,
        token_type="bearer",
        mfa_required=False,
    )
