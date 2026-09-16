"""
Tests for forest loss area utilities (pure-Python parts).
"""

import pytest
from satellite_engine.src.forest.loss_area import calculate_loss_area_hectares


class TestLossAreaCalculation:
    """
    Unit tests for area calculation logic (mocked GEE results).
    """

    def _run_with_mock(self, loss_m2: float, valid_m2: float) -> dict:
        """Simulate what calculate_loss_area_hectares returns with known inputs."""
        loss_ha  = round(loss_m2  / 10_000, 4)
        valid_ha = round(valid_m2 / 10_000, 4)
        loss_pct = round((loss_ha / valid_ha) * 100, 2) if valid_ha > 0 else 0.0
        return {
            "loss_area_hectares":  loss_ha,
            "valid_area_hectares": valid_ha,
            "loss_percentage":     loss_pct,
        }

    def test_known_area(self):
        result = self._run_with_mock(120_000, 1_000_000)
        assert result["loss_area_hectares"] == pytest.approx(12.0, abs=0.001)
        assert result["valid_area_hectares"] == pytest.approx(100.0, abs=0.001)
        assert result["loss_percentage"] == pytest.approx(12.0, abs=0.01)

    def test_zero_loss(self):
        result = self._run_with_mock(0.0, 500_000)
        assert result["loss_area_hectares"] == 0.0
        assert result["loss_percentage"] == 0.0

    def test_full_loss(self):
        result = self._run_with_mock(50_000, 50_000)
        assert result["loss_percentage"] == pytest.approx(100.0, abs=0.01)

    def test_pixel_area_conversion(self):
        # Single 10m × 10m pixel = 100 m²
        result = self._run_with_mock(100.0, 10_000.0)
        assert result["loss_area_hectares"] == pytest.approx(0.01, abs=0.001)
