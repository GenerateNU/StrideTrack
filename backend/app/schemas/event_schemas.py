from pydantic import BaseModel


class EventOption(BaseModel):
    value: str
    label: str


class EventListResponse(BaseModel):
    events: list[EventOption]
