from fastapi import APIRouter, HTTPException
from schemas.llm_client import SendPrompt, GetAnswers
from llm_client.gemini import ask_gemini

router = APIRouter(prefix="/ai", tags=["artifial_intelligence"])

@router.post("/get_answers", response_model=GetAnswers)
def get_ai_answer(user_query: SendPrompt):
    try:
        response = ask_gemini(prompt=user_query.prompt, instruction=user_query.instruction)
        if response and response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.details)
        return GetAnswers(answer = response.details)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unknown Error occured: {str(e)}")
