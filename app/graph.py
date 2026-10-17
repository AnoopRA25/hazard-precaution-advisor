
from langgraph.graph import StateGraph, START, END

from app.state import HazardState
from app.agents.scene_analyst import scene_analyst
from app.agents.risk_predictor import risk_predictor
from app.agents.safety_advisor import safety_advisor
from app.agents.reporter import reporter


def analyze_scene(state: HazardState) -> dict:
    """Analyze the image, retrying only low-confidence results."""
    result = scene_analyst(state)
    retry_count = state.get("retry_count", 0)

    result["retry_count"] = retry_count

    # Do not retry API, file, or configuration errors.
    if result.get("error"):
        return result

    if result.get("confidence", 0.0) < 0.6:
        result["retry_count"] = retry_count + 1

    return result


def route_after_analysis(state: HazardState) -> str:
    """Choose the next workflow step."""
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
    """Avoid making a safety determination when analysis fails."""
    return {
        "setting": state.get("setting", "unknown"),
        "hazards": [],
        "predicted_risk": (
            "The image could not be assessed reliably. "
            "Do not assume the area is safe."
        ),
        "risk_level": "medium",
        "precautions": [
            "Keep away from any suspected hazards until checked.",
            "Submit a clearer image or check the area in person safely.",
        ],
    }


builder = StateGraph(HazardState)

builder.add_node("scene_analyst", analyze_scene)
builder.add_node("risk_predictor", risk_predictor)
builder.add_node("safety_advisor", safety_advisor)
builder.add_node("safe_result", safe_result)
builder.add_node("retake_result", retake_result)
builder.add_node("reporter", reporter)

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
builder.add_edge("reporter", END)

graph = builder.compile()
