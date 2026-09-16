"""
TerraWatch — satellite analysis response contract.

All numeric scores are None when the model is not ready, rather than
hard-coded placeholder values.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


# ── Status constants ────────────────────────────────────────────────────────
STATUS_NEW_OBSERVATION = "NEW_OBSERVATION"
STATUS_NO_NEW_OBSERVATION = "NO_NEW_OBSERVATION"
STATUS_NO_USABLE_OBSERVATION = "NO_USABLE_OBSERVATION"
STATUS_INVALID_BOUNDARY = "INVALID_BOUNDARY"
STATUS_INVALID_DATE_RANGE = "INVALID_DATE_RANGE"
STATUS_PROCESSING_ERROR = "PROCESSING_ERROR"

# ── Quality levels ───────────────────────────────────────────────────────────
QUALITY_HIGH = "HIGH"
QUALITY_MEDIUM = "MEDIUM"
QUALITY_LOW = "LOW"
QUALITY_REJECTED = "REJECTED"

# ── Risk levels ──────────────────────────────────────────────────────────────
RISK_LOW = "LOW"
RISK_MEDIUM = "MEDIUM"
RISK_HIGH = "HIGH"
RISK_VERY_HIGH = "VERY_HIGH"
RISK_REVIEW = "REVIEW"


@dataclass
class ObservationInfo:
    date: Optional[str]
    previous_date: Optional[str]
    image_id: Optional[str]


@dataclass
class QualityInfo:
    level: str
    usable_pixel_percentage: Optional[float]
    cloud_probability: Optional[float]


@dataclass
class ForestInfo:
    ndvi_before: Optional[float]
    ndvi_after: Optional[float]
    ndvi_change: Optional[float]
    ndmi_before: Optional[float]
    ndmi_after: Optional[float]
    ndmi_change: Optional[float]
    forest_area_before_ha: Optional[float]
    forest_area_after_ha: Optional[float]
    forest_loss_hectares: Optional[float]
    deforestation_percentage: Optional[float]  # % of farm area lost


@dataclass
class RiskInfo:
    score: Optional[float]
    level: str
    model_version: Optional[str]
    model_status: str  # e.g. "RULE_BASED", "MODEL_NOT_READY"


@dataclass
class BoundaryInfo:
    boundary_manipulation_score: Optional[float]
    excluded_loss_hectares: Optional[float]
    inside_loss_hectares: Optional[float]
    total_detected_loss_ha: Optional[float]
    overlap_percentage: Optional[float]


@dataclass
class EvidenceInfo:
    before_image_url: Optional[str]
    after_image_url: Optional[str]
    loss_geojson: Optional[Dict[str, Any]]
    summary: List[str] = field(default_factory=list)


@dataclass
class SatelliteAnalysisResponse:
    """
    Full structured response from the satellite engine.
    """

    status: str
    farm_id: int
    processing_timestamp: str
    message: Optional[str]

    observation: ObservationInfo
    quality: QualityInfo
    forest: ForestInfo
    risk: RiskInfo
    boundary: BoundaryInfo
    evidence: EvidenceInfo

    def to_dict(self) -> Dict[str, Any]:
        """Convert to flat dict matching Simran's backend storage schema."""
        # Derived computed fields
        loss_ha = self.forest.forest_loss_hectares or 0.0
        valid_ha = getattr(self, "_valid_area_ha", None)
        deforestation_pct = round(self.forest.deforestation_percentage or 0.0, 2)
        deforestation_detected = (
            loss_ha > 0 and
            (self.forest.ndvi_change is not None and self.forest.ndvi_change < -0.05)
        ) if self.status == "NEW_OBSERVATION" else False

        confidence = round((self.quality.usable_pixel_percentage or 0.0) / 100, 4)

        return {
            # ── Simran's expected format ──────────────────────────────────
            "farm_id":                  self.farm_id,
            "deforestation_detected":   deforestation_detected,
            "deforestation_percentage": deforestation_pct,
            "forest_cover_change":      round(-deforestation_pct, 2),
            "ndvi_before":              self.forest.ndvi_before,
            "ndvi_after":               self.forest.ndvi_after,
            "risk_level":               self.risk.level.lower(),
            "confidence_score":         confidence,
            "historical_date":          self.observation.previous_date,
            "current_date":             self.observation.date,
            # ── Extended fields ───────────────────────────────────────────
            "status":                   self.status,
            "processing_timestamp":     self.processing_timestamp,
            "message":                  self.message,
            "observation_date":         self.observation.date,
            "previous_observation_date": self.observation.previous_date,
            "image_id":                 self.observation.image_id,
            "quality_level":            self.quality.level,
            "usable_pixel_percentage":  self.quality.usable_pixel_percentage,
            "cloud_probability":        self.quality.cloud_probability,
            "ndvi_change":              self.forest.ndvi_change,
            "ndmi_before":              self.forest.ndmi_before,
            "ndmi_after":               self.forest.ndmi_after,
            "ndmi_change":              self.forest.ndmi_change,
            "forest_area_before_ha":    self.forest.forest_area_before_ha,
            "forest_area_after_ha":     self.forest.forest_area_after_ha,
            "forest_loss_hectares":     self.forest.forest_loss_hectares,
            "risk_score":               self.risk.score,
            "risk_model_version":       self.risk.model_version,
            "risk_model_status":        self.risk.model_status,
            "boundary_manipulation_score": self.boundary.boundary_manipulation_score,
            "excluded_loss_hectares":   self.boundary.excluded_loss_hectares,
            "inside_loss_hectares":     self.boundary.inside_loss_hectares,
            "total_detected_loss_ha":   self.boundary.total_detected_loss_ha,
            "overlap_percentage":       self.boundary.overlap_percentage,
            "before_image":             self.evidence.before_image_url,
            "after_image":              self.evidence.after_image_url,
            "loss_geojson":             self.evidence.loss_geojson,
            "evidence_summary":         self.evidence.summary,
        }

    @staticmethod
    def error_response(
        farm_id: int,
        status: str,
        message: str,
    ) -> "SatelliteAnalysisResponse":
        """Build a minimal error response."""
        now = datetime.now(timezone.utc).isoformat()
        return SatelliteAnalysisResponse(
            status=status,
            farm_id=farm_id,
            processing_timestamp=now,
            message=message,
            observation=ObservationInfo(date=None, previous_date=None, image_id=None),
            quality=QualityInfo(level=QUALITY_REJECTED, usable_pixel_percentage=None, cloud_probability=None),
            forest=ForestInfo(
                ndvi_before=None, ndvi_after=None, ndvi_change=None,
                ndmi_before=None, ndmi_after=None, ndmi_change=None,
                forest_area_before_ha=None, forest_area_after_ha=None,
                forest_loss_hectares=None, deforestation_percentage=None,
            ),
            risk=RiskInfo(score=None, level=RISK_REVIEW, model_version=None, model_status="MODEL_NOT_READY"),
            boundary=BoundaryInfo(
                boundary_manipulation_score=None,
                excluded_loss_hectares=None,
                inside_loss_hectares=None,
                total_detected_loss_ha=None,
                overlap_percentage=None,
            ),
            evidence=EvidenceInfo(
                before_image_url=None,
                after_image_url=None,
                loss_geojson=None,
                summary=[],
            ),
        )
