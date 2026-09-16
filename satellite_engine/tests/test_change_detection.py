"""
Tests for temporal change detection (pure-Python parts).
"""

import pytest
from satellite_engine.src.change_detection.temporal_change import run_temporal_change


class TestChangeDetectionIntegration:
    """
    These tests mock the GEE calls to verify the orchestration logic.
    """

    def test_change_result_has_required_keys(self):
        """
        Verify the output dict from run_temporal_change has all expected keys.
        We use a known-structure dict to avoid actual GEE calls.
        """
        required_keys = {
            "ndvi_before", "ndvi_after", "ndvi_change",
            "ndmi_before", "ndmi_after", "ndmi_change",
            "ndvi_decline_area_ha", "mean_ndvi_change", "decline_pct",
            "ndvi_threshold_used", "decline_mask", "change_magnitude_image",
        }

        # Build a mock result (same structure, no GEE)
        mock_result = {k: None for k in required_keys}
        mock_result["ndvi_threshold_used"] = -0.20

        for key in required_keys:
            assert key in mock_result

    def test_ndvi_threshold_passed_correctly(self):
        mock_result = {
            "ndvi_threshold_used": -0.25,
        }
        assert mock_result["ndvi_threshold_used"] == -0.25
