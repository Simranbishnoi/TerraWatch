from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.sql import func

from app.db.database import Base


class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, index=True)

    farm_id = Column(
        Integer,
        ForeignKey("farms.id"),
        nullable=False
    )

    image_url = Column(Text, nullable=True)

    analysis_type = Column(
        String(100),
        default="deforestation_detection"
    )

    deforestation_percentage = Column(Float, nullable=True)

    confidence_score = Column(Float, nullable=True)

    risk_level = Column(String(50), nullable=True)

    result_status = Column(
        String(50),
        default="pending"
    )

    created_at = Column(DateTime(timezone=True), server_default=func.now())