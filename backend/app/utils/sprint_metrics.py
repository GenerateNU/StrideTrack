import numpy as np

from app.schemas.run_schemas import RunResponse, SprintDriftData


def _drift_window(total: int) -> int:
    return max(3, min(10, round(total * 0.1)))


def calculate_drift(data: list[RunResponse]) -> SprintDriftData:
    """
    Calculate GCT and FT drift % comparing max-velocity phase to terminal phase.

    Max-velocity baseline is approximated by:
      - GCT: mean of N shortest ground contact times
      - FT: mean of N longest flight times
    Terminal window: last N strides.
    N = round(total_strides * 0.1), clamped between 3 and 10.

    Positive GCT drift = fatigue (more time on ground).
    Negative FT drift = power loss (less time in air).
    """
    n = _drift_window(len(data))

    gct_vals = np.array([row.gct_ms for row in data])
    ft_vals = np.array([row.flight_ms for row in data])

    gct_baseline = np.mean(np.sort(gct_vals)[:n])
    gct_terminal = np.mean(gct_vals[-n:])

    ft_baseline = np.mean(np.sort(ft_vals)[::-1][:n])
    ft_terminal = np.mean(ft_vals[-n:])

    gct_drift = (
        float((gct_terminal - gct_baseline) / gct_baseline * 100)
        if gct_baseline
        else 0.0
    )
    ft_drift = (
        float((ft_terminal - ft_baseline) / ft_baseline * 100) if ft_baseline else 0.0
    )

    return SprintDriftData(
        gct_drift_pct=round(gct_drift, 2),
        ft_drift_pct=round(ft_drift, 2),
    )
