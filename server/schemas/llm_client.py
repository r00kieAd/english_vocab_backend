from pydantic import BaseModel

class SendPrompt(BaseModel):
    prompt: str
    instruction: str

class GetAnswers(BaseModel):
    answer: str

class ClientResponse(BaseModel):
    status_code: int
    details: str
