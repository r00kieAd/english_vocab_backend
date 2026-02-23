import os
from dotenv import load_dotenv
from sarvamai import SarvamAI
from schemas.llm_client import ClientResponse

load_dotenv()

client = SarvamAI(
    api_subscription_key=os.getenv("SARVAM_API_KEY"),
)


def ask_sarvam(prompt: str, instruction: str):
    try:
        # print("\n".join([instruction, prompt]))
        response = client.chat.completions(messages=[
            {
                "role": "user",
                "content": "\n".join([instruction, prompt])
            }
        ])
        res = response.choices[0].message.content
        return ClientResponse(status_code=200, details=res)
    except Exception as e:
        return ClientResponse(status_code=500, details=f"[Sarvam Error] {str(e)}")
