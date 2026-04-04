from __future__ import annotations

from app.schemas.event_type import EventType

SUPPORTED_EVENTS: frozenset[EventType] = frozenset(
    {EventType.hurdles_400m, EventType.sprint_400m}
)

SEGMENT_LABELS: dict[EventType, list[str]] = {
    EventType.hurdles_400m: ["Start→H1"]
    + [f"H{i}→H{i + 1}" for i in range(1, 10)]
    + ["H10→Fin"],
    EventType.sprint_400m: ["0-100m", "100-200m", "200-300m", "300-400m"],
}

POPULATION_STATS: dict[EventType, dict[str, list[float]]] = {
    EventType.hurdles_400m: {
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
    EventType.sprint_400m: {
        "mean": [24.6591, 23.0620, 24.8268, 27.4522],
        "std": [0.5188, 0.4290, 0.3703, 0.7590],
    },
}
