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

class TextToSpeechReq(BaseModel):
    text: str
    target_language: str = "bn-IN"
    speaker: str = "anushka"
    model: str = "bulbul:v2"

class TextToSpeechLLMRes(BaseModel):
    req_id: Optional[str] = None
    audio: list[str]

class TextToSpeechRes(BaseModel):
    original_text: str
    target_language: str
    speaker: str
    model: str
    llm_res: TextToSpeechLLMRes

