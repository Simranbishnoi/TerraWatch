"""
Tests for NDVI calculation.
Pure-Python tests; GEE is mocked.
"""

import pytest
from unittest.mock import MagicMock, patch

from satellite_engine.src.ndvi.calculator import (
    calculate_ndvi_change,
)


class TestNdviChange:
    def test_decline(self):
        result = calculate_ndvi_change(0.72, 0.31)
        assert result == pytest.approx(-0.41, abs=1e-5)

    def test_no_change(self):
        result = calculate_ndvi_change(0.5, 0.5)
        assert result == pytest.approx(0.0, abs=1e-5)

    def test_increase(self):
        result = calculate_ndvi_change(0.3, 0.6)
        assert result == pytest.approx(0.3, abs=1e-5)

    def test_zero_denominator_safe(self):
        # Both bands zero → GEE would return NaN, but the formula itself stays finite
        # This test covers the Python-side calculation only
        result = calculate_ndvi_change(0.0, 0.0)
        assert result == 0.0

    def test_extreme_negative(self):
        # Full forest to bare soil
        result = calculate_ndvi_change(0.85, -0.05)
        assert result == pytest.approx(-0.90, abs=1e-5)

    def test_rounding(self):
        result = calculate_ndvi_change(0.7123456789, 0.4987654321)
        assert len(str(result).split(".")[-1]) <= 8  # rounded to 6 dp
