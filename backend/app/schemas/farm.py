from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class FarmCreate(BaseModel):
    farm_name: str
    location: str
    latitude: float
    longitude: float
    area_hectares: Optional[float] = None
    owner_id: Optional[int] = None


class FarmResponse(BaseModel):
    id: int
    farm_name: str
    location: str
    latitude: float
    longitude: float
    area_hectares: Optional[float] = None
    owner_id: Optional[int] = None
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)