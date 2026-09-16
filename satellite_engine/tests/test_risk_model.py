"""
Tests for risk model (rule-based, pure-Python).
"""

import pytest
from satellite_engine.src.ml.risk_model import predict_risk, _rule_based_score, _score_to_level


def _features(**overrides):
    defaults = {
        "ndvi_before": 0.72, "ndvi_after": 0.72, "ndvi_change": 0.0,
        "ndmi_before": 0.3,  "ndmi_after": 0.3,  "ndmi_change": 0.0,
        "forest_loss_hectares": 0.0, "loss_percentage": 0.0,
        "forest_area_before_ha": 80.0, "forest_area_after_ha": 80.0,
        "usable_pixel_pct": 95.0,
        "boundary_overlap_pct": 100.0, "excluded_loss_ha": 0.0, "inside_loss_ha": 0.0,
        "ndvi_decline_area_ha": 0.0, "decline_pct": 0.0, "observation_gap_days": 5.0,
    }
    defaults.update(overrides)
    return defaults


class TestRuleBasedScore:
    def test_no_change_gives_low_risk(self):
        score, level = _rule_based_score(_features())
        assert score < 30
        assert level == "LOW"

    def test_strong_ndvi_decline_raises_score(self):
        score, level = _rule_based_score(_features(ndvi_change=-0.40))
        assert score >= 35

    def test_large_loss_raises_score(self):
        score, level = _rule_based_score(_features(forest_loss_hectares=15.0))
        assert score >= 35

    def test_boundary_exclusion_raises_score(self):
        score, _ = _rule_based_score(_features(
            forest_loss_hectares=10.0,
            inside_loss_ha=2.0,
            excluded_loss_ha=8.0,
        ))
        assert score > _rule_based_score(_features(forest_loss_hectares=10.0, inside_loss_ha=10.0))[0]

    def test_very_high_risk(self):
        level = _score_to_level(90.0)
        assert level == "VERY_HIGH"

    def test_medium_risk(self):
        level = _score_to_level(45.0)
        assert level == "MEDIUM"

    def test_predict_risk_no_model(self):
        result = predict_risk(_features())
        assert result["model_status"] == "RULE_BASED"
        assert result["rule_score"] is not None
        assert result["final_score"] is None   # no ML model loaded

    def test_no_fake_hardcoded_score(self):
        """Ensure result is derived from features, not hardcoded."""
        r1 = predict_risk(_features(ndvi_change=0.0))
        r2 = predict_risk(_features(ndvi_change=-0.40))
        assert r2["rule_score"] > r1["rule_score"]
