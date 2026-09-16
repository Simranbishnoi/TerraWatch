"""
TerraWatch — forest/vegetation mask.

Creates a binary mask distinguishing forest/vegetation-like areas from
bare soil, water, buildings, and roads using Sentinel-2 spectral thresholds.

This is an initial vegetation mask — not a certified forest classifier.
Results should be interpreted as *potential forest/vegetation area*.
"""

from typing import Any, Dict, Optional

import ee


# ── Thresholds (overridable) ─────────────────────────────────────────────────
DEFAULT_VEGETATION_NDVI = 0.35   # NDVI >= 0.35 → vegetated
DEFAULT_FOREST_NDVI     = 0.50   # NDVI >= 0.50 → likely forest canopy
DEFAULT_WATER_NDWI_MIN  = 0.0    # NDWI > 0 → water (suppress from forest)


def create_vegetation_mask(
    image: ee.Image,
    ndvi_threshold: float = DEFAULT_VEGETATION_NDVI,
) -> ee.Image:
    """
    Create a binary vegetation mask (1=vegetated, 0=not vegetated).

    Uses NDVI threshold only. More permissive than forest mask.

    Parameters
    ----------
    image : ee.Image — Sentinel-2 SR image.
    ndvi_threshold : float

    Returns
    -------
    ee.Image (1 band, binary, named 'vegetation_mask')
    """
    ndvi = image.normalizedDifference(["B8", "B4"]).rename("NDVI")
    veg_mask = ndvi.gte(ndvi_threshold).rename("vegetation_mask")
    return veg_mask


def create_forest_mask(
    image: ee.Image,
    ndvi_threshold: float = DEFAULT_FOREST_NDVI,
    suppress_water: bool = True,
) -> ee.Image:
    """
    Create a binary forest/dense-vegetation mask.

    Strategy:
        1. NDVI >= threshold (dense canopy)
        2. Optionally suppress water pixels (NDWI > 0)
        3. Suppress bright bare-soil (high SWIR reflectance)

    Parameters
    ----------
    image : ee.Image
    ndvi_threshold : float — default 0.50
    suppress_water : bool  — mask out water bodies

    Returns
    -------
    ee.Image (1 band, binary, named 'forest_mask')
    """
    ndvi = image.normalizedDifference(["B8", "B4"]).rename("NDVI")
    forest = ndvi.gte(ndvi_threshold)

    if suppress_water:
        # NDWI = (Green - NIR) / (Green + NIR)
        ndwi = image.normalizedDifference(["B3", "B8"])
        not_water = ndwi.lt(0.0)
        forest = forest.And(not_water)

    # Suppress extremely high SWIR (burned/bare soil can have moderate NDVI)
    swir_ratio = image.select("B11").divide(image.select("B8").add(1e-6))
    not_burned = swir_ratio.lt(0.8)
    forest = forest.And(not_burned)

    return forest.rename("forest_mask")


def get_forest_area_hectares(
    forest_mask: ee.Image,
    geometry: ee.Geometry,
    scale: int = 10,
) -> float:
    """
    Compute the total forest/vegetation area in hectares.

    Parameters
    ----------
    forest_mask : ee.Image — binary, named 'forest_mask'.
    geometry    : ee.Geometry
    scale       : int

    Returns
    -------
    float — area in hectares.
    """
    area_m2 = (
        forest_mask
        .multiply(ee.Image.pixelArea())
        .reduceRegion(
            reducer=ee.Reducer.sum(),
            geometry=geometry,
            scale=scale,
            maxPixels=1e10,
            bestEffort=True,
        )
        .get("forest_mask")
    ).getInfo()

    return round((area_m2 or 0.0) / 10_000, 4)
