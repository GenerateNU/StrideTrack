from __future__ import annotations

import math

from app.utils.split_score_constants import POPULATION_STATS, SEGMENT_LABELS


def compute_percentiles(
    segments_ms: list[float],
    total_ms: float,
    event_type: str,
) -> list[float]:
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
        percentile = round(0.5 * (1 + math.erf(z / math.sqrt(2))) * 100, 1)
        percentiles.append(percentile)
    return percentiles


def generate_coaching_notes(
    percentiles: list[float],
    event_type: str,
) -> list[str]:
    labels = SEGMENT_LABELS[event_type]
    notes: list[str] = []
    for pct, label in zip(percentiles, labels, strict=True):
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
