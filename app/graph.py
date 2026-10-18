
from langgraph.graph import StateGraph, START, END

from app.state import HazardState
from app.agents.scene_analyst import scene_analyst
from app.agents.risk_predictor import risk_predictor
from app.agents.safety_advisor import safety_advisor
from app.agents.reporter import reporter
from app.agents.caregiver_alert import caregiver_alert


def analyze_scene(state: HazardState) -> dict:
    """Analyze the image, retrying low-confidence results once."""
    result = scene_analyst(state)
    retry_count = state.get("retry_count", 0)

    result["retry_count"] = retry_count

    if result.get("error"):
        return result

    if result.get("confidence", 0.0) < 0.6:
        result["retry_count"] = retry_count + 1

    return result


def route_after_analysis(state: HazardState) -> str:
    """Choose the next step after scene analysis."""
    if state.get("error"):
        return "retake"

    if state.get("confidence", 0.0) < 0.6:
        if state.get("retry_count", 0) < 2:
            return "retry"
        return "retake"

    if not state.get("hazards", []):
        return "safe"

    return "risk"


def safe_result(state: HazardState) -> dict:
    """Prepare a cautious report when no hazard is visible."""
    return {
        "predicted_risk": "No obvious hazards were identified.",
        "risk_level": "low",
        "reason": (
            "The image analysis did not identify an obvious hazard. "
            "This does not prove the environment is completely safe."
        ),
        "precautions": [
            "Continue observing your surroundings.",
            "Check areas that may be hidden or unclear in the image.",
        ],
    }


def retake_result(state: HazardState) -> dict:
    """Avoid a definitive safety determination when analysis fails."""
    return {
        "setting": state.get("setting", "unknown"),
        "hazards": [],
        "predicted_risk": (
            "The image could not be assessed reliably. "
            "Do not assume the area is safe."
        ),
        "risk_level": "medium",
        "reason": (
            "The image could not be assessed with sufficient confidence."
        ),
        "precautions": [
            "Keep away from suspected hazards until checked.",
            "Submit a clearer image or have the area checked safely.",
        ],
    }


def route_after_report(state: HazardState) -> str:
    """Send alerts only for high-risk assessments."""
    if state.get("risk_level", "medium").lower() == "high":
        return "alert"
    return "end"


builder = StateGraph(HazardState)

# Register every node before connecting graph edges.
builder.add_node("scene_analyst", analyze_scene)
builder.add_node("risk_predictor", risk_predictor)
builder.add_node("safety_advisor", safety_advisor)
builder.add_node("safe_result", safe_result)
builder.add_node("retake_result", retake_result)
builder.add_node("reporter", reporter)
builder.add_node("caregiver_alert", caregiver_alert)

builder.add_edge(START, "scene_analyst")

builder.add_conditional_edges(
    "scene_analyst",
    route_after_analysis,
    {
        "retry": "scene_analyst",
        "retake": "retake_result",
        "safe": "safe_result",
        "risk": "risk_predictor",
    },
)

builder.add_edge("risk_predictor", "safety_advisor")
builder.add_edge("safety_advisor", "reporter")
builder.add_edge("safe_result", "reporter")
builder.add_edge("retake_result", "reporter")

builder.add_conditional_edges(
    "reporter",
    route_after_report,
    {
        "alert": "caregiver_alert",
        "end": END,
    },
)

builder.add_edge("caregiver_alert", END)

graph = builder.compile()
