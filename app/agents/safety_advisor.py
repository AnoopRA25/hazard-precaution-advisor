
import json
import re
from pathlib import Path

from app.state import HazardState

GUIDELINES_PATH = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "guidelines"
    / "safety_guidelines.json"
)


def normalize(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


def find_guidelines(hazard: str, guidelines: list[dict]) -> list[dict]:
    text = normalize(hazard)

    aliases = {
        "electrical cable": [
            "electrical cable",
            "exposed wire",
        ],
        "loose objects": ["loose objects"],
        "rug": ["rug"],
        "wet floor": ["wet floor"],
        "broken glass": ["broken glass"],
        "stairs": ["stairs"],
        "open drain": ["open drain"],
    }

    matched = []

    # Prefer direct matches.
    for entry in guidelines:
        key = normalize(entry.get("hazard", ""))
        if key and key in text:
            matched.append(entry)

    # Use aliases for descriptions phrased differently by Gemini.
    if not matched:
        if any(word in text for word in [
            "cable", "cord", "power strip", "extension board"
        ]):
            keys = aliases["electrical cable"]
        elif any(word in text for word in [
            "slipper", "sandal", "footwear", "backpack",
            "bag", "scattered", "loose item", "walking path"
        ]):
            keys = aliases["loose objects"]
        elif any(word in text for word in [
            "rug", "carpet", "slip hazard"
        ]):
            keys = aliases["rug"]
        else:
            keys = []

        for entry in guidelines:
            if normalize(entry.get("hazard", "")) in keys:
                matched.append(entry)

    return matched


def safety_advisor(state: HazardState) -> dict:
    hazards = state.get("hazards", [])
    precautions = []
    sources = []

    try:
        with GUIDELINES_PATH.open("r", encoding="utf-8") as file:
            guidelines = json.load(file)

        # Reserve space for relevant advice for each detected hazard.
        for hazard in hazards:
            entries = find_guidelines(hazard, guidelines)

            for entry in entries:
                items = entry.get("precautions", [])
                if items:
                    item = items[0]
                    if item not in precautions:
                        precautions.append(item)

                source = entry.get("source")
                if source and source not in sources:
                    sources.append(source)

        # Add further useful advice until the report has four items.
        for hazard in hazards:
            if len(precautions) >= 4:
                break

            for entry in find_guidelines(hazard, guidelines):
                for item in entry.get("precautions", []):
                    if item not in precautions:
                        precautions.append(item)
                    if len(precautions) >= 4:
                        break
                if len(precautions) >= 4:
                    break

        if not precautions:
            precautions = [
                "Keep people away from suspected hazards.",
                "Ask a qualified person to assess the area.",
            ]

        return {
            "precautions": precautions[:4],
            "guideline_sources": sources,
            "error": "",
        }

    except (OSError, json.JSONDecodeError) as exc:
        return {
            "precautions": [
                "Keep people away from suspected hazards.",
                "Ask a qualified person to assess the area.",
            ],
            "guideline_sources": [],
            "error": f"Could not load safety guidelines: {exc}",
        }
