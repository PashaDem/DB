from datetime import date

from pydantic import BaseModel


class FeedbackInput(BaseModel):
    score: int
    description: str


class FeedbackInit(FeedbackInput):
    create_at: date
    client_id: int


class Feedback(FeedbackInit):
    id: int
