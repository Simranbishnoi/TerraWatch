"""
TerraWatch — NDVI calculator.

Sentinel-2 bands:
    B4  = Red (665 nm)
    B8  = NIR (842 nm)
    B11 = SWIR-1 (1610 nm)

NDVI  = (B8 - B4) / (B8 + B4)   range [-1, 1]
NDMI  = (B8 - B11) / (B8 + B11) range [-1, 1]  moisture index
"""

from typing import Any, Dict, Optional

import ee


# ── Index calculation ────────────────────────────────────────────────────────

def add_ndvi(image: ee.Image) -> ee.Image:
    """
    Add an NDVI band (named 'NDVI') to a Sentinel-2 image.

    Parameters
    ----------
    image : ee.Image
        Sentinel-2 SR image with bands B4 (Red) and B8 (NIR).

    Returns
    -------
    ee.Image with an additional 'NDVI' band.
    """
    ndvi = image.normalizedDifference(["B8", "B4"]).rename("NDVI")
    return image.addBands(ndvi)


def add_ndmi(image: ee.Image) -> ee.Image:
    """
    Add an NDMI band (named 'NDMI') to a Sentinel-2 image.

    Parameters
    ----------
    image : ee.Image
        Sentinel-2 SR image with bands B8 (NIR) and B11 (SWIR-1).

    Returns
    -------
    ee.Image with an additional 'NDMI' band.
    """
    ndmi = image.normalizedDifference(["B8", "B11"]).rename("NDMI")
    return image.addBands(ndmi)


def calculate_ndvi(image: ee.Image) -> ee.Image:
    """Return a single-band NDVI image (no original bands)."""
    return image.normalizedDifference(["B8", "B4"]).rename("NDVI")


def calculate_ndmi(image: ee.Image) -> ee.Image:
    """Return a single-band NDMI image (no original bands)."""
    return image.normalizedDifference(["B8", "B11"]).rename("NDMI")


# ── Statistics ───────────────────────────────────────────────────────────────

def get_ndvi_statistics(
    image: ee.Image,
    geometry: ee.Geometry,
    scale: int = 10,
) -> Dict[str, Optional[float]]:
    """
    Compute mean, median, std, and valid pixel count for the NDVI band
    within the given geometry.

    Parameters
    ----------
    image : ee.Image
        Image that contains an 'NDVI' band (call add_ndvi first).
    geometry : ee.Geometry
        Farm or analysis region.
    scale : int
        Pixel scale in metres.

    Returns
    -------
    dict with keys: mean, median, std_dev, valid_pixels, min, max
    """
    ndvi = image.select("NDVI")

    stats = ndvi.reduceRegion(
        reducer=ee.Reducer.mean()
            .combine(ee.Reducer.median(), sharedInputs=True)
            .combine(ee.Reducer.stdDev(), sharedInputs=True)
            .combine(ee.Reducer.min(), sharedInputs=True)
            .combine(ee.Reducer.max(), sharedInputs=True)
            .combine(ee.Reducer.count(), sharedInputs=True),
        geometry=geometry,
        scale=scale,
        maxPixels=1e10,
        bestEffort=True,
    ).getInfo()

    def _safe(key: str) -> Optional[float]:
        val = stats.get(f"NDVI_{key}")
        return round(float(val), 6) if val is not None else None

    return {
        "mean":         _safe("mean"),
        "median":       _safe("median"),
        "std_dev":      _safe("stdDev"),
        "min":          _safe("min"),
        "max":          _safe("max"),
        "valid_pixels": stats.get("NDVI_count"),
    }


def get_ndmi_statistics(
    image: ee.Image,
    geometry: ee.Geometry,
    scale: int = 10,
) -> Dict[str, Optional[float]]:
    """
    Same as get_ndvi_statistics but for the NDMI band.
    """
    ndmi = image.select("NDMI")

    stats = ndmi.reduceRegion(
        reducer=ee.Reducer.mean()
            .combine(ee.Reducer.median(), sharedInputs=True)
            .combine(ee.Reducer.stdDev(), sharedInputs=True)
            .combine(ee.Reducer.count(), sharedInputs=True),
        geometry=geometry,
        scale=scale,
        maxPixels=1e10,
        bestEffort=True,
    ).getInfo()

    def _safe(key: str) -> Optional[float]:
        val = stats.get(f"NDMI_{key}")
        return round(float(val), 6) if val is not None else None

    return {
        "mean":         _safe("mean"),
        "median":       _safe("median"),
        "std_dev":      _safe("stdDev"),
        "valid_pixels": stats.get("NDMI_count"),
    }


# ── Change ───────────────────────────────────────────────────────────────────

def calculate_ndvi_change(
    ndvi_before: float,
    ndvi_after: float,
) -> float:
    """
    Simple difference: ndvi_after - ndvi_before.
    Negative = potential decline; positive = possible regrowth.
    """
    return round(ndvi_after - ndvi_before, 6)
