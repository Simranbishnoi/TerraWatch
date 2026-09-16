from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.farm import Farm
from app.models.report import Report
from app.schemas.report import ReportCreate, ReportResponse

router = APIRouter()


@router.post("/", response_model=ReportResponse, status_code=201)
def create_report(
    report_data: ReportCreate,
    db: Session = Depends(get_db)
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


from app.core.security import get_current_user
from app.models.user import User

MOCK_REPORTS_DATA = [
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


@router.get("/")
def get_reports(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return MOCK_REPORTS_DATA



@router.get("/{report_id}", response_model=ReportResponse)
def get_report(
    report_id: int,
    db: Session = Depends(get_db)
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