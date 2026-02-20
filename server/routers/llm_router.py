from fastapi import APIRouter, HTTPException
from schemas.llm_client import SendPrompt, GetAnswers
from llm_client.gemini import ask_gemini

router = APIRouter(prefix="/ai", tags=["artifial_intelligence"])

@router.post("/get_answers", response_model=GetAnswers)
def get_ai_answer(user_query: SendPrompt):
    try:
        original_context = [user_query.prompt]
        user_instructions = user_query.instruction
        if user_query.word:
            original_context.append(user_query.word)
        if user_query.word_type:
            original_context.append(user_query.word_type)
        if user_query.meaning:
            original_context.append(user_query.meaning)
        if user_query.example:
            original_context.append(user_query.example)
        if not user_instructions:
            user_instructions = "You are a english professor. Answer to the point. No need to explain the word."
        
        context = "\n".join(original_context)
        context.strip()
        response = ask_gemini(prompt=context, instruction=user_instructions)
        if response and response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.details)
        print(original_context)
        print()
        print(response.details)
        return GetAnswers(received_prompt=context, answer = response.details)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unknown Error occured: {str(e)}")
