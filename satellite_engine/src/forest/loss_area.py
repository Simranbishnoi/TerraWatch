"""
TerraWatch — forest/vegetation loss area estimation.

Compares before/after forest masks to identify pixels that transitioned
from forest/vegetation to non-forest.

The result is labelled 'potential forest/vegetation loss' — not confirmed
deforestation — until validated by a trained classifier.
"""

from typing import Any, Dict, Optional

import ee

from .forest_mask import create_forest_mask


# ── Loss detection ───────────────────────────────────────────────────────────

def detect_loss_mask(
    before_forest_mask: ee.Image,
    after_forest_mask: ee.Image,
) -> ee.Image:
    """
    Create a binary loss mask.

    Loss = pixel was forest BEFORE and is NOT forest AFTER.

    Parameters
    ----------
    before_forest_mask : ee.Image — binary, 'forest_mask' band, before date.
    after_forest_mask  : ee.Image — binary, 'forest_mask' band, after date.

    Returns
    -------
    ee.Image — binary (1=loss, 0=no loss), named 'loss_mask'.
    """
    # Loss = before is forest (1) AND after is not forest (0)
    loss = before_forest_mask.And(after_forest_mask.Not()).rename("loss_mask")
    return loss


def calculate_loss_area_hectares(
    loss_mask: ee.Image,
    geometry: ee.Geometry,
    scale: int = 10,
) -> Dict[str, float]:
    """
    Calculate loss area and total valid area in hectares.

    Parameters
    ----------
    loss_mask : ee.Image — binary loss mask, 'loss_mask' band.
    geometry  : ee.Geometry — analysis region.
    scale     : int — pixel scale in metres.

    Returns
    -------
    dict:
        loss_area_hectares   : float
        valid_area_hectares  : float  (total pixels analysed)
        loss_percentage      : float
    """
    pixel_area = ee.Image.pixelArea()

    loss_area_m2 = (
        loss_mask
        .multiply(pixel_area)
        .reduceRegion(
            reducer=ee.Reducer.sum(),
            geometry=geometry,
            scale=scale,
            maxPixels=1e10,
            bestEffort=True,
        )
        .get("loss_mask")
    )

    valid_area_m2 = (
        loss_mask
        .mask()
        .multiply(pixel_area)
        .reduceRegion(
            reducer=ee.Reducer.sum(),
            geometry=geometry,
            scale=scale,
            maxPixels=1e10,
            bestEffort=True,
        )
        .get("loss_mask")
    )

    result = ee.Dictionary({
        "loss_m2": loss_area_m2,
        "valid_m2": valid_area_m2,
    }).getInfo()

    loss_m2  = result.get("loss_m2")  or 0.0
    valid_m2 = result.get("valid_m2") or 1.0

    loss_ha  = round(loss_m2  / 10_000, 4)
    valid_ha = round(valid_m2 / 10_000, 4)
    loss_pct = round((loss_ha / valid_ha) * 100, 2) if valid_ha > 0 else 0.0

    return {
        "loss_area_hectares":  loss_ha,
        "valid_area_hectares": valid_ha,
        "loss_percentage":     loss_pct,
    }


def generate_loss_geojson(
    loss_mask: ee.Image,
    geometry: ee.Geometry,
    min_cluster_ha: float = 0.10,
    scale: int = 10,
) -> Optional[Dict[str, Any]]:
    """
    Convert the loss raster to a GeoJSON FeatureCollection of loss polygons.

    Small patches below ``min_cluster_ha`` are removed to reduce noise.

    Parameters
    ----------
    loss_mask      : ee.Image — binary loss mask.
    geometry       : ee.Geometry — analysis region.
    min_cluster_ha : float — minimum cluster size to keep.
    scale          : int

    Returns
    -------
    GeoJSON FeatureCollection dict, or None if no loss polygons found.
    """
    try:
        vectors = loss_mask.reduceToVectors(
            geometry=geometry,
            scale=scale,
            geometryType="polygon",
            eightConnected=True,
            maxPixels=1e10,
            bestEffort=True,
        )

        # Add area to each feature and filter small patches
        min_area_m2 = min_cluster_ha * 10_000

        def add_area(feature: ee.Feature) -> ee.Feature:
            area = feature.geometry().area(maxError=1)
            return feature.set("area_m2", area)

        vectors_with_area = vectors.map(add_area)
        filtered = vectors_with_area.filter(ee.Filter.gte("area_m2", min_area_m2))

        # Add semantic label to each polygon
        def label_feature(feature: ee.Feature) -> ee.Feature:
            area_ha = ee.Number(feature.get("area_m2")).divide(10_000)
            return feature.set({
                "change_type": "potential_forest_loss",
                "area_ha": area_ha,
            })

        labelled = filtered.map(label_feature)
        geojson = labelled.getInfo()

        if not geojson or not geojson.get("features"):
            return None

        return geojson

    except Exception as exc:
        # Return None rather than crashing the pipeline
        print(f"[loss_area] Warning: Could not generate loss GeoJSON: {exc}")
        return None


def run_loss_analysis(
    before_image: ee.Image,
    after_image: ee.Image,
    geometry: ee.Geometry,
    ndvi_threshold: float = 0.50,
    scale: int = 10,
    min_cluster_ha: float = 0.10,
) -> Dict[str, Any]:
    """
    Full loss analysis pipeline: masks → loss mask → area → GeoJSON.

    Parameters
    ----------
    before_image  : ee.Image — cloud-masked Sentinel-2, before date.
    after_image   : ee.Image — cloud-masked Sentinel-2, after date.
    geometry      : ee.Geometry — farm boundary.
    ndvi_threshold: float — forest NDVI threshold.
    scale         : int
    min_cluster_ha: float — minimum patch size to include.

    Returns
    -------
    dict with:
        forest_mask_before   : ee.Image
        forest_mask_after    : ee.Image
        loss_mask            : ee.Image
        forest_area_before_ha
        forest_area_after_ha
        forest_loss_hectares
        valid_area_hectares
        loss_percentage
        loss_geojson         : dict | None
    """
    from .forest_mask import get_forest_area_hectares

    # Create forest masks
    fm_before = create_forest_mask(before_image, ndvi_threshold=ndvi_threshold)
    fm_after  = create_forest_mask(after_image,  ndvi_threshold=ndvi_threshold)

    # Loss mask
    loss = detect_loss_mask(fm_before, fm_after)

    # Areas (executes GEE calls)
    fa_before = get_forest_area_hectares(fm_before, geometry, scale)
    fa_after  = get_forest_area_hectares(fm_after,  geometry, scale)
    loss_stats = calculate_loss_area_hectares(loss, geometry, scale)

    # GeoJSON polygons
    loss_geojson = generate_loss_geojson(loss, geometry, min_cluster_ha, scale)

    return {
        "forest_mask_before":  fm_before,
        "forest_mask_after":   fm_after,
        "loss_mask":           loss,
        "forest_area_before_ha": fa_before,
        "forest_area_after_ha":  fa_after,
        "forest_loss_hectares":  loss_stats["loss_area_hectares"],
        "valid_area_hectares":   loss_stats["valid_area_hectares"],
        "loss_percentage":       loss_stats["loss_percentage"],
        "loss_geojson":          loss_geojson,
    }
