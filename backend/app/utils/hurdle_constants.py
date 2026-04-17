from app.schemas.event_type import EventType

EXPECTED_HURDLE_COUNTS: dict[EventType, int] = {
    EventType.hurdles_60m: 5,
    EventType.hurdles_100m: 10,
    EventType.hurdles_110m: 10,
    EventType.hurdles_400m: 10,
}
