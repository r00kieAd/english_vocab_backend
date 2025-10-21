from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ScoreBase(BaseModel):
    high_score: int
    high_scorer: str

class ScoreCreate(ScoreBase):
    pass

class Score(ScoreBase):
    id: int
    date_created: datetime

    class Config:
        from_attributes = True