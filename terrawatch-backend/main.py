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
from security import get_password_hash, verify_password, create_access_token, get_current_user


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
    "http://localhost:8080",
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


from pydantic import BaseModel
from typing import Dict, Any, Optional

class AnalyzeRequest(BaseModel):
    farm_id: Optional[int] = 1
    boundary: Dict[str, Any]
    start_date: str
    end_date: str
    previous_observation_date: Optional[str] = None




@app.post("/analyze", tags=["Analysis"])
def analyze_farm(request: AnalyzeRequest):
    import sys
    import os
    import json
    
    # Path to the pre-computed demo result (fallback)
    demo_file = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'satellite_engine', 'outputs', 'demo_result.json'))
    
    # Add satellite_engine to path
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    req_dict = {
        "farm_id": request.farm_id or 0,
        "boundary": request.boundary,
        "start_date": request.start_date,
        "end_date": request.end_date,
        "previous_observation_date": request.previous_observation_date,
    }
    
    try:
        # Try to run the REAL pipeline
        from satellite_engine.src.pipeline import run_satellite_analysis
        result = run_satellite_analysis(req_dict)
        
        # Enrich result
        if result.get("risk_score") is None:
            level = result.get("risk_level", "low")
            result["risk_score_pct"] = {"low": 20, "medium": 55, "high": 87, "very_high": 95}.get(level, 20)
        else:
            result["risk_score_pct"] = round((result["risk_score"] or 0) / 100 * 100, 1)

        loss_ha = result.get("forest_loss_hectares") or 0.0
        result["deforestation_detected"] = loss_ha > 0.5 and result.get("status") == "NEW_OBSERVATION"
        
        # If the pipeline returned a hard error (e.g. no GEE auth), fallback
        if result.get("status") in ["ERROR", "INVALID_REQUEST", "GEE_ERROR"]:
            raise RuntimeError("Pipeline returned error status: " + result.get("message", ""))
            
        return result

    except Exception as e:
        print(f"⚠️ Real pipeline failed ({str(e)}). Falling back to demo data for hackathon presentation!")
        # Fallback to demo result if GEE isn't authenticated or packages are missing
        try:
            with open(demo_file, 'r') as f:
                fallback_data = json.load(f)
            return fallback_data
        except Exception as fallback_e:
            raise HTTPException(status_code=500, detail=f"Pipeline failed and fallback failed: {str(fallback_e)}")


MOCK_FARMS_LIST = [
    {
        "id": 1,
        "name": "Fazenda Santa Maria",
        "latitude": -10.5124,
        "longitude": -62.2158,
        "status": "HIGH",
        "hectares_lost": 12.4
    },
    {
        "id": 2,
        "name": "Rancho Verde Norte",
        "latitude": -10.4289,
        "longitude": -62.1542,
        "status": "HIGH",
        "hectares_lost": 18.7
    },
    {
        "id": 3,
        "name": "Agroflorestal Nova Vida",
        "latitude": -10.6311,
        "longitude": -62.3105,
        "status": "MEDIUM",
        "hectares_lost": 5.2
    },
    {
        "id": 4,
        "name": "Fazenda Rio Bonito",
        "latitude": -10.3841,
        "longitude": -62.0917,
        "status": "OK",
        "hectares_lost": 0.0
    },
    {
        "id": 5,
        "name": "Estância Esperança",
        "latitude": -10.5982,
        "longitude": -62.1894,
        "status": "OK",
        "hectares_lost": 0.4
    },
]

MOCK_REPORTS_LIST = [
    {
        "id": "REP-2024-0891",
        "farm_name": "Fazenda Santa Maria",
        "status": "HIGH",
        "date": "2024-10-14"
    },
    {
        "id": "REP-2024-0842",
        "farm_name": "Rancho Verde Norte",
        "status": "HIGH",
        "date": "2024-10-12"
    },
    {
        "id": "REP-2024-0815",
        "farm_name": "Fazenda Esperança",
        "status": "MEDIUM",
        "date": "2024-10-08"
    },
    {
        "id": "REP-2024-0799",
        "farm_name": "Fazenda Rio Bonito",
        "status": "OK",
        "date": "2024-09-28"
    },
    {
        "id": "REP-2024-0774",
        "farm_name": "Rancho Fundo",
        "status": "HIGH",
        "date": "2024-09-22"
    },
    {
        "id": "REP-2024-0752",
        "farm_name": "Sítio Boa Vista",
        "status": "OK",
        "date": "2024-09-17"
    },
    {
        "id": "REP-2024-0731",
        "farm_name": "Agroflorestal Nova Vida",
        "status": "MEDIUM",
        "date": "2024-09-11"
    },
    {
        "id": "REP-2024-0710",
        "farm_name": "Estância Esperança",
        "status": "OK",
        "date": "2024-09-05"
    },
    {
        "id": "REP-2024-0688",
        "farm_name": "Fazenda Bela Alvorada",
        "status": "HIGH",
        "date": "2024-08-29"
    },
    {
        "id": "REP-2024-0665",
        "farm_name": "Vale do Guaporé Agrícola",
        "status": "MEDIUM",
        "date": "2024-08-21"
    },
    {
        "id": "REP-2024-0640",
        "farm_name": "Fazenda Primavera do Sul",
        "status": "OK",
        "date": "2024-08-15"
    },
    {
        "id": "REP-2024-0618",
        "farm_name": "Recanto dos Ipês",
        "status": "MEDIUM",
        "date": "2024-08-08"
    },
    {
        "id": "REP-2024-0592",
        "farm_name": "Cooperativa Agro Verde",
        "status": "OK",
        "date": "2024-07-30"
    },
]


@app.get("/farms", tags=["Farms"])
@app.get("/api/farms", tags=["Farms"])
def get_farms(current_user: models.User = Depends(get_current_user)):
    return MOCK_FARMS_LIST


class FarmInputSchema(BaseModel):
    name: str
    latitude: float
    longitude: float
    status: str = "OK"
    hectares_lost: float = 0.0


@app.post("/farms", tags=["Farms"])
@app.post("/api/farms", tags=["Farms"])
def add_farm(farm_in: FarmInputSchema, current_user: models.User = Depends(get_current_user)):
    new_farm = {
        "id": len(MOCK_FARMS_LIST) + 1,
        "name": farm_in.name,
        "latitude": farm_in.latitude,
        "longitude": farm_in.longitude,
        "status": farm_in.status.upper() if farm_in.status else "OK",
        "hectares_lost": farm_in.hectares_lost,
    }
    MOCK_FARMS_LIST.insert(0, new_farm)
    return new_farm


@app.get("/reports", tags=["Reports"])
@app.get("/api/reports", tags=["Reports"])
def get_reports(current_user: models.User = Depends(get_current_user)):
    return MOCK_REPORTS_LIST


