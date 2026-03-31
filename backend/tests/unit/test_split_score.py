from __future__ import annotations

import pytest

from app.utils.split_score import compute_diffs, generate_coaching_notes
from app.utils.split_score_constants import POPULATION_STATS


def _mean_segments_ms(event_type: str, total_ms: float = 50_000.0) -> list[float]:
    """Build a segment list that sits exactly at the population mean."""
    means = POPULATION_STATS[event_type]["mean"]
    return [m / 100.0 * total_ms for m in means]


@pytest.mark.unit
class TestComputeDiffs:
    def test_mean_segments_return_zero_diff(self) -> None:
        total_ms = 50_000.0
        segments_ms = _mean_segments_ms("hurdles_400m", total_ms)
        result = compute_diffs(segments_ms, total_ms, "hurdles_400m")
        assert len(result) == 11
        for d in result:
            assert abs(d["diff_s"]) < 0.01, f"Expected ~0s diff, got {d['diff_s']}"
            assert abs(d["diff_pct"]) < 0.01, f"Expected ~0% diff, got {d['diff_pct']}"

    def test_slow_segments_have_positive_diff(self) -> None:
        total_ms = 50_000.0
        means = POPULATION_STATS["hurdles_400m"]["mean"]
        stds = POPULATION_STATS["hurdles_400m"]["std"]
        slow_pcts = [m + 2 * s for m, s in zip(means, stds, strict=True)]
        segments_ms = [p / 100.0 * total_ms for p in slow_pcts]
        result = compute_diffs(segments_ms, total_ms, "hurdles_400m")
        for d in result:
            assert d["diff_s"] > 0, (
                f"Expected positive diff for slow segment, got {d['diff_s']}"
            )

    def test_fast_segments_have_negative_diff(self) -> None:
        total_ms = 50_000.0
        means = POPULATION_STATS["hurdles_400m"]["mean"]
        stds = POPULATION_STATS["hurdles_400m"]["std"]
        fast_pcts = [m - 2 * s for m, s in zip(means, stds, strict=True)]
        segments_ms = [p / 100.0 * total_ms for p in fast_pcts]
        result = compute_diffs(segments_ms, total_ms, "hurdles_400m")
        for d in result:
            assert d["diff_s"] < 0, (
                f"Expected negative diff for fast segment, got {d['diff_s']}"
            )

    def test_sprint_400m_returns_four_diffs(self) -> None:
        total_ms = 45_000.0
        segments_ms = _mean_segments_ms("sprint_400m", total_ms)
        result = compute_diffs(segments_ms, total_ms, "sprint_400m")
        assert len(result) == 4

    def test_wrong_segment_count_raises_value_error(self) -> None:
        with pytest.raises(ValueError, match="Expected 11 segments"):
            compute_diffs([1000.0] * 5, 50_000.0, "hurdles_400m")

    def test_unsupported_event_raises_key_error(self) -> None:
        with pytest.raises(KeyError):
            compute_diffs([1000.0] * 4, 50_000.0, "hurdles_110m")


@pytest.mark.unit
class TestGenerateCoachingNotes:
    def _slow_diffs(self, n: int = 11, diff_s: float = 0.5) -> list[dict]:
        return [{"diff_s": diff_s, "diff_pct": 1.0}] + [
            {"diff_s": 0.0, "diff_pct": 0.0}
        ] * (n - 1)

    def _fast_diffs(self, n: int = 11, diff_s: float = -0.5) -> list[dict]:
        return [{"diff_s": diff_s, "diff_pct": -1.0}] + [
            {"diff_s": 0.0, "diff_pct": 0.0}
        ] * (n - 1)

    def _on_pace_diffs(self, n: int = 11) -> list[dict]:
        return [{"diff_s": 0.0, "diff_pct": 0.0}] * n

    def test_slow_segment_says_slower_than_average(self) -> None:
        notes = generate_coaching_notes(self._slow_diffs(), "hurdles_400m")
        assert "slower than average" in notes[0]
        assert "Start→H1" in notes[0]

    def test_fast_segment_says_faster_than_average(self) -> None:
        notes = generate_coaching_notes(self._fast_diffs(), "hurdles_400m")
        assert "faster than average" in notes[0]
        assert "Start→H1" in notes[0]

    def test_on_pace_segment_says_on_pace(self) -> None:
        notes = generate_coaching_notes(self._on_pace_diffs(), "hurdles_400m")
        assert all("on pace" in n for n in notes)

    def test_note_includes_diff_s_value(self) -> None:
        notes = generate_coaching_notes(self._slow_diffs(diff_s=0.31), "hurdles_400m")
        assert "0.31s" in notes[0]

    def test_note_includes_diff_pct_value(self) -> None:
        diffs = [{"diff_s": 0.31, "diff_pct": 4.0}] + [
            {"diff_s": 0.0, "diff_pct": 0.0}
        ] * 10
        notes = generate_coaching_notes(diffs, "hurdles_400m")
        assert "4.0%" in notes[0]

    def test_multiple_segments_flagged(self) -> None:
        diffs = [
            {"diff_s": 0.5, "diff_pct": 1.0},
            {"diff_s": -0.5, "diff_pct": -1.0},
        ] + [{"diff_s": 0.0, "diff_pct": 0.0}] * 9
        notes = generate_coaching_notes(diffs, "hurdles_400m")
        assert len(notes) == 11  # all segments get a note
        assert "slower than average" in notes[0]
        assert "faster than average" in notes[1]

    def test_sprint_400m_labels_used_correctly(self) -> None:
        diffs = [{"diff_s": 0.5, "diff_pct": 1.0}] + [
            {"diff_s": 0.0, "diff_pct": 0.0}
        ] * 3
        notes = generate_coaching_notes(diffs, "sprint_400m")
        assert "0-100m" in notes[0]
