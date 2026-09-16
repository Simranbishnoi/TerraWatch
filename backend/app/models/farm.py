from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.sql import func

from app.db.database import Base


class Farm(Base):
    __tablename__ = "farms"

    id = Column(Integer, primary_key=True, index=True)

    owner_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True
    )

    farm_name = Column(String(150), nullable=False)

    location = Column(String(255), nullable=False)

    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)

    area_hectares = Column(Float, nullable=True)

    status = Column(
        String(50),
        default="pending"
    )

    created_at = Column(DateTime(timezone=True), server_default=func.now())