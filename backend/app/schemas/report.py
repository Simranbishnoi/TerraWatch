from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class ReportCreate(BaseModel):
    farm_id: int
    analysis_id: Optional[int] = None
    report_title: str
    summary: Optional[str] = None


class ReportResponse(BaseModel):
    id: int
    farm_id: int
    analysis_id: Optional[int] = None
    report_title: str
    report_url: Optional[str] = None
    summary: Optional[str] = None
    fraud_detected: str
    verification_status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)