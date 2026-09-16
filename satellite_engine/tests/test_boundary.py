"""
Tests for boundary overlap and exclusion analysis (pure-Python).
"""

import pytest
from satellite_engine.src.boundary.exclusion import analyze_boundary_exclusion


class TestBoundaryExclusion:
    def _overlap(self, total_ha, inside_ha):
        outside_ha = max(0.0, total_ha - inside_ha)
        return {
            "total_detected_loss_ha": total_ha,
            "inside_loss_ha":         inside_ha,
            "outside_loss_ha":        outside_ha,
            "overlap_percentage":     round(inside_ha / total_ha * 100, 2) if total_ha else 0.0,
            "outside_percentage":     round(outside_ha / total_ha * 100, 2) if total_ha else 0.0,
        }

    def test_all_inside_boundary(self):
        result = analyze_boundary_exclusion(self._overlap(10.0, 10.0))
        assert result["boundary_manipulation_score"] == 0.0
        assert result["assessment"] == "CONSISTENT_WITH_BOUNDARY"

    def test_all_outside_boundary(self):
        result = analyze_boundary_exclusion(self._overlap(10.0, 0.0))
        assert result["boundary_manipulation_score"] == 1.0
        assert result["assessment"] == "REQUIRES_BOUNDARY_VERIFICATION"

    def test_minor_discrepancy(self):
        result = analyze_boundary_exclusion(self._overlap(10.0, 9.5))
        assert result["boundary_manipulation_score"] < 0.10
        assert result["assessment"] == "CONSISTENT_WITH_BOUNDARY"

    def test_notable_discrepancy(self):
        result = analyze_boundary_exclusion(self._overlap(10.0, 6.0))
        assert 0.30 <= result["boundary_manipulation_score"] <= 0.60

    def test_no_loss_detected(self):
        result = analyze_boundary_exclusion(self._overlap(0.0, 0.0))
        assert result["assessment"] == "NO_LOSS_DETECTED"
        assert result["boundary_manipulation_score"] == 0.0
