from __future__ import annotations

from app.schemas.split_score_schemas import SegmentDiff
from app.utils.split_score_constants import POPULATION_STATS, SEGMENT_LABELS


def compute_diffs(
    segments_ms: list[float],
    total_ms: float,
    event_type: str,
    gender: str = "male",
) -> list[SegmentDiff]:
    """Compute per-segment time differences vs. population mean percentages."""
    gender_key = gender if gender in ("male", "female") else "male"
    stats = POPULATION_STATS[gender_key][event_type]
    means = stats["mean"]

    if len(segments_ms) != len(means):
        raise ValueError(
            f"Expected {len(means)} segments for {event_type}, got {len(segments_ms)}."
        )

    diffs: list[SegmentDiff] = []
    for i, raw_ms in enumerate(segments_ms):
        athlete_pct = (raw_ms / total_ms) * 100.0
        diff_pct = athlete_pct - means[i]
        diff_s = (diff_pct / 100.0) * total_ms / 1000.0
        diffs.append(
            SegmentDiff(
                diff_s=round(diff_s, 2),
                diff_pct=round(diff_pct, 2),
            )
        )
    return diffs


def generate_coaching_notes(
    diffs: list[SegmentDiff],
    event_type: str,
    on_pace_threshold_s: float = 0.1,
) -> list[str]:
    """Generate human-readable coaching notes for each segment diff."""
    labels = SEGMENT_LABELS[event_type]
    notes: list[str] = []
    for diff, label in zip(diffs, labels, strict=True):
        diff_s = diff["diff_s"]
        diff_pct = diff["diff_pct"]
        abs_s = abs(diff_s)
        abs_pct = abs(diff_pct)
        if abs_s <= on_pace_threshold_s:
            notes.append(f"{label}: on pace")
        elif diff_s > 0:
            notes.append(
                f"{label}: {abs_s:.2f}s slower than average ({abs_pct:.1f}% slower)"
            )
        else:
            notes.append(
                f"{label}: {abs_s:.2f}s faster than average ({abs_pct:.1f}% faster)"
            )
    return notes
