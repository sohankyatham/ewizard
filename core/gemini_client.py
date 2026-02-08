import os
import requests
from dotenv import load_dotenv

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def get_disposal_tips(item_label: str, location_hint: str = "University of Georgia (UGA), Athens, Georgia") -> str:
    if not GEMINI_API_KEY:
        return "Gemini is not configured. Add GEMINI_API_KEY to your .env file."

    prompt = f"""
    Return ONLY valid JSON. No markdown. No extra text.

    Schema:
    {{
    "what": "ONE sentence defining what the item is (what it does).",
    "safety": "ONE sentence about safety or data wiping if needed."
    }}

    Item: {item_label}

    Write the "what" field as a definition, not disposal advice.
    """.strip()


    resources = [
        {"name": "UGA Surplus Store & Recycling Center", "url": "https://busfin.uga.edu/surplus"},
        {"name": "Athens-Clarke County Household Hazardous Waste", "url": "https://www.accgov.com/hhw"},
        {"name": "Best Buy Recycling", "url": "https://www.bestbuy.com/site/services/recycling/pcmcat149900050025.c"},
    ]



    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.2,
            "maxOutputTokens": 300,
            "responseMimeType": "application/json"
        }
    }

    try:
        model_name = "gemini-2.5-flash"
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={GEMINI_API_KEY}"

        r = requests.post(url, json=payload, timeout=30)
        if r.status_code != 200:
            return f"Gemini error {r.status_code}: {r.text}"

        data = r.json()
        candidates = data.get("candidates", [])
        if not candidates:
            return "Gemini returned no candidates."

        content = candidates[0].get("content", {})
        parts = content.get("parts", [])
        text = "".join(p.get("text", "") for p in parts).strip()

        
        # DEBUG: print full Gemini response once (remove later)
        finish = candidates[0].get("finishReason", "UNKNOWN")
        print("Gemini raw text:", text)

        # Parse JSON response
        import json

        def extract_json(s: str) -> str | None:
            s = s.strip()
            if s.startswith("```"):
                s = s.split("\n", 1)[-1]
                if s.endswith("```"):
                    s = s.rsplit("```", 1)[0].strip()
            start = s.find("{")
            end = s.rfind("}")
            if start == -1 or end == -1 or end <= start:
                return None
            return s[start:end+1]

        json_str = extract_json(text)
        if not json_str:
            return "Gemini did not return valid JSON. Try again."
        
        obj = json.loads(json_str)


        try:
            obj = json.loads(text)
        except json.JSONDecodeError:
            # If Gemini fails JSON, fall back to raw text
            return "Gemini returned invalid JSON. Try again."

        what = obj.get("what", "")
        safety = obj.get("safety", "")
        resources = [
        {"name": "UGA Surplus Store & Recycling Center", "url": "https://busfin.uga.edu/surplus"},
        {"name": "Athens-Clarke County Household Hazardous Waste", "url": "https://www.accgov.com/hhw"},
        {"name": "Best Buy Recycling", "url": "https://www.bestbuy.com/site/services/recycling/pcmcat149900050025.c"},
        ]

        out = (
            f"## What it is\n{what}\n\n"
            f"## Safety & Data\n{safety}\n\n"
            f"## How to Dispose (Athens / UGA)\n"
        )

        for r in resources[:3]:
            name = r.get("name", "Resource")
            url = r.get("url", "")
            out += f"- **{name}** – {url}\n"

        return out.strip()


    except requests.RequestException as e:
        return f"Gemini request failed: {e}"
