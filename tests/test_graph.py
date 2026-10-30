
from unittest.mock import patch

from app.graph import build_graph, route_after_analysis, route_after_report


def test_low_confidence_routes_to_retry():
    state = {
        "confidence": 0.3,
        "retry_count": 1,
        "hazards": ["unclear object"],
    }

    assert route_after_analysis(state) == "retry"


def test_repeated_low_confidence_routes_to_retake():
    state = {
        "confidence": 0.3,
        "retry_count": 2,
        "hazards": [],
    }

    assert route_after_analysis(state) == "retake"


def test_analysis_error_routes_to_retake():
    assert route_after_analysis({"error": "analysis failed"}) == "retake"


def test_no_hazards_routes_to_safe_result():
    state = {
        "confidence": 0.95,
        "retry_count": 0,
        "hazards": [],
    }

    assert route_after_analysis(state) == "safe"


def test_detected_hazards_route_to_risk_prediction():
    state = {
        "confidence": 0.95,
        "retry_count": 0,
        "hazards": ["wet floor"],
    }

    assert route_after_analysis(state) == "risk"


def test_only_high_risk_routes_to_caregiver_alert():
    assert route_after_report({"risk_level": "high"}) == "alert"


def test_low_and_medium_risk_do_not_route_to_alert():
    assert route_after_report({"risk_level": "low"}) == "end"
    assert route_after_report({"risk_level": "medium"}) == "end"


@patch("app.graph.caregiver_alert")
@patch("app.graph.reporter")
@patch("app.graph.scene_analyst")
def test_graph_returns_safe_result_without_running_risk_agents(
    mock_scene, mock_reporter, mock_alert
):
    mock_scene.return_value = {
        "setting": "living room",
        "hazards": [],
        "confidence": 0.95,
        "error": "",
    }

    mock_reporter.return_value = {
        "message": "No obvious hazards identified.",
        "risk_level": "low",
        "caregiver_alert_required": False,
    }

    result = build_graph().invoke({
        "image_path": "unused.jpg",
        "person_type": "adult",
        "language": "English",
        "retry_count": 0,
    })

    assert result["risk_level"] == "low"
    mock_reporter.assert_called_once()
    mock_alert.assert_not_called()


@patch("app.graph.caregiver_alert")
@patch("app.graph.reporter")
@patch("app.graph.safety_advisor")
@patch("app.graph.risk_predictor")
@patch("app.graph.scene_analyst")
def test_graph_sends_high_risk_result_to_caregiver_alert(
    mock_scene, mock_risk, mock_advisor, mock_reporter, mock_alert
):
    mock_scene.return_value = {
        "setting": "bedroom",
        "hazards": ["electrical cables across walkway"],
        "confidence": 0.95,
        "error": "",
    }

    mock_risk.return_value = {
        "risk_level": "high",
        "predicted_risk": "Trip and fall",
        "reason": "Cables obstruct the walkway.",
    }

    mock_advisor.return_value = {
        "precautions": ["Move cables away from the walkway."],
        "guideline_sources": [],
    }

    mock_reporter.return_value = {
        "message": "High risk detected.",
        "risk_level": "high",
        "caregiver_alert_required": True,
    }

    mock_alert.return_value = {
        "caregiver_alert_sent": False,
        "caregiver_alert_error": "Mocked notification",
    }

    result = build_graph().invoke({
        "image_path": "unused.jpg",
        "person_type": "elderly",
        "language": "English",
        "retry_count": 0,
    })

    assert result["risk_level"] == "high"
    mock_alert.assert_called_once()
