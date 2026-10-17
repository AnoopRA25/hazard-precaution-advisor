
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

    # Hazards that may cause trips, slips, or falls
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
        "electrical cable",
        "trailing cable",
        "cables across",
        "walkway",
        "loose slippers",
        "sandals",
        "scattered",
        "walking path",
    ]

    vulnerable_person = person_type in ["baby", "child", "elderly"]

    if any(word in hazard_text for word in severe_keywords):
        risk_level = "high"
        predicted_risk = (
            "The detected hazard may cause serious injury, "
            "including electrical injury or other severe harm."
        )
        reason = "A potentially severe hazard was identified."

    elif any(word in hazard_text for word in trip_keywords):
        risk_level = "high" if vulnerable_person else "medium"
        predicted_risk = (
            "Trailing cables and/or loose items in the walking path "
            "may cause a trip, loss of balance, and a fall."
        )
        reason = (
            "The walking path contains potential trip hazards."
        )

        if person_type == "elderly":
            reason += (
                " A fall may have more serious consequences for an "
                "older adult, particularly if balance or mobility is limited."
            )
        elif person_type in ["baby", "child"]:
            reason += (
                " Young children need appropriate supervision "
                "around these hazards."
            )

    else:
        risk_level = "medium"
        predicted_risk = (
            "The identified hazard may cause injury and requires "
            "further assessment."
        )
        reason = (
            "The hazard could not be classified confidently "
            "using the current prototype rules."
        )

    return {
        "predicted_risk": predicted_risk,
        "risk_level": risk_level,
        "reason": reason,
    }
