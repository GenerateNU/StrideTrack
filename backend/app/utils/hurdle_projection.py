from __future__ import annotations

import numpy as np

from app.schemas.hurdle_schemas import HurdleMetricRow



# The athlete covers ground faster per metre than during hurdled segments.
SPRINT_SCALAR: float = 0.98

# Per-event race parameters and normalised three-phase split templates
EVENT_CONFIG: dict[str, dict] = {
    "hurdles_60m": {
        "hurdle_count": 5,
        "inter_hurdle_m": 9.14,
        "final_segment_m": 8.72, # 9.72m, ~1m landing offset
        "phase_boundaries": (3, 4),
        "template_ratios": [0.0, 1.03, 1.00, 0.98, 0.99],
    },
    "hurdles_100m": {
        "hurdle_count": 10,
        "inter_hurdle_m": 8.50,
        "final_segment_m": 9.50, # 10.50m, ~1m landing offset
        "phase_boundaries": (4, 7),
        "template_ratios": [
            0.0,
            1.02, 1.00, 0.98, # acceleration  (H1-H3)
            0.98, 0.98, 0.99, # peak speed    (H4-H6)
            1.00, 1.02, 1.03, # fatigue       (H7-H9)
        ],
    },
    "hurdles_110m": {
        "hurdle_count": 10,
        "inter_hurdle_m": 9.14,
        "final_segment_m": 13.02, # 14.02m, ~1m landing offset
        "phase_boundaries": (4, 7),
        "template_ratios": [
            0.0,
            1.02, 1.00, 0.98,
            0.98, 0.98, 0.99,
            1.00, 1.02, 1.03,
        ],
    },
    "hurdles_400m": {
        "hurdle_count": 10,
        "inter_hurdle_m": 35.0,
        "final_segment_m": 39.0, # 40m, ~1m landing offset
        "phase_boundaries": (4, 7),
        "template_ratios": [
            0.0,
            1.03, 1.00, 0.97,
            0.96, 0.96, 0.97,
            0.99, 1.03, 1.09,
        ],
    },
}


def _get_phase(hurdle_idx: int, boundaries: tuple[int, int]) -> int:
    """Map a 0-based hurdle index to its phase. 0 (accel), 1 (peak), or 2 (fatigue)."""
    if hurdle_idx < boundaries[0]:
        return 0
    if hurdle_idx < boundaries[1]:
        return 1
    return 2


def _phases_covered(observed_indices: list[int], boundaries: tuple[int, int]) -> int:
    """Count how many distinct phases the observed hurdle indices span."""
    return len({_get_phase(i, boundaries) for i in observed_indices})


def _fit_phase_trends(
    hurdle_indices: np.ndarray,
    split_values: np.ndarray,
    boundaries: tuple[int, int],
) -> dict[int, tuple[float, float]]:
    """Fit a separate linear trend per phase where 2 or more data points exist."""
    trends: dict[int, tuple[float, float]] = {}

    for phase_id in (0, 1, 2):
        mask = np.array([_get_phase(int(i), boundaries) == phase_id for i in hurdle_indices])
        if mask.sum() >= 2:
            coeffs = np.polyfit(hurdle_indices[mask], split_values[mask], deg=1)
            trends[phase_id] = (float(coeffs[0]), float(coeffs[1]))

    return trends


def _scale_template(
    template_ratios: list[float],
    completed_splits: list[dict],
) -> list[float]:
    """Compute a least-squares scaling factor that fits the template ratios to the observed splits. Applies
    that factor to the full template so projections are anchored to actual performance."""
    observed_ratios = np.array([template_ratios[s["hurdle_num"]] for s in completed_splits])
    observed_values = np.array([s["split_ms"] for s in completed_splits])

    # Least-squares scaling factor
    scale_factor = float(np.dot(observed_ratios, observed_values) / np.dot(observed_ratios, observed_ratios))

    return [r * scale_factor for r in template_ratios]


def _blend_projection(
    hurdle_idx: int,
    last_observed_idx: int,
    phase_trends: dict[int, tuple[float, float]],
    boundaries: tuple[int, int],
    scaled_template: list[float],
) -> float:
    """Blend the athlete's per-phase trend with the scaled template, weighting the athlete more for nearby
    hurdles and falling back to the template for distant or unobserved phases."""
    distance = hurdle_idx - last_observed_idx

    phase = _get_phase(hurdle_idx, boundaries)
    template_ms = scaled_template[hurdle_idx]

    if phase not in phase_trends:
        # No athlete data in this phase, rely fully on template
        return template_ms

    slope, intercept = phase_trends[phase]
    athlete_ms = slope * hurdle_idx + intercept

    # Athlete weight decays with distance from observed data
    w_athlete = max(0.20, 1.0 - 0.18 * distance)

    return w_athlete * athlete_ms + (1 - w_athlete) * template_ms


