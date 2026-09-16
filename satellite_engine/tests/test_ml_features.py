"""
Tests for ML feature builder.
"""

import pytest
from satellite_engine.src.ml.feature_builder import (
    build_features,
    features_to_vector,
    calculate_observation_gap,
    FEATURE_NAMES,
)


class TestBuildFeatures:
    def _sample_features(self, **overrides):
        defaults = dict(
            ndvi_before=0.72, ndvi_after=0.31, ndvi_change=-0.41,
            ndmi_before=0.3,  ndmi_after=0.1,  ndmi_change=-0.2,
            forest_loss_ha=12.4, loss_pct=15.2,
            forest_area_before=80.0, forest_area_after=67.6,
            usable_pixel_pct=94.2,
            overlap_pct=74.2, excluded_loss_ha=3.2, inside_loss_ha=9.2,
            decline_area_ha=10.0, decline_pct=12.5,
            observation_gap_days=5,
        )
        defaults.update(overrides)
        return build_features(**defaults)

    def test_returns_all_feature_names(self):
        f = self._sample_features()
        for name in FEATURE_NAMES:
            assert name in f

    def test_none_values_preserved(self):
        f = self._sample_features(ndvi_before=None)
        assert f["ndvi_before"] is None

    def test_to_vector_length(self):
        f = self._sample_features()
        vec = features_to_vector(f)
        assert len(vec) == len(FEATURE_NAMES)

    def test_none_imputed_as_zero_in_vector(self):
        f = self._sample_features(ndvi_before=None)
        vec = features_to_vector(f)
        idx = FEATURE_NAMES.index("ndvi_before")
        assert vec[idx] == 0.0

    def test_gap_calculation(self):
        assert calculate_observation_gap("2026-09-07", "2026-09-12") == 5
        assert calculate_observation_gap("2026-08-01", "2026-09-01") == 31
