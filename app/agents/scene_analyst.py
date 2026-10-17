
import json
import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types
from PIL import Image, UnidentifiedImageError

from app.state import HazardState

load_dotenv()


def scene_analyst(state: HazardState) -> dict:
    """Analyze a real image and return structured hazard observations."""

    image_path = Path(state.get("image_path", ""))

    if not image_path.is_file():
        return {
            "setting": "unknown",
            "hazards": [],
            "confidence": 0.0,
            "error": "Image file not found.",
        }

    api_key = os.getenv("GEMINI_API_KEY")
    model = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")

    if not api_key:
        return {
            "setting": "unknown",
            "hazards": [],
            "confidence": 0.0,
            "error": "GEMINI_API_KEY is not configured.",
        }

    prompt = """
    Analyze this image for visible physical safety hazards.

    Return ONLY valid JSON with these fields:
    {
      "setting": "short description of the environment",
      "hazards": ["specific visible hazard"],
      "confidence": 0.0
    }

    Rules:
    - Include only hazards supported by visible evidence.
    - If no obvious hazard is visible, return an empty hazards list.
    - Do not assume that an image is completely safe.
    - Confidence must be a number between 0.0 and 1.0
      representing confidence in this visual assessment.
    - Do not invent details that cannot be seen.
    """

    try:
        with Image.open(image_path) as image:
            image.load()
            client = genai.Client(api_key=api_key)

            response = client.models.generate_content(
                model=model,
                contents=[prompt, image.copy()],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                ),
            )

        if not response.text:
            raise ValueError("Gemini returned an empty response.")

        data = json.loads(response.text)

        setting = data.get("setting", "unknown")
        hazards = data.get("hazards", [])
        confidence = float(data.get("confidence", 0.0))

        if not isinstance(setting, str):
            raise ValueError("The setting must be a string.")

        if (
            not isinstance(hazards, list)
            or not all(isinstance(item, str) for item in hazards)
        ):
            raise ValueError("Hazards must be a list of strings.")

        if not 0.0 <= confidence <= 1.0:
            raise ValueError("Confidence must be between 0 and 1.")

        return {
            "setting": setting,
            "hazards": hazards,
            "confidence": confidence,
            "error": "",
        }

    except (OSError, UnidentifiedImageError):
        return {
            "setting": "unknown",
            "hazards": [],
            "confidence": 0.0,
            "error": "The image could not be opened or decoded.",
        }
    except Exception as exc:
        return {
            "setting": "unknown",
            "hazards": [],
            "confidence": 0.0,
            "error": f"Scene analysis failed: {type(exc).__name__}: {exc}",
        }
