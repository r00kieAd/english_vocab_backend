import os
import httpx
import traceback
from dotenv import load_dotenv
from schemas.llm_client import TextToSpeechLLMRes
from fastapi import HTTPException

load_dotenv()

async def sarvamTextToSpeech(req):
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            res = await client.post(
                os.getenv("SARVAM_TEXT_TO_SPEECH_API_URI"),
                json=req.model_dump(),
                headers={
                    "api-subscription-key": os.getenv("SARVAM_API_KEY")
                }
            )
        status = res.status_code
        if 200 <= status < 300:
            res = res.json()
            return TextToSpeechLLMRes(req_id=res.get('request_id'), audio=res.get('audios'))
        raise HTTPException(status_code=status, detail="Text to Speech Conversion failed" if not res else res.json())
    except httpx.ConnectTimeout:
        raise HTTPException(status_code=504, detail="Connection Timeout")
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=status if status else 500, detail=str(e) if not res else res.json())
