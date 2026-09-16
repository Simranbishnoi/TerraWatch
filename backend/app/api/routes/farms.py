from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.farm import Farm
from app.schemas.farm import FarmCreate, FarmResponse

router = APIRouter()


@router.post("/", response_model=FarmResponse, status_code=201)
def create_farm(
    farm_data: FarmCreate,
    db: Session = Depends(get_db)
):
    farm = Farm(**farm_data.model_dump())

    db.add(farm)
    db.commit()
    db.refresh(farm)

    return farm


from app.core.security import get_current_user
from app.models.user import User

MOCK_FARMS_DATA = [
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


from pydantic import BaseModel
from typing import Optional

class FarmInput(BaseModel):
    name: str
    latitude: float
    longitude: float
    status: str = "OK"
    hectares_lost: float = 0.0


@router.get("/")
def get_farms(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return MOCK_FARMS_DATA


@router.post("/")
def add_farm(
    farm_in: FarmInput,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    new_farm = {
        "id": len(MOCK_FARMS_DATA) + 1,
        "name": farm_in.name,
        "latitude": farm_in.latitude,
        "longitude": farm_in.longitude,
        "status": farm_in.status.upper() if farm_in.status else "OK",
        "hectares_lost": farm_in.hectares_lost,
    }
    # Add to in-memory list for live demo session
    MOCK_FARMS_DATA.insert(0, new_farm)
    return new_farm




@router.get("/{farm_id}", response_model=FarmResponse)
def get_farm(
    farm_id: int,
    db: Session = Depends(get_db)
):
    farm = db.query(Farm).filter(Farm.id == farm_id).first()

    if not farm:
        raise HTTPException(
            status_code=404,
            detail="Farm not found"
        )

    return farm


@router.delete("/{farm_id}", status_code=204)
def delete_farm(
    farm_id: int,
    db: Session = Depends(get_db)
):
    farm = db.query(Farm).filter(Farm.id == farm_id).first()

    if not farm:
        raise HTTPException(
            status_code=404,
            detail="Farm not found"
        )

    db.delete(farm)
    db.commit()

    return None