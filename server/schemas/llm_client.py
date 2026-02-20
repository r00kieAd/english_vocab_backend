from typing import Optional
from pydantic import BaseModel

class SendPrompt(BaseModel):
    prompt: str
    word: Optional[str] = None
    word_type: Optional[str] = None
    meaning: Optional[str] = None
    example: Optional[str] = None
    instruction: Optional[str] = None

class GetAnswers(BaseModel):
    received_prompt: str
    answer: str

class ClientResponse(BaseModel):
    status_code: int
    details: str
