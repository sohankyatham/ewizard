import os
import requests
from dotenv import load_dotenv

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def get_disposal_tips(item_label: str, location_hint: str = "University of Georgia (UGA), Athens, Georgia") -> str:
    if not GEMINI_API_KEY:
        return "Gemini is not configured. Add GEMINI_API_KEY to your .env file."

    prompt = f"""
Give disposal guidance for a student.

Item: {item_label}
Location: {location_hint}

Return ONLY plain text in this exact format:

What it is: <1 sentence>
Safety: <1 sentence>
Disposal:
- <bullet 1>
- <bullet 2>
- <bullet 3>
(Optional) Local tip: <1 sentence>

Keep it under 120 words.
"""

    model_name = "gemini-2.5-flash"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={GEMINI_API_KEY}"

    payload = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.3,
            "maxOutputTokens": 900,   # <-- bigger so it doesn't cut off
        },
    }

    try:
        r = requests.post(url, json=payload, timeout=30)
        r.raise_for_status()
        data = r.json()

        candidates = data.get("candidates", [])
        if not candidates:
            return f"Gemini returned no candidates. Full response: {data}"

        content = candidates[0].get("content", {})
        parts = content.get("parts", [])
        text = "".join(p.get("text", "") for p in parts).strip()

        # Debug info in case it truncates again
        finish = candidates[0].get("finishReason", "UNKNOWN")

        if not text:
            return f"Gemini returned empty text. finishReason={finish}. Full response: {data}"

        # If it still truncates, include finish reason so we know why
        return text + (f"\n\n[debug] finishReason={finish}" if finish != "STOP" else "")

    except requests.RequestException as e:
        return f"Gemini request failed: {e}"
