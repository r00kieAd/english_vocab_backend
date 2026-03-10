from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ScoreBase(BaseModel):
    high_score: int
    high_scorer: str


class ScoreCreate(ScoreBase):
    pass


class Score(ScoreBase):
    id: int
    date_created: Optional[datetime] = None
    date_modified: Optional[datetime] = None

    class Config:
        from_attributes = True