def _compute_confidence(
    num_completed: int,
    total_hurdles: int,
    phases_covered: int,
) -> float:
    """Score 0-1 based on fraction completed (40%), data quality (30%), and phase coverage (30%). Returns
    0 if fewer than 2 hurdles completed."""
    if num_completed < 2 or total_hurdles == 0:
        return 0.0

    fraction = num_completed / total_hurdles
    data_quality = min(1.0, (num_completed - 1) / (total_hurdles / 2))
    phase_score = phases_covered / 3.0

    raw = fraction * 0.40 + data_quality * 0.30 + phase_score * 0.30
    return round(min(1.0, raw), 2)


def _estimate_final_segment(
    all_splits_ms: list[int],
    inter_hurdle_m: float,
    final_segment_m: float,
) -> int:
    """Derive the final segment time from the athlete's late-race pace, scaled down by SPRINT_SCALAR since
    there are no hurdles to clear."""
    if not all_splits_ms:
        return 0

    # Use the last 2 splits (or all if fewer) to capture late-race pace
    late_splits = all_splits_ms[-2:] if len(all_splits_ms) >= 2 else all_splits_ms
    avg_late_ms = sum(late_splits) / len(late_splits)

    ms_per_m = avg_late_ms / inter_hurdle_m
    return int(round(ms_per_m * final_segment_m * SPRINT_SCALAR))


def project_hurdle_race(
    completed_metrics: list[HurdleMetricRow],
    target_event: str,
) -> dict:
    """Project total race time from partial hurdle data. Keeps completed splits as-is, fits a template
    to observed data, and blends with per-phase trends to project remaining hurdles."""
    if target_event not in EVENT_CONFIG:
        raise ValueError(
            f"Unknown target event '{target_event}'. "
            f"Must be one of {sorted(EVENT_CONFIG.keys())}"
        )

    config = EVENT_CONFIG[target_event]
    total_hurdles: int = config["hurdle_count"]
    inter_hurdle_m: float = config["inter_hurdle_m"]
    final_segment_m: float = config["final_segment_m"]
    boundaries: tuple[int, int] = config["phase_boundaries"]
    template_ratios: list[float] = config["template_ratios"]

    # Extract completed splits
    completed_splits: list[dict] = []
    for m in completed_metrics:
        if m.hurdle_split_ms is not None:
            completed_splits.append(
                {"hurdle_num": m.hurdle_num, "split_ms": m.hurdle_split_ms}
            )

    num_completed = len(completed_splits)

    if num_completed < 2:
        return {
            "completed_splits": completed_splits,
            "projected_splits": [],
            "projected_final_segment_ms": None,
            "projected_total_ms": None,
            "confidence": 0.0,
            "target_event": target_event,
            "total_hurdles": total_hurdles,
        }

    hurdle_indices = np.array([s["hurdle_num"] for s in completed_splits])
    split_values = np.array([s["split_ms"] for s in completed_splits])

    # Phase-aware fitting
    phase_trends = _fit_phase_trends(hurdle_indices, split_values, boundaries)

    # Scale template to athlete's observed splits
    scaled_template = _scale_template(template_ratios, completed_splits)

    # Project remaining hurdles
    last_observed_idx = int(hurdle_indices.max())
    remaining_start = last_observed_idx + 1

    projected_splits: list[dict] = []
    for h in range(remaining_start, total_hurdles):
        proj_ms = _blend_projection(
            hurdle_idx=h,
            last_observed_idx=last_observed_idx,
            phase_trends=phase_trends,
            boundaries=boundaries,
            scaled_template=scaled_template,
        )
        projected_splits.append({
            "hurdle_num": h,
            "split_ms": max(0, int(round(proj_ms))),
        })

    # Estimate final segment from athlete's pace
    all_split_values = (
        [s["split_ms"] for s in completed_splits]
        + [s["split_ms"] for s in projected_splits]
    )
    final_segment_ms = _estimate_final_segment(
        all_split_values, inter_hurdle_m, final_segment_m,
    )

    # Total time
    first_clearance_ms = (
        completed_metrics[0].clearance_start_ms if completed_metrics else 0
    )
    completed_total = sum(s["split_ms"] for s in completed_splits)
    projected_total = sum(s["split_ms"] for s in projected_splits)

    projected_total_ms = (
        first_clearance_ms + completed_total + projected_total + final_segment_ms
    )

    # Confidence
    observed_indices = [s["hurdle_num"] for s in completed_splits]
    phases = _phases_covered(observed_indices, boundaries)
    confidence = _compute_confidence(num_completed, total_hurdles, phases)

    return {
        "completed_splits": completed_splits,
        "projected_splits": projected_splits,
        "projected_final_segment_ms": final_segment_ms,
        "projected_total_ms": projected_total_ms,
        "confidence": confidence,
        "target_event": target_event,
        "total_hurdles": total_hurdles,
    }