
from app.state import HazardState


def risk_predictor(state: HazardState) -> dict:
    hazards = state.get("hazards", [])
    person_type = state.get("person_type", "adult").lower()

    if not hazards:
        return {
            "predicted_risk": "No visible hazards were identified.",
            "risk_level": "low",
            "reason": (
                "No hazards were detected. This does not guarantee "
                "that the environment is safe."
            ),
        }

    hazard_text = " ".join(hazards).lower()

    # Potentially severe hazards
    severe_keywords = [
        "open drain",
        "open manhole",
        "deep water",
        "fire",
        "exposed wire",
        "electrical hazard",
        "electric shock",
    ]

    # Potential falling-object hazards
    falling_object_keywords = [
        "falling object",
        "unsecured heavy items",
        "stacked loosely",
        "top of the wardrobe",
        "overhead storage",
        "unstable storage",
        "stored on top",
        "heavy items stored",
        "objects stored at height",
    ]

    # Potential trip and slip hazards
    trip_keywords = [
        "wet floor",
        "stairs",
        "sharp object",
        "broken glass",
        "tripping hazard",
        "trip hazard",
        "trip or slip",
        "extension cord",
        "power strip",
        "extension board",
        "electrical cable",
        "trailing cable",
        "power cords",
        "cables across",
        "walkway",
        "walking path",
        "loose slippers",
        "loose footwear",
        "footwear scattered",
        "sandals",
        "scattered",
        "unsecured rug",
        "loose throw rug",
        "slip hazard",
        "slick tile",
        "smooth tile",
    ]

    vulnerable_person = person_type in [
        "baby",
        "child",
        "elderly",
    ]

    # 1. Potentially severe hazards take priority.
    if any(word in hazard_text for word in severe_keywords):
        risk_level = "high"
        predicted_risk = (
            "The detected hazard may cause serious injury, "
            "including electrical injury or other severe harm."
        )
        reason = (
            "A potentially severe hazard was identified. "
            "Keep people away and arrange appropriate professional help."
        )

    # 2. Objects stored overhead may fall and cause impact injuries.
    elif any(
        word in hazard_text for word in falling_object_keywords
    ):
        risk_level = "high"
        predicted_risk = (
            "Unsecured items stored at height may fall and cause "
            "head injuries or other impact injuries."
        )
        reason = (
            "Unstable or unsecured objects were detected above "
            "the walking area. Heavy items should be stored securely "
            "at a lower height."
        )

        if person_type in ["baby", "child"]:
            reason += (
                " Keep children away from the area and have an adult "
                "secure the objects."
            )
        elif person_type == "elderly":
            reason += (
                " Avoid reaching overhead or attempting to move "
                "heavy objects without appropriate assistance."
            )

    # 3. Trip and slip hazards.
    elif any(word in hazard_text for word in trip_keywords):
        risk_level = "high" if vulnerable_person else "medium"

        predicted_risk = (
            "Trailing cables, loose objects, or slippery surfaces "
            "may cause a trip, loss of balance, or a fall."
        )

        reason = (
            "The walking area contains potential trip or slip hazards."
        )

        if person_type == "elderly":
            reason += (
                " A fall may have more serious consequences for an "
                "older adult, particularly if balance or mobility "
                "is limited."
            )
        elif person_type in ["baby", "child"]:
            reason += (
                " Young children require appropriate supervision "
                "around these hazards."
            )

    # 4. Unknown hazard descriptions need further assessment.
    else:
        risk_level = "medium"
        predicted_risk = (
            "The identified hazard may cause injury and requires "
            "further assessment."
        )
        reason = (
            "The hazard could not be classified confidently using "
            "the current prototype rules. Do not assume the area is safe."
        )

    return {
        "predicted_risk": predicted_risk,
        "risk_level": risk_level,
        "reason": reason,
    }
