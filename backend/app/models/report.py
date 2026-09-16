from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.sql import func

from app.db.database import Base


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)

    farm_id = Column(
        Integer,
        ForeignKey("farms.id"),
        nullable=False
    )

    analysis_id = Column(
        Integer,
        ForeignKey("analyses.id"),
        nullable=True
    )

    report_title = Column(String(200), nullable=False)

    report_url = Column(Text, nullable=True)

    summary = Column(Text, nullable=True)

    fraud_detected = Column(String(20), default="false")

    verification_status = Column(
        String(50),
        default="pending"
    )

    created_at = Column(DateTime(timezone=True), server_default=func.now())