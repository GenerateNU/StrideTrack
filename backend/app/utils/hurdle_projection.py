from __future__ import annotations

import numpy as np

from app.schemas.hurdle_schemas import HurdleMetricRow

# Expected hurdle count and fixed final segment time.
EVENT_CONFIG: dict[str, dict[str, int]] = {
    "hurdles_60m": {"hurdle_count": 5, "final_segment_ms": 1000},
    "hurdles_100m": {"hurdle_count": 10, "final_segment_ms": 1300},
    "hurdles_110m": {"hurdle_count": 10, "final_segment_ms": 1400},
    "hurdles_400m": {"hurdle_count": 10, "final_segment_ms": 4500},
}


def _fit_linear_trend(
    hurdle_nums: np.ndarray, split_values: np.ndarray
) -> tuple[float, float]:
    """
    Fit a simple linear regression: split_ms = slope * hurdle_num + intercept.
    Returns (slope, intercept).
    """
    coeffs = np.polyfit(hurdle_nums, split_values, deg=1)
    return float(coeffs[0]), float(coeffs[1])


def _compute_confidence(completed: int, total: int) -> float:
    """
    Confidence score 0-1 that degrades with fewer completed hurdles.
    At least 2 hurdles needed for a trend; confidence scales with
    the fraction completed, with a bonus for having more data points.
    """
    if completed < 2 or total == 0:
        return 0.0

    fraction = completed / total
    data_quality = min(1.0, (completed - 1) / (total / 2))

    return round(min(1.0, fraction * 0.7 + data_quality * 0.3), 2)


def project_hurdle_race(
    completed_metrics: list[HurdleMetricRow],
    target_event: str,
) -> dict:
    """
    Project total race time from partial hurdle data.
    """
    if target_event not in EVENT_CONFIG:
        raise ValueError(
            f"Unknown target event '{target_event}'. "
            f"Must be one of {sorted(EVENT_CONFIG.keys())}"
        )

    config = EVENT_CONFIG[target_event]
    total_hurdles = config["hurdle_count"]
    final_segment_ms = config["final_segment_ms"]

    # Extract completed splits
    completed_splits: list[dict] = []
    for m in completed_metrics:
        if m.hurdle_split_ms is not None:
            completed_splits.append(
                {"hurdle_num": m.hurdle_num, "split_ms": m.hurdle_split_ms}
            )

    num_completed = len(completed_splits)

    # Need at least 2 splits to fit a trend
    if num_completed < 2:
        return {
            "completed_splits": completed_splits,
            "projected_splits": [],
            "projected_final_segment_ms": final_segment_ms,
            "projected_total_ms": None,
            "confidence": 0.0,
            "target_event": target_event,
            "total_hurdles": total_hurdles,
        }

    # Fit linear trend to completed splits
    hurdle_nums = np.array([s["hurdle_num"] for s in completed_splits])
    split_values = np.array([s["split_ms"] for s in completed_splits])
    slope, intercept = _fit_linear_trend(hurdle_nums, split_values)

    projected_splits: list[dict] = []
    remaining_start = max(s["hurdle_num"] for s in completed_splits) + 1

    for h in range(remaining_start, total_hurdles):
        projected_ms = max(0, int(round(slope * h + intercept)))
        projected_splits.append({"hurdle_num": h, "split_ms": projected_ms})

    # Sum up total time
    first_clearance_ms = (
        completed_metrics[0].clearance_start_ms if completed_metrics else 0
    )

    completed_total = sum(s["split_ms"] for s in completed_splits)
    projected_total = sum(s["split_ms"] for s in projected_splits)

    projected_total_ms = (
        first_clearance_ms + completed_total + projected_total + final_segment_ms
    )

    confidence = _compute_confidence(num_completed, total_hurdles - 1)

    return {
        "completed_splits": completed_splits,
        "projected_splits": projected_splits,
        "projected_final_segment_ms": final_segment_ms,
        "projected_total_ms": projected_total_ms,
        "confidence": confidence,
        "target_event": target_event,
        "total_hurdles": total_hurdles,
    }
