
from app.state import HazardState


def scene_analyst(state: HazardState) -> dict:
    """
    Temporary mock Scene Analyst.
    Replace with a vision model after testing the workflow.
    """

    image_path = state.get("image_path", "")

    if not image_path:
        return {
            "setting": "unknown",
            "hazards": [],
            "confidence": 0.0,
            "error": "No image path provided."
        }

    # MOCK RESULT: This does not inspect the actual image.
    return {
        "setting": "kitchen",
        "hazards": ["wet floor"],
        "confidence": 0.85,
        "error": ""
    }
