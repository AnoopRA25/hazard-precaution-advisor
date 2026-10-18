
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


def get_hazard_category(hazard: str) -> str:
    """Classify a detected hazard using flexible keyword matching."""
    text = normalize(hazard)
    words = set(text.split())

    # Exposed electrical wires: check before general cable hazards.
    if (
        "wire" in words
        and any(
            term in text
            for term in [
                "exposed",
                "live wire",
                "bare wire",
                "uninsulated",
            ]
        )
    ):
        return "exposed wire"

    # Falling objects and unstable overhead storage.
    if any(
        term in text
        for term in [
            "falling object",
            "falling objects",
            "stored on top",
            "stacked",
            "overhead storage",
            "objects stored at height",
            "heavy items",
            "suitcase",
            "cardboard box",
            "top of the wardrobe",
            "wardrobe",
            "unstable storage",
            "unsecured items",
        ]
    ):
        return "items stacked overhead"

    # Wet floors and liquid spills.
    if any(
        term in text
        for term in [
            "wet floor",
            "water spill",
            "liquid spill",
            "spilled liquid",
            "water on the floor",
            "wet surface",
        ]
    ):
        return "wet floor"

    # Broken glass.
    if any(
        term in text
        for term in [
            "broken glass",
            "shattered glass",
        ]
    ):
        return "broken glass"

    # Open drains and manholes.
    if any(
        term in text
        for term in [
            "open drain",
            "open manhole",
        ]
    ):
        return "open drain"

    # Stairs and step edges.
    if any(
        term in text
        for term in [
            "stairs",
            "staircase",
            "step edge",
        ]
    ):
        return "stairs"

    # Rugs and carpets.
    if any(
        term in text
        for term in [
            "rug",
            "carpet",
            "throw mat",
        ]
    ):
        return "rug"

    # Trailing electrical cables.
    if any(
        term in text
        for term in [
            "cable",
            "cord",
            "power strip",
            "extension board",
            "extension lead",
        ]
    ):
        return "electrical cable"

    # Loose objects on floors and walking paths.
    if any(
        term in text
        for term in [
            "slipper",
            "sandal",
            "footwear",
            "backpack",
            "bag",
            "papers",
            "books",
            "scattered",
            "loose items",
            "clutter",
            "walking path",
            "walkway",
        ]
    ):
        return "loose objects"

    # Other explicitly described electrical hazards.
    if any(
        term in text
        for term in [
            "electrical hazard",
            "electric shock",
            "electrical fire",
        ]
    ):
        return "electrical hazard"

    return "unknown"


def safety_advisor(state: HazardState) -> dict:
    """Return precautions matching the detected hazard categories."""
    hazards = state.get("hazards", [])
    precautions = []
    sources = []

    try:
        with GUIDELINES_PATH.open("r", encoding="utf-8") as file:
            guidelines = json.load(file)

        if not isinstance(guidelines, list):
            raise ValueError("Safety guidelines must be a JSON list.")

        for hazard in hazards:
            category = get_hazard_category(hazard)

            if category == "unknown":
                continue

            for entry in guidelines:
                guideline_category = normalize(
                    entry.get("hazard", "")
                )

                if guideline_category != normalize(category):
                    continue

                for item in entry.get("precautions", []):
                    if item not in precautions:
                        precautions.append(item)

                source = entry.get("source")
                if source and source not in sources:
                    sources.append(source)

        if not precautions:
            precautions = [
                "Keep people away from the suspected hazard.",
                "Ask a qualified person to assess the area.",
            ]

        return {
            "precautions": precautions[:4],
            "guideline_sources": sources,
            "error": "",
        }

    except (OSError, json.JSONDecodeError, ValueError) as exc:
        return {
            "precautions": [
                "Keep people away from suspected hazards.",
                "Ask a qualified person to assess the area.",
            ],
            "guideline_sources": [],
            "error": f"Could not load safety guidelines: {exc}",
        }
