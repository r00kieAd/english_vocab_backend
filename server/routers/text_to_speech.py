from schemas.llm_client import TextToSpeechReq, TextToSpeechLLMRes, TextToSpeechRes
from fastapi import APIRouter, HTTPException
from llm_client.sarvam_text_speech import sarvamTextToSpeech

router = APIRouter(prefix="/ai", tags=["artifial_intelligence"])


@router.post("/text_to_speech", response_model=TextToSpeechRes)
async def textToSpeechRouter(req: TextToSpeechReq):
    try:
        res = await sarvamTextToSpeech(req=req)
        return TextToSpeechRes(original_text=req.text, target_language=req.target_language, speaker=req.speaker, pace=req.pace, model=req.model, llm_res=res)
    except HTTPException:
        raise
    except Exception as e:
        print(str(e))
        raise HTTPException(status_code=500, detail="Text to Speech Conversion process failed while routing request to llm")