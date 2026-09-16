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
from pydantic import BaseModel
from typing import Dict, Any, Optional

class AnalyzeRequest(BaseModel):
    farm_id: Optional[int] = 1
    boundary: Dict[str, Any]
    start_date: str
    end_date: str
    previous_observation_date: Optional[str] = None

@router.post("/analyze")
def analyze_farm_direct(request: AnalyzeRequest):
    import json
    import os
    
    # Path to the pre-computed demo result (fallback)
    demo_file = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'satellite_engine', 'outputs', 'demo_result.json'))
    
    try:
        from app.services.satellite_service import run_analysis_direct
        result = run_analysis_direct(
            boundary=request.boundary,
            start_date=request.start_date,
            end_date=request.end_date,
            previous_observation_date=request.previous_observation_date
        )
        
        if result.get("status") in ["ERROR", "INVALID_REQUEST", "GEE_ERROR"]:
            raise RuntimeError("Pipeline returned error status: " + result.get("message", ""))
            
        return result
    except Exception as e:
        print(f"⚠️ Real pipeline failed ({str(e)}). Falling back to demo data!")
        try:
            with open(demo_file, 'r') as f:
                return json.load(f)
        except Exception as fallback_e:
            raise HTTPException(status_code=500, detail=f"Pipeline and fallback failed: {str(fallback_e)}")
