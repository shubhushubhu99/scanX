import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
MODEL = "gemini-2.5-flash"

SYSTEM_PROMPT = """
You are a cybersecurity trust analyst.
Explain clearly and neutrally.
Do NOT accuse.
Do NOT exaggerate.
Limit response to 80–100 words.
"""

def explain_dimension(dimension: str, status: str, signals: dict) -> str:
    prompt = f"""
Trust Dimension: {dimension}
Assessment Status: {status}

Signals observed:
{signals}

Explain:
- Why this dimension received this status
- Which signals influenced it
- What this means for users
"""

    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=[SYSTEM_PROMPT, prompt]
        )
        return response.text.strip()
    except Exception:
        return (
            "This trust dimension was assessed based on multiple technical and "
            "user-experience signals. While some controls exist, observed patterns "
            "indicate potential weaknesses that users should consider."
        )
