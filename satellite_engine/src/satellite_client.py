"""
TerraWatch — satellite client.

High-level wrapper around image_processor and observation_manager.
Provides the before/after observation retrieval used by the pipeline.
"""

from typing import Any, Dict, Optional

import ee

from .gee_client import require_gee
from .image_processor import (
    get_sentinel2_collection,
    get_cloud_probability_collection,
    join_cloud_probability,
    apply_cloud_mask,
    get_true_color_thumb_url,
    DEFAULT_CLOUD_THRESHOLD,
)
from .observation_manager import (
    find_latest_usable_observation,
    find_observation_for_date,
    STATUS_NEW_OBSERVATION,
)
from .quality.quality_checker import assess_image_quality


class SatelliteClient:
    """
    Thin wrapper providing before/after observation retrieval.

    Usage
    -----
    client = SatelliteClient(project_id="my-gee-project")
    before = client.get_before_observation(geometry, start_date, end_date)
    after  = client.get_after_observation(geometry, previous_obs_date, end_date)
    """

    def __init__(
        self,
        project_id: Optional[str] = None,
        cloud_prob_threshold: int = DEFAULT_CLOUD_THRESHOLD,
    ) -> None:
        require_gee(project_id)
        self.cloud_prob_threshold = cloud_prob_threshold

    # ── Before observation ───────────────────────────────────────────────

    def get_before_observation(
        self,
        geometry: ee.Geometry,
        start_date: str,
        end_date: str,
        previous_observation_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Retrieve the 'before' observation.

        If a previous_observation_date is given, find the best image
        near that date (±5 days).  Otherwise use the best image in
        [start_date, end_date].

        Returns
        -------
        dict — same structure as find_latest_usable_observation.
        """
        if previous_observation_date:
            return find_observation_for_date(
                geometry,
                target_date=previous_observation_date,
                window_days=5,
                cloud_prob_threshold=self.cloud_prob_threshold,
            )

        # Use the oldest usable observation in the range as the baseline
        result = find_latest_usable_observation(
            geometry,
            after_date=_one_day_before(start_date),
            until_date=end_date,
            cloud_prob_threshold=self.cloud_prob_threshold,
        )
        return result

    # ── After (new) observation ──────────────────────────────────────────

    def get_after_observation(
        self,
        geometry: ee.Geometry,
        after_date: str,
        until_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Find the newest usable observation after ``after_date``.

        Parameters
        ----------
        geometry   : ee.Geometry
        after_date : str — search strictly after this date.
        until_date : str | None — search window end (defaults to today).

        Returns
        -------
        dict — same structure as find_latest_usable_observation.
        """
        return find_latest_usable_observation(
            geometry,
            after_date=after_date,
            until_date=until_date,
            cloud_prob_threshold=self.cloud_prob_threshold,
        )

    # ── Thumbnail URLs ───────────────────────────────────────────────────

    def get_thumbnail_url(
        self,
        image: ee.Image,
        geometry: ee.Geometry,
    ) -> Optional[str]:
        """Return a true-colour thumbnail URL for the given image."""
        return get_true_color_thumb_url(image, geometry)


# ── Private helper ────────────────────────────────────────────────────────────

def _one_day_before(date_str: str) -> str:
    from datetime import date, timedelta
    d = date.fromisoformat(date_str)
    return (d - timedelta(days=1)).isoformat()
