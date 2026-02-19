import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.api_core import exceptions
from schemas.llm_client import ClientResponse

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def ask_gemini(prompt: str, instruction: str) -> dict:
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash-lite",
            config=types.GenerateContentConfig(system_instruction=instruction),
            contents=prompt
        )
        # print(f"gemini response: {response}")
        return ClientResponse(status_code=200, details=response.text)
    except exceptions.GoogleAPICallError as e:
        return ClientResponse(status_code=e.code, details=e.message)
    except Exception as e:
        return ClientResponse(status_code=500, details=f"[Gemini Error] {str(e)}")
