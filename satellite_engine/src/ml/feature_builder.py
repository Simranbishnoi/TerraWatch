"""
TerraWatch — ML feature builder.

Converts satellite analysis results into a normalised feature vector
for the risk model and anomaly detector.

Feature schema: models/feature_schema.json
"""

from typing import Any, Dict, List, Optional


FEATURE_NAMES = [
    # NDVI
    "ndvi_before", "ndvi_after", "ndvi_change",
    # NDMI
    "ndmi_before", "ndmi_after", "ndmi_change",
    # Loss
    "forest_loss_hectares", "loss_percentage",
    # Forest
    "forest_area_before_ha", "forest_area_after_ha",
    # Quality
    "usable_pixel_pct",
    # Boundary
    "boundary_overlap_pct", "excluded_loss_ha", "inside_loss_ha",
    # Change extent
    "ndvi_decline_area_ha", "decline_pct",
    # Observation
    "observation_gap_days",
]


def build_features(
    ndvi_before: Optional[float],
    ndvi_after:  Optional[float],
    ndvi_change: Optional[float],
    ndmi_before: Optional[float],
    ndmi_after:  Optional[float],
    ndmi_change: Optional[float],
    forest_loss_ha: Optional[float],
    loss_pct: Optional[float],
    forest_area_before: Optional[float],
    forest_area_after:  Optional[float],
    usable_pixel_pct:   Optional[float],
    overlap_pct:        Optional[float],
    excluded_loss_ha:   Optional[float],
    inside_loss_ha:     Optional[float],
    decline_area_ha:    Optional[float],
    decline_pct:        Optional[float],
    observation_gap_days: Optional[int],
) -> Dict[str, Optional[float]]:
    """
    Build a named feature dict ready for model input.

    All values are kept as floats or None (not imputed here).
    Imputation happens inside risk_model.py.

    Returns
    -------
    dict[str, float | None]
    """
    return {
        "ndvi_before":          ndvi_before,
        "ndvi_after":           ndvi_after,
        "ndvi_change":          ndvi_change,
        "ndmi_before":          ndmi_before,
        "ndmi_after":           ndmi_after,
        "ndmi_change":          ndmi_change,
        "forest_loss_hectares": forest_loss_ha,
        "loss_percentage":      loss_pct,
        "forest_area_before_ha": forest_area_before,
        "forest_area_after_ha":  forest_area_after,
        "usable_pixel_pct":     usable_pixel_pct,
        "boundary_overlap_pct": overlap_pct,
        "excluded_loss_ha":     excluded_loss_ha,
        "inside_loss_ha":       inside_loss_ha,
        "ndvi_decline_area_ha": decline_area_ha,
        "decline_pct":          decline_pct,
        "observation_gap_days": float(observation_gap_days) if observation_gap_days is not None else None,
    }


def features_to_vector(features: Dict[str, Optional[float]]) -> List[float]:
    """
    Convert features dict to an ordered list for sklearn models.
    Missing values are imputed with 0.0.

    Parameters
    ----------
    features : dict — output of build_features().

    Returns
    -------
    List[float] — ordered by FEATURE_NAMES.
    """
    return [float(features.get(name) or 0.0) for name in FEATURE_NAMES]


def calculate_observation_gap(before_date: str, after_date: str) -> int:
    """Return the number of days between before and after observations."""
    from datetime import date
    d_before = date.fromisoformat(before_date)
    d_after  = date.fromisoformat(after_date)
    return (d_after - d_before).days
