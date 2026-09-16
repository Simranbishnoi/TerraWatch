"""
TerraWatch — temporal change orchestration.

Combines NDVI and spectral change into a single temporal-change result
dict that is consumed by the main pipeline.
"""

from typing import Any, Dict, Optional

import ee

from .ndvi_change import detect_ndvi_decline
from .spectral_change import compute_spectral_change


def run_temporal_change(
    before_image: ee.Image,
    after_image: ee.Image,
    geometry: ee.Geometry,
    ndvi_threshold: float = -0.20,
    scale: int = 10,
) -> Dict[str, Any]:
    """
    Run the full temporal-change analysis pipeline.

    Parameters
    ----------
    before_image   : ee.Image — cloud-masked Sentinel-2, earlier date.
    after_image    : ee.Image — cloud-masked Sentinel-2, later date.
    geometry       : ee.Geometry — farm boundary.
    ndvi_threshold : float — NDVI change below this = potential decline.
    scale          : int — pixel scale in metres.

    Returns
    -------
    dict with all spectral and NDVI change statistics plus the binary
    decline mask and change magnitude image.
    """
    # ── Spectral statistics ───────────────────────────────────────────────
    spectral = compute_spectral_change(before_image, after_image, geometry, scale)

    # ── NDVI-specific decline detection ──────────────────────────────────
    ndvi_result = detect_ndvi_decline(
        before_image, after_image, geometry, ndvi_threshold, scale
    )

    return {
        # Spectral means
        "ndvi_before":          spectral["ndvi_before"],
        "ndvi_after":           spectral["ndvi_after"],
        "ndvi_change":          spectral["ndvi_change"],
        "ndmi_before":          spectral["ndmi_before"],
        "ndmi_after":           spectral["ndmi_after"],
        "ndmi_change":          spectral["ndmi_change"],
        "brightness_before":    spectral["brightness_before"],
        "brightness_after":     spectral["brightness_after"],
        "brightness_change":    spectral["brightness_change"],
        "swir_ratio_before":    spectral["swir_ratio_before"],
        "swir_ratio_after":     spectral["swir_ratio_after"],
        # Decline-specific
        "ndvi_decline_area_ha":  ndvi_result["decline_area_ha"],
        "mean_ndvi_change":      ndvi_result["mean_ndvi_change"],
        "decline_pct":           ndvi_result["decline_pct"],
        "ndvi_threshold_used":   ndvi_threshold,
        # Images (EE server-side, used by downstream modules)
        "decline_mask":         ndvi_result["change_image"],
        "change_magnitude_image": spectral["change_magnitude_image"],
    }
