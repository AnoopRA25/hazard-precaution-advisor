
from app.state import HazardState


def reporter(state: HazardState) -> dict:
    """Format the assessment as a readable safety report."""

    language = state.get("language", "English")
    person_type = state.get("person_type", "adult")
    setting = state.get("setting", "unknown")
    hazards = state.get("hazards", [])
    risk_level = state.get("risk_level", "medium")
    predicted_risk = state.get(
        "predicted_risk",
        "The scene requires further assessment."
    )
    precautions = state.get("precautions", [])

    # Temporary language handling.
    # Real translation will be added using an AI model.
    if language not in ["English", "Kannada", "Hindi"]:
        language = "English"

    title = {
        "English": "HAZARD PRECAUTION ADVISOR",
        "Kannada": "ಅಪಾಯ ಮುನ್ನೆಚ್ಚರಿಕೆ ಸಲಹೆಗಾರ",
        "Hindi": "खतरा सावधानी सलाहकार"
    }[language]

    # Until real translation is implemented, precaution text
    # remains in English for every language selection.
    lines = [
        title,
        "",
        f"Setting: {setting}",
        f"Person: {person_type}",
        f"Risk level: {risk_level.upper()}",
        f"Possible danger: {predicted_risk}",
        "",
        "Precautions:"
    ]

    if hazards:
        lines.insert(4, f"Hazards: {', '.join(hazards)}")

    if precautions:
        lines.extend(
            f"{index}. {item}"
            for index, item in enumerate(precautions, start=1)
        )
    else:
        lines.append(
            "Keep away from suspected hazards and seek qualified help."
        )

    lines.extend([
        "",
        "Disclaimer: This is assistive advice, not a guarantee of safety.",
        "In an emergency, contact local emergency services."
    ])

    high_risk = risk_level == "high"

    return {
        "message": "\n".join(lines),
        "caregiver_alert_required": high_risk
    }
