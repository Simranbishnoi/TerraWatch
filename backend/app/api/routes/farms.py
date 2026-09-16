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


@router.get("/", response_model=List[FarmResponse])
def get_farms(
    db: Session = Depends(get_db)
):
    return db.query(Farm).order_by(Farm.created_at.desc()).all()


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