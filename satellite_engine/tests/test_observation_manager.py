"""
Tests for observation_manager helpers (no GEE).
"""

import pytest
from datetime import date, timedelta
from satellite_engine.src.observation_manager import _next_day, _days_ahead, _no_new, STATUS_NO_NEW_OBSERVATION


class TestHelpers:
    def test_next_day(self):
        assert _next_day("2026-09-07") == "2026-09-08"

    def test_next_day_month_boundary(self):
        assert _next_day("2026-09-30") == "2026-10-01"

    def test_days_ahead(self):
        assert _days_ahead("2026-09-07", 5) == "2026-09-12"

    def test_days_ahead_zero(self):
        assert _days_ahead("2026-09-07", 0) == "2026-09-07"

    def test_no_new_returns_correct_status(self):
        result = _no_new("some message")
        assert result["status"] == STATUS_NO_NEW_OBSERVATION
        assert result["observation_date"] is None
        assert result["masked_image"] is None
        assert "some message" in result["message"]
