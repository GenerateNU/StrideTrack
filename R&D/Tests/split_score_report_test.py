import json
from dataclasses import asdict, dataclass

import numpy as np
from scipy import stats

SEGMENT_LABELS: dict[str, list[str]] = {
    "400mH": ["Start→H1"]
    + [f"H{i}→H{i+1}" for i in range(1, 10)]
    + ["H10→Fin"],
    "400m": ["0-100m", "100-200m", "200-300m", "300-400m"],
}


# Schema


@dataclass
class SegmentReport:
    """Analysis result for a single race segment."""

    label: str
    raw_time: float
    pct_of_total: float
    percentile: float


@dataclass
class RaceReportResponse:
    """Full race report card returned by the analysis endpoint."""

    event_type: str
    total_time: float
    population_size: int
    segments: list[SegmentReport]
    coaching_notes: list[str]

    def to_json(self, indent: int = 2) -> str:
        """Serialize to JSON string."""
        return json.dumps(asdict(self), indent=indent)


# Analysis


class RaceAnalyzer:
    """
    Compares an athlete's split profile against a population distribution.

    Initialize once with population data (e.g., at app startup), then call
    analyze_run() for each incoming race. No ML model — just percentile lookups
    on the stored population distribution.
    """

    def __init__(
        self, population_normalized: np.ndarray, event_type: str
    ) -> None:
        """
        Initialize with precomputed normalized population data.

        Args:
            population_normalized: (N, S) array of normalized splits (% of total time)
                where N = number of races, S = number of segments.
            event_type: "400mH" or "400m".
        """
        self.event_type = event_type
        self.labels = SEGMENT_LABELS[event_type]
        self.population = population_normalized
        self.pop_mean = population_normalized.mean(axis=0)
        self.n_races = len(population_normalized)

    @classmethod
    def from_races(cls, races: list[dict], event_type: str) -> "RaceAnalyzer":
        """
        Build an analyzer from parsed race dicts.

        Args:
            races: list of {"time": float, "intervals": list[float]} for 400mH
                   or {"time": float, "splits": list[float]} for 400m.
            event_type: "400mH" or "400m".
        """
        key = "intervals" if event_type == "400mH" else "splits"
        raw = np.array([r[key] for r in races])
        times = np.array([r["time"] for r in races])
        normalized = raw / times[:, None] * 100
        return cls(normalized, event_type)

    def analyze_run(
        self, segments: list[float], total_time: float
    ) -> RaceReportResponse:
        """
        Analyze a single run against the population.

        Args:
            segments: raw segment times in seconds.
                400mH: 11 values [Start→H1, H1→H2, ..., H9→H10, H10→Fin].
                400m:  4 values [0-100m, 100-200m, 200-300m, 300-400m].
            total_time: official finish time in seconds.

        Returns:
            RaceReportResponse with per-segment percentiles and coaching notes.
        """
        segments_arr = np.array(segments)
        normalized = segments_arr / total_time * 100

        percentiles = np.array([
            stats.percentileofscore(self.population[:, i], normalized[i])
            for i in range(len(segments))
        ])

        segment_reports = [
            SegmentReport(
                label=self.labels[i],
                raw_time=round(float(segments[i]), 3),
                pct_of_total=round(float(normalized[i]), 2),
                percentile=round(float(percentiles[i]), 1),
            )
            for i in range(len(segments))
        ]

        notes: list[str] = []
        for pct, label in zip(percentiles, self.labels):
            if pct > 85:
                notes.append(
                    f"{label}: {pct:.0f}th percentile — significant deceleration. "
                    f"Focus on maintaining pace here."
                )
            elif pct > 70:
                notes.append(
                    f"{label}: {pct:.0f}th percentile — mild deceleration. "
                    f"Room for improvement."
                )
            elif pct < 15:
                notes.append(f"{label}: {pct:.0f}th percentile — strong segment.")

        return RaceReportResponse(
            event_type=self.event_type,
            total_time=total_time,
            population_size=self.n_races,
            segments=segment_reports,
            coaching_notes=notes,
        )