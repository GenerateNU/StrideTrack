EVENT_DISPLAY_NAMES = {
    "sprint_60m": "60 Meter Sprint",
    "sprint_100m": "100 Meter Sprint",
    "sprint_200m": "200 Meter Sprint",
    "sprint_400m": "400 Meter Sprint",
    "hurdles_60m": "60 Meter Hurdles",
    "hurdles_110m": "110 Meter Hurdles",
    "hurdles_100m": "100 Meter Hurdles",
    "hurdles_400m": "400 Meter Hurdles",
    "long_jump": "Long Jump",
    "triple_jump": "Triple Jump",
    "high_jump": "High Jump",
    "bosco_test": "Bosco Test",
    "reaction_time_test": "Reaction Time Test",
}


def get_event_display_name(event_type: str) -> str:
    return EVENT_DISPLAY_NAMES.get(event_type, event_type)


def get_all_events() -> list[dict[str, str]]:
    return [
        {"value": key, "label": value} for key, value in EVENT_DISPLAY_NAMES.items()
    ]
