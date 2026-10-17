
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from PIL import Image

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

if not api_key or "PASTE_YOUR" in api_key:
    sys.exit("ERROR: Configure GEMINI_API_KEY in .env first.")

if len(sys.argv) < 2:
    sys.exit(
        "Usage: python test_gemini_vision.py <path-to-image>"
    )

image_path = Path(sys.argv[1])

if not image_path.is_file():
    sys.exit(f"ERROR: Image not found: {image_path}")

try:
    with Image.open(image_path) as image:
        image.verify()

    with Image.open(image_path) as image:
        client = genai.Client(api_key=api_key)
        prompt = """
        Analyze this image for visible physical safety hazards.
        Return:
        1. The setting.
        2. Visible hazards, if any.
        3. Evidence supporting each hazard.
        4. Who may be particularly vulnerable.
        5. What cannot be determined reliably from this image.

        Do not claim the scene is safe merely because no hazard
        is visible. Do not invent hazards that are not supported
        by the image.
        """
        response = client.models.generate_content(
            model=model,
            contents=[prompt, image],
        )

    print("\n--- GEMINI IMAGE ANALYSIS ---\n")
    print(response.text or "The model returned no text.")
except Exception as exc:
    print(f"ERROR: {type(exc).__name__}: {exc}")
    sys.exit(1)
