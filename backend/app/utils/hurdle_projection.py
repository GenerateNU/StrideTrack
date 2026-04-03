from __future__ import annotations

import numpy as np

from app.schemas.hurdle_schemas import HurdleMetricRow


# Per-event race parameters and normalised three-phase split templates
EVENT_CONFIG: dict[str, dict] = {
    "hurdles_60m": {
        "hurdle_count": 5,
        "final_segment_ms": 1000,
        "phase_boundaries": (3, 4),
        "template_ratios": [1.12, 1.03, 0.97, 0.95, 0.97],
    },
    "hurdles_100m": {
        "hurdle_count": 10,
        "final_segment_ms": 1300,
        "phase_boundaries": (4, 7),
        "template_ratios": [
            1.15, 1.06, 1.00, 0.97,   # acceleration  (H1-H4)
            0.95, 0.95, 0.96,         # peak speed    (H5-H7)
            0.97, 0.99, 1.00,         # fatigue       (H8-H10)
        ],
    },
    "hurdles_110m": {
        "hurdle_count": 10,
        "final_segment_ms": 1400,
        "phase_boundaries": (4, 7),
        "template_ratios": [
            1.15, 1.05, 1.00, 0.97,
            0.95, 0.95, 0.96,
            0.97, 0.99, 1.00,
        ],
    },
    "hurdles_400m": {
        "hurdle_count": 10,
        "final_segment_ms": 4500,
        "phase_boundaries": (3, 7),
        "template_ratios": [
            1.10, 1.03, 0.98,
            0.95, 0.94, 0.95, 0.96,
            0.99, 1.02, 1.06,
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


def project_hurdle_race(
    completed_metrics: list[HurdleMetricRow],
    target_event: str,
) -> dict:
    """Project total race time from partial hurdle data. Keeps completed splits as-is, fits a template to
    observed data, and blends with per-phase trends to project remaining hurdles."""
    if target_event not in EVENT_CONFIG:
        raise ValueError(
            f"Unknown target event '{target_event}'. "
            f"Must be one of {sorted(EVENT_CONFIG.keys())}"
        )

    config = EVENT_CONFIG[target_event]
    total_hurdles: int = config["hurdle_count"]
    final_segment_ms: int = config["final_segment_ms"]
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

    # Not enough data to fit anything
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

    hurdle_indices = np.array([s["hurdle_num"] for s in completed_splits])
    split_values = np.array([s["split_ms"] for s in completed_splits])

    phase_trends = _fit_phase_trends(hurdle_indices, split_values, boundaries)

    scaled_template = _scale_template(template_ratios, completed_splits)

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