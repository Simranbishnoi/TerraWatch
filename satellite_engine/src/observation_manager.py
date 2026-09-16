"""
TerraWatch — observation manager.

Heart of the 5-day monitoring system.

Queries Google Earth Engine for Sentinel-2 observations after a given
date, applies cloud/quality filters, and returns the newest usable
observation — or NO_NEW_OBSERVATION if none qualifies.

The monitoring logic is observation-based, NOT calendar-date-based.
Sentinel-2 has a nominal 5-day revisit but clouds can prevent a
usable observation from being available on any given window.
"""

from datetime import date, timedelta
from typing import Any, Dict, List, Optional

import ee

from .image_processor import (
    get_sentinel2_collection,
    get_cloud_probability_collection,
    join_cloud_probability,
    apply_cloud_mask,
    get_image_metadata,
    DEFAULT_CLOUD_THRESHOLD,
    DEFAULT_MAX_CLOUD_PCT,
)
from .quality.quality_checker import assess_image_quality, is_observation_usable


# ── Status constants ─────────────────────────────────────────────────────────
STATUS_NEW_OBSERVATION    = "NEW_OBSERVATION"
STATUS_NO_NEW_OBSERVATION = "NO_NEW_OBSERVATION"
STATUS_NO_USABLE          = "NO_USABLE_OBSERVATION"


def find_latest_usable_observation(
    geometry: ee.Geometry,
    after_date: str,
    until_date: Optional[str] = None,
    cloud_prob_threshold: int = DEFAULT_CLOUD_THRESHOLD,
    max_cloud_pct: float = DEFAULT_MAX_CLOUD_PCT,
    search_window_days: int = 30,
) -> Dict[str, Any]:
    """
    Find the most recent usable Sentinel-2 observation after ``after_date``.

    Parameters
    ----------
    geometry             : ee.Geometry — farm boundary.
    after_date           : str — "YYYY-MM-DD" — search AFTER this date.
    until_date           : str | None — search until this date (defaults to today).
    cloud_prob_threshold : int — cloud-probability threshold for pixel masking.
    max_cloud_pct        : float — pre-filter: skip images > this% cloudy.
    search_window_days   : int — look-forward window if until_date is None.

    Returns
    -------
    dict with:
        status           : "NEW_OBSERVATION" | "NO_NEW_OBSERVATION" | "NO_USABLE_OBSERVATION"
        observation_date : str | None
        image_id         : str | None
        quality          : dict | None
        masked_image     : ee.Image | None   (for pipeline use, NOT serialisable)
        raw_image        : ee.Image | None   (unmasked, for metadata)
    """
    # Determine search window
    start = _next_day(after_date)
    end   = until_date or _days_ahead(after_date, search_window_days)

    if start >= end:
        return _no_new(f"No time window between {start} and {end}.")

    # Build collections
    s2_col    = get_sentinel2_collection(geometry, start, end, max_cloud_pct)
    cloud_col = get_cloud_probability_collection(geometry, start, end)

    # Check if any images exist at all
    count = s2_col.size().getInfo()
    if count == 0:
        return _no_new(f"No Sentinel-2 images found between {start} and {end}.")

    # Join cloud probability
    joined = join_cloud_probability(s2_col, cloud_col)

    # Iterate from newest to oldest; return the first usable image
    image_list = joined.sort("system:time_start", False).toList(count)

    for i in range(count):
        try:
            candidate = ee.Image(image_list.get(i))
            masked    = apply_cloud_mask(candidate, cloud_prob_threshold)
            quality   = assess_image_quality(masked, geometry)

            if is_observation_usable(quality):
                meta = get_image_metadata(candidate)
                return {
                    "status":           STATUS_NEW_OBSERVATION,
                    "observation_date": meta["observation_date"],
                    "image_id":         meta["image_id"],
                    "quality":          quality,
                    "masked_image":     masked,
                    "raw_image":        candidate,
                }
        except Exception as exc:
            print(f"[observation_manager] Warning: skipping image {i}: {exc}")
            continue

    return {
        "status":           STATUS_NO_USABLE,
        "observation_date": None,
        "image_id":         None,
        "quality":          None,
        "masked_image":     None,
        "raw_image":        None,
        "message":          "Candidate images did not meet quality requirements.",
    }


def find_observation_for_date(
    geometry: ee.Geometry,
    target_date: str,
    window_days: int = 5,
    cloud_prob_threshold: int = DEFAULT_CLOUD_THRESHOLD,
) -> Dict[str, Any]:
    """
    Find the best usable observation within ±window_days of target_date.

    Used to retrieve the 'before' observation when a previous observation
    date is known.

    Parameters
    ----------
    geometry          : ee.Geometry
    target_date       : str — "YYYY-MM-DD"
    window_days       : int — search ± this many days around target.
    cloud_prob_threshold : int

    Returns
    -------
    Same structure as find_latest_usable_observation.
    """
    d = date.fromisoformat(target_date)
    start = (d - timedelta(days=window_days)).isoformat()
    end   = (d + timedelta(days=window_days + 1)).isoformat()

    s2_col    = get_sentinel2_collection(geometry, start, end)
    cloud_col = get_cloud_probability_collection(geometry, start, end)

    count = s2_col.size().getInfo()
    if count == 0:
        return _no_new(f"No Sentinel-2 image found near {target_date}.")

    joined     = join_cloud_probability(s2_col, cloud_col)
    image_list = joined.sort("system:time_start", False).toList(count)

    for i in range(count):
        try:
            candidate = ee.Image(image_list.get(i))
            masked    = apply_cloud_mask(candidate, cloud_prob_threshold)
            quality   = assess_image_quality(masked, geometry)

            if is_observation_usable(quality):
                meta = get_image_metadata(candidate)
                return {
                    "status":           STATUS_NEW_OBSERVATION,
                    "observation_date": meta["observation_date"],
                    "image_id":         meta["image_id"],
                    "quality":          quality,
                    "masked_image":     masked,
                    "raw_image":        candidate,
                }
        except Exception:
            continue

    return _no_new(f"No usable observation near {target_date} (±{window_days} days).")


def list_observations(
    geometry: ee.Geometry,
    start_date: str,
    end_date: str,
    max_cloud_pct: float = DEFAULT_MAX_CLOUD_PCT,
) -> List[Dict[str, Any]]:
    """
    List all Sentinel-2 observations (metadata only) in a date range.
    Does NOT apply cloud masking — useful for browsing available imagery.

    Returns
    -------
    List of dicts with observation_date, image_id, cloud_pct_metadata.
    """
    s2_col = get_sentinel2_collection(geometry, start_date, end_date, max_cloud_pct)
    count  = s2_col.size().getInfo()
    if count == 0:
        return []

    image_list = s2_col.sort("system:time_start").toList(count)
    observations = []

    for i in range(count):
        try:
            img  = ee.Image(image_list.get(i))
            meta = get_image_metadata(img)
            observations.append(meta)
        except Exception:
            continue

    return observations


# ── Private helpers ───────────────────────────────────────────────────────────

def _next_day(date_str: str) -> str:
    d = date.fromisoformat(date_str)
    return (d + timedelta(days=1)).isoformat()


def _days_ahead(date_str: str, days: int) -> str:
    d = date.fromisoformat(date_str)
    return (d + timedelta(days=days)).isoformat()


def _no_new(message: str) -> Dict[str, Any]:
    return {
        "status":           STATUS_NO_NEW_OBSERVATION,
        "observation_date": None,
        "image_id":         None,
        "quality":          None,
        "masked_image":     None,
        "raw_image":        None,
        "message":          message,
    }
