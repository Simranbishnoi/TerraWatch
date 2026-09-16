"""
TerraWatch — spectral change detection.

Extends NDVI-only change detection with additional Sentinel-2 bands:
    B4  (Red)   B8 (NIR)   B11 (SWIR-1)   B12 (SWIR-2)

Spectral indices computed:
    NDMI = (B8 - B11) / (B8 + B11)   — moisture / canopy water content
    BRIGHTNESS = mean of visible + NIR bands
    SWIR_RATIO = B11 / B8             — bare-soil / burned indicator
"""

from typing import Any, Dict, Optional

import ee

from ..ndvi.calculator import calculate_ndvi, calculate_ndmi


def add_spectral_indices(image: ee.Image) -> ee.Image:
    """
    Add NDVI, NDMI, Brightness, and SWIR_RATIO bands to a Sentinel-2 image.
    """
    ndvi       = image.normalizedDifference(["B8", "B4"]).rename("NDVI")
    ndmi       = image.normalizedDifference(["B8", "B11"]).rename("NDMI")
    brightness = image.select(["B2", "B3", "B4", "B8"]).reduce(ee.Reducer.mean()).rename("BRIGHTNESS")
    swir_ratio = image.select("B11").divide(
        image.select("B8").add(1e-6)
    ).rename("SWIR_RATIO")

    return image.addBands([ndvi, ndmi, brightness, swir_ratio])


def compute_spectral_change(
    before_image: ee.Image,
    after_image: ee.Image,
    geometry: ee.Geometry,
    scale: int = 10,
) -> Dict[str, Any]:
    """
    Compute multi-spectral change statistics between two observations.

    Returns
    -------
    dict with keys:
        ndvi_before, ndvi_after, ndvi_change
        ndmi_before, ndmi_after, ndmi_change
        brightness_before, brightness_after, brightness_change
        swir_ratio_before, swir_ratio_after
        change_magnitude_image  : ee.Image (Euclidean distance in feature space)
    """
    # Enrich both images
    before_idx = add_spectral_indices(before_image)
    after_idx  = add_spectral_indices(after_image)

    def _mean(image: ee.Image, band: str) -> Optional[float]:
        result = image.select(band).reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=geometry,
            scale=scale,
            maxPixels=1e10,
            bestEffort=True,
        ).getInfo()
        val = result.get(band)
        return round(float(val), 6) if val is not None else None

    ndvi_b = _mean(before_idx, "NDVI")
    ndvi_a = _mean(after_idx,  "NDVI")
    ndmi_b = _mean(before_idx, "NDMI")
    ndmi_a = _mean(after_idx,  "NDMI")
    brt_b  = _mean(before_idx, "BRIGHTNESS")
    brt_a  = _mean(after_idx,  "BRIGHTNESS")
    swir_b = _mean(before_idx, "SWIR_RATIO")
    swir_a = _mean(after_idx,  "SWIR_RATIO")

    # ── Change magnitude image (per-pixel Euclidean distance) ─────────────
    diff = after_idx.select(["NDVI", "NDMI", "BRIGHTNESS"]).subtract(
        before_idx.select(["NDVI", "NDMI", "BRIGHTNESS"])
    )
    magnitude = diff.pow(2).reduce(ee.Reducer.sum()).sqrt().rename("CHANGE_MAGNITUDE")

    return {
        "ndvi_before":          ndvi_b,
        "ndvi_after":           ndvi_a,
        "ndvi_change":          round(ndvi_a - ndvi_b, 6) if (ndvi_a and ndvi_b) else None,
        "ndmi_before":          ndmi_b,
        "ndmi_after":           ndmi_a,
        "ndmi_change":          round(ndmi_a - ndmi_b, 6) if (ndmi_a and ndmi_b) else None,
        "brightness_before":    brt_b,
        "brightness_after":     brt_a,
        "brightness_change":    round(brt_a - brt_b, 6) if (brt_a and brt_b) else None,
        "swir_ratio_before":    swir_b,
        "swir_ratio_after":     swir_a,
        "change_magnitude_image": magnitude,
    }
