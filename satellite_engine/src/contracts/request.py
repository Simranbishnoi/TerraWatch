"""
TerraWatch — satellite analysis request contract.
"""

from dataclasses import dataclass, field
from datetime import date
from typing import Any, Dict, Optional


@dataclass
class SatelliteAnalysisRequest:
    """
    Input sent by Simran's backend to the satellite engine.

    farm_id                    : int  — database ID of the farm.
    boundary                   : dict — GeoJSON Polygon geometry.
    start_date                 : str  — analysis start (YYYY-MM-DD).
    end_date                   : str  — analysis end   (YYYY-MM-DD).
    previous_observation_date  : str | None — last processed observation;
                                 if None, this is the first analysis run.
    """

    farm_id: int
    boundary: Dict[str, Any]
    start_date: str
    end_date: str
    previous_observation_date: Optional[str] = None

    # ------------------------------------------------------------------ #
    # Helpers                                                              #
    # ------------------------------------------------------------------ #

    def validate(self) -> None:
        """Raise ValueError for obviously bad inputs."""
        if not isinstance(self.farm_id, int) or self.farm_id < 0:
            raise ValueError(f"farm_id must be a non-negative integer, got {self.farm_id!r}")

        if not isinstance(self.boundary, dict):
            raise ValueError("boundary must be a GeoJSON dict")

        if self.boundary.get("type") != "Polygon":
            raise ValueError(
                f"boundary.type must be 'Polygon', got {self.boundary.get('type')!r}"
            )

        if "coordinates" not in self.boundary or not self.boundary["coordinates"]:
            raise ValueError("boundary.coordinates is missing or empty")

        try:
            date.fromisoformat(self.start_date)
        except (TypeError, ValueError):
            raise ValueError(f"start_date is not a valid ISO date: {self.start_date!r}")

        try:
            date.fromisoformat(self.end_date)
        except (TypeError, ValueError):
            raise ValueError(f"end_date is not a valid ISO date: {self.end_date!r}")

        if self.start_date >= self.end_date:
            raise ValueError(
                f"start_date ({self.start_date}) must be before end_date ({self.end_date})"
            )

        if self.previous_observation_date is not None:
            try:
                date.fromisoformat(self.previous_observation_date)
            except (TypeError, ValueError):
                raise ValueError(
                    f"previous_observation_date is not a valid ISO date: "
                    f"{self.previous_observation_date!r}"
                )

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SatelliteAnalysisRequest":
        return cls(
            farm_id=data["farm_id"],
            boundary=data["boundary"],
            start_date=data["start_date"],
            end_date=data["end_date"],
            previous_observation_date=data.get("previous_observation_date"),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "farm_id": self.farm_id,
            "boundary": self.boundary,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "previous_observation_date": self.previous_observation_date,
        }
