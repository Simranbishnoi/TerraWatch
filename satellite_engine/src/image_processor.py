"""
TerraWatch — Sentinel-2 image processing utilities.

Handles collection retrieval, cloud-probability joining,
cloud masking, and thumbnail URL generation.
"""

from typing import Any, Dict, List, Optional

import ee


# ── Constants ────────────────────────────────────────────────────────────────
S2_COLLECTION       = "COPERNICUS/S2_SR_HARMONIZED"
CLOUD_COLLECTION    = "COPERNICUS/S2_CLOUD_PROBABILITY"
DEFAULT_CLOUD_THRESHOLD = 50  # cloud_probability < 50 = clear pixel
DEFAULT_MAX_CLOUD_PCT   = 80  # pre-filter: skip images > 80% cloudy


# ── Collection retrieval ─────────────────────────────────────────────────────

def get_sentinel2_collection(
    geometry: ee.Geometry,
    start_date: str,
    end_date: str,
    max_cloud_pct: float = DEFAULT_MAX_CLOUD_PCT,
) -> ee.ImageCollection:
    """
    Retrieve a Sentinel-2 SR collection filtered to the ROI and dates.

    Parameters
    ----------
    geometry      : ee.Geometry
    start_date    : str — "YYYY-MM-DD"
    end_date      : str — "YYYY-MM-DD"
    max_cloud_pct : float — pre-filter threshold (image-level metadata)

    Returns
    -------
    ee.ImageCollection (unmasked at pixel level; sorted ascending by date)
    """
    return (
        ee.ImageCollection(S2_COLLECTION)
        .filterBounds(geometry)
        .filterDate(start_date, end_date)
        .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", max_cloud_pct))
        .sort("system:time_start")
    )


def get_cloud_probability_collection(
    geometry: ee.Geometry,
    start_date: str,
    end_date: str,
) -> ee.ImageCollection:
    """
    Retrieve the corresponding cloud-probability collection.
    """
    return (
        ee.ImageCollection(CLOUD_COLLECTION)
        .filterBounds(geometry)
        .filterDate(start_date, end_date)
    )


# ── Cloud-probability join ───────────────────────────────────────────────────

def join_cloud_probability(
    s2_collection: ee.ImageCollection,
    cloud_collection: ee.ImageCollection,
) -> ee.ImageCollection:
    """
    Join the Sentinel-2 collection with cloud-probability images
    using system:index as the join key.

    Each S2 image gains a 'cloud_prob_image' property containing
    the matching cloud-probability image.

    Parameters
    ----------
    s2_collection    : ee.ImageCollection — Sentinel-2 SR.
    cloud_collection : ee.ImageCollection — S2_CLOUD_PROBABILITY.

    Returns
    -------
    ee.ImageCollection — S2 images with 'cloud_prob_image' attached.
    """
    join = ee.Join.saveFirst("cloud_prob_image")
    condition = ee.Filter.equals(
        leftField="system:index",
        rightField="system:index",
    )
    return join.apply(s2_collection, cloud_collection, condition)


# ── Cloud masking ────────────────────────────────────────────────────────────

def apply_cloud_mask(image: ee.Image, cloud_prob_threshold: int = DEFAULT_CLOUD_THRESHOLD) -> ee.Image:
    """
    Mask cloudy pixels using the joined cloud-probability band.

    Parameters
    ----------
    image : ee.Image
        S2 image with 'cloud_prob_image' property (from join_cloud_probability).
    cloud_prob_threshold : int
        Pixels with probability < threshold are kept as clear.

    Returns
    -------
    ee.Image — cloud-masked S2 image.
    """
    cloud_prob_img = ee.Image(image.get("cloud_prob_image")).select("probability")
    is_clear = cloud_prob_img.lt(cloud_prob_threshold)
    return image.updateMask(is_clear)


def mask_collection(
    joined_collection: ee.ImageCollection,
    cloud_prob_threshold: int = DEFAULT_CLOUD_THRESHOLD,
) -> ee.ImageCollection:
    """Apply cloud masking to every image in the joined collection."""
    def _mask(image: ee.Image) -> ee.Image:
        return apply_cloud_mask(image, cloud_prob_threshold)
    return joined_collection.map(_mask)


# ── Image metadata ────────────────────────────────────────────────────────────

def get_image_date(image: ee.Image) -> str:
    """Return the observation date as 'YYYY-MM-DD' string."""
    millis = image.get("system:time_start")
    date_str = ee.Date(millis).format("YYYY-MM-dd").getInfo()
    return date_str


def get_image_id(image: ee.Image) -> str:
    """Return the full GEE image ID."""
    return image.get("system:id").getInfo()


def get_image_metadata(image: ee.Image) -> Dict[str, Any]:
    """
    Return basic metadata for a single Sentinel-2 image.
    Executes a single .getInfo() call.
    """
    result = ee.Dictionary({
        "date":          ee.Date(image.get("system:time_start")).format("YYYY-MM-dd"),
        "image_id":      image.get("system:id"),
        "cloud_pct_meta": image.get("CLOUDY_PIXEL_PERCENTAGE"),
    }).getInfo()

    return {
        "observation_date":       result.get("date"),
        "image_id":               result.get("image_id"),
        "cloud_pct_metadata":     result.get("cloud_pct_meta"),
    }


# ── Thumbnail / visualization ─────────────────────────────────────────────────

def get_true_color_thumb_url(
    image: ee.Image,
    geometry: ee.Geometry,
    dimensions: int = 512,
) -> Optional[str]:
    """
    Get a true-colour (RGB) thumbnail URL for display in the frontend.

    Parameters
    ----------
    image      : ee.Image — Sentinel-2 SR image.
    geometry   : ee.Geometry — region to crop the thumbnail to.
    dimensions : int — thumbnail dimension in pixels.

    Returns
    -------
    URL string or None on failure.
    """
    try:
        vis_params = {
            "min": 0,
            "max": 3000,
            "bands": ["B4", "B3", "B2"],
        }
        url = image.getThumbURL({
            "dimensions": dimensions,
            "region": geometry,
            **vis_params,
            "format": "jpg",
        })
        return url
    except Exception as exc:
        print(f"[image_processor] Warning: Could not generate thumbnail URL: {exc}")
        return None


def get_ndvi_thumb_url(
    image: ee.Image,
    geometry: ee.Geometry,
    dimensions: int = 512,
) -> Optional[str]:
    """Get an NDVI visualisation thumbnail URL."""
    try:
        ndvi = image.normalizedDifference(["B8", "B4"]).rename("NDVI")
        url = ndvi.getThumbURL({
            "dimensions": dimensions,
            "region": geometry,
            "min": -0.2,
            "max": 0.9,
            "palette": ["brown", "white", "green"],
            "format": "jpg",
        })
        return url
    except Exception as exc:
        print(f"[image_processor] Warning: Could not generate NDVI thumbnail URL: {exc}")
        return None
