"""
Pure functions for split score percentile computation and coaching note generation.

Design: swap scipy.stats.percentileofscore (needs full population array at
runtime) for norm.cdf with precomputed mean + std. This lets us compute
percentiles from constants alone — no DB or file access at request time.
"""

from __future__ import annotations

from scipy.stats import norm

from app.utils.split_score_constants import POPULATION_STATS, SEGMENT_LABELS


def compute_percentiles(
    segments_ms: list[float],
    total_ms: float,
    event_type: str,
) -> list[float]:
    """
    Compute per-segment percentiles using a normal CDF against hardcoded constants.

    Each raw segment time is first normalized as a percentage of total race time,
    then placed on the population distribution (mean, std) for that segment index.

    Interpretation: a HIGH percentile means the athlete spent MORE time in that
    segment than the population — i.e., they were relatively slower there.

    Args:
        segments_ms: Raw segment durations in milliseconds, in order.
        total_ms: Official total race time in milliseconds.
        event_type: Must be a key in POPULATION_STATS (e.g. "400mH", "400m").

    Returns:
        List of percentile values (0.0–100.0), one per segment.

    Raises:
        KeyError: If event_type is not present in POPULATION_STATS.
        ValueError: If len(segments_ms) does not match the expected segment count.
    """
    stats = POPULATION_STATS[event_type]
    means = stats["mean"]
    stds = stats["std"]

    if len(segments_ms) != len(means):
        raise ValueError(
            f"Expected {len(means)} segments for {event_type}, got {len(segments_ms)}."
        )

    percentiles: list[float] = []
    for i, raw_ms in enumerate(segments_ms):
        pct_of_total = (raw_ms / total_ms) * 100.0
        z = (pct_of_total - means[i]) / stds[i]
        percentile = round(float(norm.cdf(z)) * 100, 1)
        percentiles.append(percentile)

    return percentiles


def generate_coaching_notes(
    percentiles: list[float],
    event_type: str,
) -> list[str]:
    """
    Generate human-readable coaching notes from per-segment percentiles.

    Percentile interpretation (higher = slower relative to population):
      > 85th  → significant deceleration, primary focus area
      > 70th  → mild deceleration, room for improvement
      < 15th  → strong segment, positive signal

    Args:
        percentiles: Per-segment percentile values from compute_percentiles().
        event_type: Used to look up segment labels.

    Returns:
        List of coaching note strings. Only flagged segments produce a note.
    """
    labels = SEGMENT_LABELS[event_type]
    notes: list[str] = []

    for pct, label in zip(percentiles, labels):
        if pct > 85:
            notes.append(
                f"{label}: {pct:.0f}th percentile — significant deceleration. "
                "Focus on maintaining pace here."
            )
        elif pct > 70:
            notes.append(
                f"{label}: {pct:.0f}th percentile — mild deceleration. "
                "Room for improvement."
            )
        elif pct < 15:
            notes.append(f"{label}: {pct:.0f}th percentile — strong segment.")

    return notes
