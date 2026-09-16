"""
Tests for quality checker (mocked GEE).
"""

import pytest
from satellite_engine.src.quality.quality_checker import (
    assess_image_quality,
    is_observation_usable,
    QUALITY_HIGH,
    QUALITY_MEDIUM,
    QUALITY_LOW,
    QUALITY_REJECTED,
)


def _fake_quality(usable_pct: float) -> dict:
    """Build a fake quality result dict without calling GEE."""
    total = 1000
    valid = int(total * usable_pct / 100)

    if usable_pct >= 85:
        level = QUALITY_HIGH
    elif usable_pct >= 70:
        level = QUALITY_MEDIUM
    elif usable_pct >= 50:
        level = QUALITY_LOW
    else:
        level = QUALITY_REJECTED

    return {
        "quality_level":        level,
        "usable_pixel_pct":     usable_pct,
        "total_pixels":         total,
        "valid_pixels":         valid,
        "cloud_prob_threshold": 50.0,
        "is_usable":            level in (QUALITY_HIGH, QUALITY_MEDIUM),
    }


class TestQualityClassification:
    @pytest.mark.parametrize("pct,expected_level", [
        (95.0, QUALITY_HIGH),
        (85.0, QUALITY_HIGH),
        (80.0, QUALITY_MEDIUM),
        (70.0, QUALITY_MEDIUM),
        (60.0, QUALITY_LOW),
        (50.0, QUALITY_LOW),
        (49.9, QUALITY_REJECTED),
        (0.0,  QUALITY_REJECTED),
    ])
    def test_level_classification(self, pct, expected_level):
        q = _fake_quality(pct)
        assert q["quality_level"] == expected_level

    def test_high_is_usable(self):
        q = _fake_quality(90.0)
        assert is_observation_usable(q) is True

    def test_medium_is_usable(self):
        q = _fake_quality(75.0)
        assert is_observation_usable(q) is True

    def test_low_is_not_usable(self):
        q = _fake_quality(60.0)
        assert is_observation_usable(q) is False

    def test_rejected_is_not_usable(self):
        q = _fake_quality(30.0)
        assert is_observation_usable(q) is False
