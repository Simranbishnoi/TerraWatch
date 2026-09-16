"""
TerraWatch — NDVI-based change detection.

Produces a per-pixel change mask and summary statistics for the
NDVI difference between a before and after observation.

NDVI decline alone is NOT proof of deforestation.
Always interpret alongside spectral and temporal context.
"""

from typing import Any, Dict, Optional

import ee

from ..ndvi.calculator import calculate_ndvi


# ── Change mask ──────────────────────────────────────────────────────────────

def compute_ndvi_change_image(
    before_image: ee.Image,
    after_image: ee.Image,
) -> ee.Image:
    """
    Compute per-pixel NDVI difference image.

    Parameters
    ----------
    before_image : ee.Image — cloud-masked Sentinel-2 image (before period).
    after_image  : ee.Image — cloud-masked Sentinel-2 image (after period).

    Returns
    -------
    ee.Image with a single band 'NDVI_change' (float, range approx -2 to 2).
    """
    ndvi_before = calculate_ndvi(before_image)
    ndvi_after  = calculate_ndvi(after_image)
    change = ndvi_after.subtract(ndvi_before).rename("NDVI_change")
    return change


def detect_ndvi_decline(
    before_image: ee.Image,
    after_image: ee.Image,
    geometry: ee.Geometry,
    threshold: float = -0.20,
    scale: int = 10,
) -> Dict[str, Any]:
    """
    Create a binary mask of pixels where NDVI declined below ``threshold``.

    Parameters
    ----------
    before_image : ee.Image
    after_image  : ee.Image
    geometry     : ee.Geometry — farm/analysis region.
    threshold    : float — NDVI change below this value = potential decline.
                   Default -0.20 per config/thresholds.yaml.
    scale        : int — pixel scale in metres.

    Returns
    -------
    dict with:
        change_image      : ee.Image (binary, 1=decline, 0=no decline)
        decline_area_ha   : float
        mean_ndvi_change  : float
        decline_pct       : float  (% of valid pixels that declined)
        threshold_used    : float
    """
    change_img = compute_ndvi_change_image(before_image, after_image)

    # Binary mask: 1 where change < threshold
    decline_mask = change_img.lt(threshold).rename("NDVI_decline")

    pixel_area = ee.Image.pixelArea()

    # ── Decline area ──────────────────────────────────────────────────────
    decline_area_m2 = (
        decline_mask
        .multiply(pixel_area)
        .reduceRegion(
            reducer=ee.Reducer.sum(),
            geometry=geometry,
            scale=scale,
            maxPixels=1e10,
            bestEffort=True,
        )
        .get("NDVI_decline")
    )

    # ── Mean change over whole farm ───────────────────────────────────────
    mean_change = (
        change_img
        .reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=geometry,
            scale=scale,
            maxPixels=1e10,
            bestEffort=True,
        )
        .get("NDVI_change")
    )

    # ── Total valid pixel count ───────────────────────────────────────────
    total_pixels = (
        change_img
        .mask()
        .reduceRegion(
            reducer=ee.Reducer.sum(),
            geometry=geometry,
            scale=scale,
            maxPixels=1e10,
            bestEffort=True,
        )
        .get("NDVI_change")
    )

    # ── Declined pixel count ──────────────────────────────────────────────
    decline_pixels = (
        decline_mask
        .reduceRegion(
            reducer=ee.Reducer.sum(),
            geometry=geometry,
            scale=scale,
            maxPixels=1e10,
            bestEffort=True,
        )
        .get("NDVI_decline")
    )

    # Execute all at once
    result = ee.Dictionary({
        "decline_area_m2": decline_area_m2,
        "mean_change": mean_change,
        "total_pixels": total_pixels,
        "decline_pixels": decline_pixels,
    }).getInfo()

    area_m2   = result.get("decline_area_m2") or 0.0
    mean_chg  = result.get("mean_change")
    tot_px    = result.get("total_pixels") or 1
    dec_px    = result.get("decline_pixels") or 0

    decline_pct = round((dec_px / tot_px) * 100, 2) if tot_px else 0.0

    return {
        "change_image":      decline_mask,
        "decline_area_ha":   round(area_m2 / 10_000, 4),
        "mean_ndvi_change":  round(float(mean_chg), 6) if mean_chg is not None else None,
        "decline_pct":       decline_pct,
        "threshold_used":    threshold,
    }
