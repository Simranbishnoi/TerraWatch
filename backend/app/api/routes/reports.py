from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.database import get_db
from app.models.farm import Farm
from app.models.report import Report
from app.models.user import User
from app.schemas.report import ReportCreate, ReportResponse


router = APIRouter()


@router.post(
    "/",
    response_model=ReportResponse,
    status_code=201
)
def create_report(
    report_data: ReportCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    farm = db.query(Farm).filter(
        Farm.id == report_data.farm_id
    ).first()

    if not farm:
        raise HTTPException(
            status_code=404,
            detail="Farm not found"
        )

    report = Report(**report_data.model_dump())

    db.add(report)
    db.commit()
    db.refresh(report)

    return report


@router.get(
    "/",
    response_model=List[ReportResponse]
)
def get_reports(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(Report).order_by(
        Report.created_at.desc()
    ).all()


@router.get(
    "/{report_id}",
    response_model=ReportResponse
)
def get_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    report = db.query(Report).filter(
        Report.id == report_id
    ).first()

    if not report:
        raise HTTPException(
            status_code=404,
            detail="Report not found"
        )

    return report