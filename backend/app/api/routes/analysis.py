"""
analysis.py — TerraWatch Analysis Routes
Connects frontend directly to Greeshma's satellite engine.
"""
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.database import get_db
from app.models.analysis import Analysis
from app.models.farm import Farm
from app.models.user import User
from app.schemas.analysis import AnalysisCreate, AnalysisResponse, SatelliteAnalysisTrigger
from app.services.satellite_service import run_analysis_direct, run_analysis_for_farm

router = APIRouter()


# ── Schema for direct boundary analysis (what frontend sends) ─────────────────

class DirectAnalysisRequest(BaseModel):
    """
    Frontend sends this directly — no need to create a farm first.
    Matches the dashboard 'Analyze' button flow.
    """
    boundary: Dict[str, Any]          # GeoJSON Polygon
    start_date: str = "2023-01-01"    # YYYY-MM-DD
    end_date: str = "2024-01-01"      # YYYY-MM-DD
    farm_name: Optional[str] = "Ad-hoc Analysis"
    previous_observation_date: Optional[str] = None


# ── Direct analysis endpoint (frontend primary entry point) ───────────────────

@router.post("/analyze")
def analyze_boundary(
    body: DirectAnalysisRequest,
    db: Session = Depends(get_db),
):
    """
    POST /api/analysis/analyze
    Frontend sends boundary + dates → returns full satellite analysis result.
    This is what the 'Analyze' button on the map calls.
    """
    try:
        result = run_analysis_direct(
            boundary=body.boundary,
            start_date=body.start_date,
            end_date=body.end_date,
            previous_observation_date=body.previous_observation_date,
        )
        return result
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Satellite analysis error: {exc}")


# ── Farm-based trigger endpoint (Simran's backend internal use) ───────────────

@router.post("/trigger/{farm_id}")
def trigger_satellite_analysis(
    farm_id: int,
    body: SatelliteAnalysisTrigger = None,
    db: Session = Depends(get_db),
):
    """
    POST /api/analysis/trigger/{farm_id}
    Triggers analysis for a saved farm. Saves result to DB.
    """
    try:
        result = run_analysis_for_farm(
            db=db,
            farm_id=farm_id,
            start_date=body.start_date if body else None,
            end_date=body.end_date if body else None,
        )
        return result
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Satellite analysis error: {exc}")


# ── Standard CRUD ─────────────────────────────────────────────────────────────

@router.post(
    "/",
    response_model=AnalysisResponse,
    status_code=201
)
def create_analysis(
    analysis_data: AnalysisCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    farm = db.query(Farm).filter(Farm.id == analysis_data.farm_id).first()
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")
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
        raise HTTPException(status_code=404, detail="Analysis not found")
    return analysis