from pydantic import BaseModel


class FeedbackResponse(BaseModel):
    feedback: str
