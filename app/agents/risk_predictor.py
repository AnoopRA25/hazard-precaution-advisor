
from app.state import HazardState


def risk_predictor(state: HazardState) -> dict:
    """
    Rule-based Risk Predictor for the initial prototype.
    """

    hazards = state.get("hazards", [])
    person_type = state.get("person_type", "adult").lower()

    if not hazards:
        return {
            "predicted_risk": "No visible hazards identified.",
            "risk_level": "low",
            "reason": "No hazards were detected in the supplied scene."
        }

    hazard_text = " ".join(hazards).lower()

    # Identify potential accidents using simple rules.
    if any(word in hazard_text for word in [
        "open drain", "deep water", "open manhole",
        "fire", "exposed wire", "electrical hazard"
    ]):
        risk_level = "high"
        accident = "Serious injury may occur if the hazard is approached."
        reason = "The scene contains a potentially dangerous hazard."

    elif any(word in hazard_text for word in [
        "wet floor", "stairs", "busy road",
        "sharp object", "broken glass"
    ]):
        risk_level = "high" if person_type in [
            "baby", "child", "elderly"
        ] else "medium"
        accident = "A fall, cut, or other injury may occur."
        reason = "The hazard could cause injury, depending on exposure."

    else:
        risk_level = "medium"
        accident = "Contact with the identified hazard may cause injury."
        reason = "The hazard needs further assessment."

    if person_type in ["baby", "child"]:
        reason += " Young children require close supervision."
    elif person_type == "elderly":
        reason += " Mobility and balance may affect the risk."

    return {
        "predicted_risk": accident,
        "risk_level": risk_level,
        "reason": reason
    }
