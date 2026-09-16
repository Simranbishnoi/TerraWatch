"""
TerraWatch — loss / farm-boundary overlap analysis.

Computes how much of the detected forest/vegetation loss area falls
inside the submitted farm boundary versus outside it.
"""

from typing import Any, Dict, Optional

import ee


def calculate_overlap(
    loss_mask: ee.Image,
    farm_geometry: ee.Geometry,
    scale: int = 10,
) -> Dict[str, Optional[float]]:
    """
    Compute the split of detected loss between inside and outside
    the farm boundary.

    Parameters
    ----------
    loss_mask : ee.Image
        Binary image — 1 = loss pixel, 0 = no loss.
        Must already be clipped or masked to the analysis region.
    farm_geometry : ee.Geometry
        The submitted farm polygon.
    scale : int
        Pixel scale in metres (default 10 for Sentinel-2).

    Returns
    -------
    dict with keys:
        total_detected_loss_ha
        inside_loss_ha
        outside_loss_ha
        overlap_percentage          (inside / total × 100)
        outside_percentage
    """
    pixel_area = ee.Image.pixelArea()  # m² per pixel

    # ── Total loss area (may extend beyond farm polygon) ─────────────────
    # Use the loss mask's own footprint — unbounded region
    total_loss_area_m2 = (
        loss_mask
        .multiply(pixel_area)
        .reduceRegion(
            reducer=ee.Reducer.sum(),
            geometry=farm_geometry.buffer(500),  # small buffer to catch edge loss
            scale=scale,
            maxPixels=1e10,
            bestEffort=True,
        )
        .get("loss_mask")
    )

    # ── Loss inside farm boundary ─────────────────────────────────────────
    inside_loss_m2 = (
        loss_mask
        .clip(farm_geometry)
        .multiply(pixel_area)
        .reduceRegion(
            reducer=ee.Reducer.sum(),
            geometry=farm_geometry,
            scale=scale,
            maxPixels=1e10,
            bestEffort=True,
        )
        .get("loss_mask")
    )

    # Execute both at once
    result = ee.Dictionary({
        "total": total_loss_area_m2,
        "inside": inside_loss_m2,
    }).getInfo()

    total_m2 = result.get("total") or 0.0
    inside_m2 = result.get("inside") or 0.0
    outside_m2 = max(0.0, total_m2 - inside_m2)

    total_ha = round(total_m2 / 10_000, 4)
    inside_ha = round(inside_m2 / 10_000, 4)
    outside_ha = round(outside_m2 / 10_000, 4)

    overlap_pct = round((inside_ha / total_ha * 100), 2) if total_ha > 0 else 0.0
    outside_pct = round(100 - overlap_pct, 2)

    return {
        "total_detected_loss_ha": total_ha,
        "inside_loss_ha": inside_ha,
        "outside_loss_ha": outside_ha,
        "overlap_percentage": overlap_pct,
        "outside_percentage": outside_pct,
    }
