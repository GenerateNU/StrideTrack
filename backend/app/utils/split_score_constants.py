"""
Population distribution constants for split score percentile computation.

Derived by running the R&D parsing and normalization logic against the
AthletesFirst PDFs (326 hurdle races, 304 sprint races). Hardcoded so
percentiles can be computed at request time with a single normal CDF call —
no DB or file I/O required.

To regenerate: add the four print statements to the bottom of
R&D/Tests/split_score_test.py main() and rerun against the PDFs.
"""

from __future__ import annotations

# Event types supported by split score analysis.
SUPPORTED_EVENTS: frozenset[str] = frozenset({"400mH", "400m"})

# Human-readable labels for each segment, in order.
SEGMENT_LABELS: dict[str, list[str]] = {
    "400mH": ["Start→H1"] + [f"H{i}→H{i + 1}" for i in range(1, 10)] + ["H10→Fin"],
    "400m": ["0-100m", "100-200m", "200-300m", "300-400m"],
}

# Per-segment population statistics.
# Values are normalized splits expressed as a percentage of total race time.
# A higher percentile = athlete spent MORE time in that segment = relatively slower.
POPULATION_STATS: dict[str, dict[str, list[float]]] = {
    "400mH": {
        # Segments: Start→H1, H1→H2, H2→H3, H3→H4, H4→H5, H5→H6,
        #           H6→H7, H7→H8, H8→H9, H9→H10, H10→Fin
        "mean": [
            12.0721,
            7.7015,
            7.8618,
            8.1616,
            8.2444,
            7.9165,
            8.7185,
            9.1875,
            9.5192,
            9.5428,
            11.0741,
        ],
        "std": [
            0.3099,
            0.2323,
            0.2204,
            1.1089,
            0.9439,
            1.4996,
            1.1925,
            1.3120,
            1.4594,
            0.3331,
            0.6104,
        ],
    },
    "400m": {
        # Segments: 0-100m, 100-200m, 200-300m, 300-400m
        "mean": [24.6591, 23.0620, 24.8268, 27.4522],
        "std": [0.5188, 0.4290, 0.3703, 0.7590],
    },
}
