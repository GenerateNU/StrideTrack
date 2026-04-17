from dataclasses import dataclass


@dataclass(frozen=True)
class Interval:
    start: int
    end: int
