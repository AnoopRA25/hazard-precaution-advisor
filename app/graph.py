
from langgraph.graph import StateGraph, START, END

from app.state import HazardState
from app.agents.scene_analyst import scene_analyst
from app.agents.risk_predictor import risk_predictor
from app.agents.safety_advisor import safety_advisor
from app.agents.reporter import reporter
from app.agents.caregiver_alert import caregiver_alert


def analyze_scene(state: HazardState) -> dict:
    """Analyze the image and track low-confidence retries."""
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
    """Prepare a cautious report when no hazard is detected."""
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
    """Avoid declaring an area safe when analysis is unreliable."""
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
    """Send caregiver alerts only for high-risk assessments."""
    if state.get("risk_level", "medium").lower() == "high":
        return "alert"

    return "end"


def build_graph():
    """Build a fresh graph using the currently configured agent functions."""
    builder = StateGraph(HazardState)

    # Register all nodes.
    builder.add_node("scene_analyst", analyze_scene)
    builder.add_node("risk_predictor", risk_predictor)
    builder.add_node("safety_advisor", safety_advisor)
    builder.add_node("safe_result", safe_result)
    builder.add_node("retake_result", retake_result)
    builder.add_node("reporter", reporter)
    builder.add_node("caregiver_alert", caregiver_alert)

    # Start with image analysis.
    builder.add_edge(START, "scene_analyst")

    # Route according to the image-analysis result.
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

    # Hazard assessment and precaution generation.
    builder.add_edge("risk_predictor", "safety_advisor")
    builder.add_edge("safety_advisor", "reporter")

    # Safe and unreliable-analysis results also get reported.
    builder.add_edge("safe_result", "reporter")
    builder.add_edge("retake_result", "reporter")

    # Send alerts only when the reported risk is high.
    builder.add_conditional_edges(
        "reporter",
        route_after_report,
        {
            "alert": "caregiver_alert",
            "end": END,
        },
    )

    builder.add_edge("caregiver_alert", END)

    return builder.compile()


# The application uses this compiled graph.
graph = build_graph()
