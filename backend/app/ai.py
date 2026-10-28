import json
from typing import Optional
from .config import GEMINI_API_KEY, GEMINI_MODEL

def generate_json(prompt: str, fallback: dict, image_bytes: Optional[bytes] = None, mime_type: str = "image/jpeg"):
    if GEMINI_API_KEY:
        try:
            from google import genai
            from google.genai import types
            client = genai.Client(api_key=GEMINI_API_KEY)
            contents = [prompt + "\nReturn only valid JSON, with no markdown."]
            if image_bytes:
                contents.append(types.Part.from_bytes(data=image_bytes, mime_type=mime_type))
            response = client.models.generate_content(model=GEMINI_MODEL, contents=contents)
            raw = (response.text or "").strip()
            if raw.startswith("```"):
                raw = raw.split("\n", 1)[-1].rsplit("```", 1)[0].strip()
            parsed = json.loads(raw)
            if isinstance(parsed, dict):
                return parsed, "gemini"
        except Exception:
            pass
    return fallback, "demo"
