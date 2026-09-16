from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class SatelliteAnalysisTrigger(BaseModel):
    """Optional body for POST /api/analysis/trigger/{farm_id}."""
    start_date: Optional[str] = None   # "YYYY-MM-DD", defaults to 1 year ago
    end_date: Optional[str] = None     # "YYYY-MM-DD", defaults to today


class AnalysisCreate(BaseModel):
    farm_id: int
    image_url: Optional[str] = None
    analysis_type: str = "deforestation_detection"


class AnalysisResponse(BaseModel):
    id: int
    farm_id: int
    image_url: Optional[str] = None
    analysis_type: str
    deforestation_percentage: Optional[float] = None
    confidence_score: Optional[float] = None
    risk_level: Optional[str] = None
    result_status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)