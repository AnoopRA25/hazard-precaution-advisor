
import json
from pathlib import Path

from app.state import HazardState


GUIDELINES_PATH = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "guidelines"
    / "safety_guidelines.json"
)


def safety_advisor(state: HazardState) -> dict:
    """Match detected hazards against the local safety knowledge base."""

    hazards = state.get("hazards", [])
    precautions = []
    sources = []

    if not GUIDELINES_PATH.exists():
        return {
            "precautions": [
                "Keep people away from the suspected hazard.",
                "Seek help from a qualified person to assess the danger."
            ],
            "guideline_sources": [],
            "error": "Safety guideline file was not found."
        }

    with GUIDELINES_PATH.open("r", encoding="utf-8") as file:
        guidelines = json.load(file)

    for detected_hazard in hazards:
        detected = detected_hazard.lower()

        for guideline in guidelines:
            known_hazard = guideline["hazard"].lower()

            if known_hazard in detected or detected in known_hazard:
                precautions.extend(guideline["precautions"])
                sources.append(guideline["source"])
                break

    # Remove duplicate precautions while preserving their order.
    precautions = list(dict.fromkeys(precautions))[:4]
    sources = list(dict.fromkeys(sources))

    if len(precautions) < 2:
        precautions = [
            "Keep people away from the suspected hazard.",
            "Seek help from a qualified person to assess the danger."
        ]

    return {
        "precautions": precautions,
        "guideline_sources": sources,
        "error": ""
    }
