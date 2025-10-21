from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class VocabBase(BaseModel):
    word: str
    word_type: Optional[str] = None
    meaning: Optional[str] = None
    example: Optional[str] = None

class ScoreBase(BaseModel):
    high_score: int
    high_scorer: str

class VocabCreate(VocabBase):
    pass

class VocabUpdate(BaseModel):
    word_type: Optional[str] = None
    meaning: Optional[str] = None
    example: Optional[str] = None

class Vocab(VocabBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

