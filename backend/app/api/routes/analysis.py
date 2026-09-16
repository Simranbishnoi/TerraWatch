from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.analysis import Analysis
from app.models.farm import Farm
from app.schemas.analysis import AnalysisCreate, AnalysisResponse

router = APIRouter()


@router.post("/", response_model=AnalysisResponse, status_code=201)
def create_analysis(
    analysis_data: AnalysisCreate,
    db: Session = Depends(get_db)
):
    farm = db.query(Farm).filter(
        Farm.id == analysis_data.farm_id
    ).first()

    if not farm:
        raise HTTPException(
            status_code=404,
            detail="Farm not found"
        )

    analysis = Analysis(**analysis_data.model_dump())

    db.add(analysis)
    db.commit()
    db.refresh(analysis)

    return analysis


@router.get("/", response_model=List[AnalysisResponse])
def get_analyses(
    db: Session = Depends(get_db)
):
    return db.query(Analysis).order_by(
        Analysis.created_at.desc()
    ).all()


@router.get("/{analysis_id}", response_model=AnalysisResponse)
def get_analysis(
    analysis_id: int,
    db: Session = Depends(get_db)
):
    analysis = db.query(Analysis).filter(
        Analysis.id == analysis_id
    ).first()

    if not analysis:
        raise HTTPException(
            status_code=404,
            detail="Analysis not found"
        )

    return analysis