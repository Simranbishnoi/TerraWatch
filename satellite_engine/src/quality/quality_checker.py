"""
TerraWatch — observation data quality checker.

Assesses Sentinel-2 observations for usability based on cloud
coverage and pixel availability over the farm boundary.

Quality levels:
    HIGH     — >= 85% usable pixels, low cloud
    MEDIUM   — >= 70% usable pixels
    LOW      — >= 50% usable pixels (borderline; used with caution)
    REJECTED — < 50% usable pixels (do not use for analysis)
"""

from typing import Any, Dict

import ee


# ── Constants ────────────────────────────────────────────────────────────────
QUALITY_HIGH     = "HIGH"
QUALITY_MEDIUM   = "MEDIUM"
QUALITY_LOW      = "LOW"
QUALITY_REJECTED = "REJECTED"

HIGH_THRESHOLD   = 85.0  # %
MEDIUM_THRESHOLD = 70.0  # %
LOW_THRESHOLD    = 50.0  # %


def assess_image_quality(
    image: ee.Image,
    geometry: ee.Geometry,
    cloud_prob_threshold: float = 50.0,
    scale: int = 10,
) -> Dict[str, Any]:
    """
    Assess the data quality of a cloud-masked Sentinel-2 image.

    The function calculates what percentage of pixels within the farm
    boundary are valid (unmasked = cloud-free).

    Parameters
    ----------
    image : ee.Image
        Cloud-masked Sentinel-2 image. Masked pixels = cloudy/invalid.
    geometry : ee.Geometry
        Farm boundary.
    cloud_prob_threshold : float
        The threshold used during cloud masking (for metadata purposes).
    scale : int
        Pixel scale in metres.

    Returns
    -------
    dict with:
        quality_level         : str  (HIGH / MEDIUM / LOW / REJECTED)
        usable_pixel_pct      : float
        total_pixels          : int
        valid_pixels          : int
        cloud_prob_threshold  : float
        is_usable             : bool
    """
    # Total pixels in the geometry (using a constant band as reference)
    total_pixels_result = (
        image.select("B8")
        .unmask(0)  # count all pixels (masked + unmasked)
        .reduceRegion(
            reducer=ee.Reducer.count(),
            geometry=geometry,
            scale=scale,
            maxPixels=1e10,
            bestEffort=True,
        )
        .get("B8")
    )

    # Valid pixels (not masked)
    valid_pixels_result = (
        image.select("B8")
        .reduceRegion(
            reducer=ee.Reducer.count(),
            geometry=geometry,
            scale=scale,
            maxPixels=1e10,
            bestEffort=True,
        )
        .get("B8")
    )

    result = ee.Dictionary({
        "total": total_pixels_result,
        "valid": valid_pixels_result,
    }).getInfo()

    total = result.get("total") or 0
    valid = result.get("valid") or 0

    usable_pct = round((valid / total) * 100, 2) if total > 0 else 0.0

    # Classify quality
    if usable_pct >= HIGH_THRESHOLD:
        level = QUALITY_HIGH
    elif usable_pct >= MEDIUM_THRESHOLD:
        level = QUALITY_MEDIUM
    elif usable_pct >= LOW_THRESHOLD:
        level = QUALITY_LOW
    else:
        level = QUALITY_REJECTED

    is_usable = level in (QUALITY_HIGH, QUALITY_MEDIUM)

    return {
        "quality_level":        level,
        "usable_pixel_pct":     usable_pct,
        "total_pixels":         total,
        "valid_pixels":         valid,
        "cloud_prob_threshold": cloud_prob_threshold,
        "is_usable":            is_usable,
    }


def is_observation_usable(quality_result: Dict[str, Any]) -> bool:
    """Convenience: return True if quality is HIGH or MEDIUM."""
    return quality_result.get("is_usable", False)
