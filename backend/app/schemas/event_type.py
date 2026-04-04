from enum import StrEnum


class EventType(StrEnum):
    sprint_60m = "sprint_60m"
    sprint_100m = "sprint_100m"
    sprint_200m = "sprint_200m"
    sprint_400m = "sprint_400m"
    hurdles_60m = "hurdles_60m"
    hurdles_110m = "hurdles_110m"
    hurdles_100m = "hurdles_100m"
    hurdles_400m = "hurdles_400m"
    hurdles_partial = "hurdles_partial"
    long_jump = "long_jump"
    triple_jump = "triple_jump"
    high_jump = "high_jump"
    bosco_test = "bosco_test"
    reaction_time_test = "reaction_time_test"
