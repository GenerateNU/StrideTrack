from __future__ import annotations

import pytest

from app.utils.split_score import compute_percentiles, generate_coaching_notes
from app.utils.split_score_constants import POPULATION_STATS


def _mean_segments_ms(event_type: str, total_ms: float = 50_000.0) -> list[float]:
    """Build a segment list that sits exactly at the population mean."""
    means = POPULATION_STATS[event_type]["mean"]
    return [m / 100.0 * total_ms for m in means]


@pytest.mark.unit
class TestComputePercentiles:
    def test_mean_segments_return_near_50th(self) -> None:
        total_ms = 50_000.0
        segments_ms = _mean_segments_ms("hurdles_400m", total_ms)
        result = compute_percentiles(segments_ms, total_ms, "hurdles_400m")
        assert len(result) == 11
        for pct in result:
            assert 45.0 <= pct <= 55.0, f"Expected ~50th, got {pct}"

    def test_slow_segments_above_50th(self) -> None:
        total_ms = 50_000.0
        means = POPULATION_STATS["hurdles_400m"]["mean"]
        stds = POPULATION_STATS["hurdles_400m"]["std"]
        slow_pcts = [m + 2 * s for m, s in zip(means, stds, strict=True)]
        segments_ms = [p / 100.0 * total_ms for p in slow_pcts]
        result = compute_percentiles(segments_ms, total_ms, "hurdles_400m")
        for pct in result:
            assert pct > 90.0, f"Expected >90th for 2-std-slow segment, got {pct}"

    def test_fast_segments_below_50th(self) -> None:
        total_ms = 50_000.0
        means = POPULATION_STATS["hurdles_400m"]["mean"]
        stds = POPULATION_STATS["hurdles_400m"]["std"]
        fast_pcts = [m - 2 * s for m, s in zip(means, stds, strict=True)]
        segments_ms = [p / 100.0 * total_ms for p in fast_pcts]
        result = compute_percentiles(segments_ms, total_ms, "hurdles_400m")
        for pct in result:
            assert pct < 10.0, f"Expected <10th for 2-std-fast segment, got {pct}"

    def test_sprint_400m_event_returns_four_percentiles(self) -> None:
        total_ms = 45_000.0
        segments_ms = _mean_segments_ms("sprint_400m", total_ms)
        result = compute_percentiles(segments_ms, total_ms, "sprint_400m")
        assert len(result) == 4

    def test_percentiles_bounded_0_to_100(self) -> None:
        total_ms = 50_000.0
        segments_ms = _mean_segments_ms("hurdles_400m", total_ms)
        result = compute_percentiles(segments_ms, total_ms, "hurdles_400m")
        for pct in result:
            assert 0.0 <= pct <= 100.0

    def test_wrong_segment_count_raises_value_error(self) -> None:
        with pytest.raises(ValueError, match="Expected 11 segments"):
            compute_percentiles([1000.0] * 5, 50_000.0, "hurdles_400m")

    def test_unsupported_event_raises_key_error(self) -> None:
        with pytest.raises(KeyError):
            compute_percentiles([1000.0] * 4, 50_000.0, "hurdles_110m")


@pytest.mark.unit
class TestGenerateCoachingNotes:
    def test_high_percentile_produces_significant_deceleration_note(self) -> None:
        percentiles = [90.0] + [50.0] * 10
        notes = generate_coaching_notes(percentiles, "hurdles_400m")
        assert len(notes) == 1
        assert "significant deceleration" in notes[0]
        assert "Start→H1" in notes[0]

    def test_moderate_percentile_produces_mild_deceleration_note(self) -> None:
        percentiles = [75.0] + [50.0] * 10
        notes = generate_coaching_notes(percentiles, "hurdles_400m")
        assert len(notes) == 1
        assert "mild deceleration" in notes[0]

    def test_low_percentile_produces_strong_segment_note(self) -> None:
        percentiles = [10.0] + [50.0] * 10
        notes = generate_coaching_notes(percentiles, "hurdles_400m")
        assert len(notes) == 1
        assert "strong segment" in notes[0]

    def test_mid_range_percentiles_produce_no_notes(self) -> None:
        percentiles = [50.0] * 11
        notes = generate_coaching_notes(percentiles, "hurdles_400m")
        assert notes == []

    def test_multiple_flagged_segments_produce_multiple_notes(self) -> None:
        percentiles = [90.0, 75.0, 10.0] + [50.0] * 8
        notes = generate_coaching_notes(percentiles, "hurdles_400m")
        assert len(notes) == 3

    def test_note_includes_correct_percentile_value(self) -> None:
        percentiles = [88.0] + [50.0] * 10
        notes = generate_coaching_notes(percentiles, "hurdles_400m")
        assert "88th" in notes[0]

    def test_sprint_400m_labels_used_correctly(self) -> None:
        percentiles = [90.0, 50.0, 50.0, 50.0]
        notes = generate_coaching_notes(percentiles, "sprint_400m")
        assert len(notes) == 1
        assert "0-100m" in notes[0]

    def test_boundary_85th_percentile_is_mild(self) -> None:
        percentiles = [85.0] + [50.0] * 10
        notes = generate_coaching_notes(percentiles, "hurdles_400m")
        assert len(notes) == 1
        assert "mild deceleration" in notes[0]

    def test_boundary_15th_percentile_is_not_strong(self) -> None:
        percentiles = [15.0] + [50.0] * 10
        notes = generate_coaching_notes(percentiles, "hurdles_400m")
        assert notes == []
