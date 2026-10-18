from app.agents.reporter import reporter


def sample_state(language="English", risk_level="high"):
    return {
        "language": language,
        "person_type": "elderly",
        "setting": "indoor bedroom",
        "hazards": ["Power cables across the walking path"],
        "risk_level": risk_level,
        "predicted_risk": "Cables may cause a trip or fall.",
        "reason": "The walking area contains trip hazards.",
        "precautions": [
            "Keep the walking path clear of cables.",
            "Remove loose objects from the floor.",
        ],
    }


def test_english_report():
    result = reporter(sample_state("English"))
    assert "HAZARD PRECAUTION ADVISOR" in result["message"]
    assert "Risk level: HIGH" in result["message"]
    assert result["caregiver_alert_required"] is True
    assert result["translation_error"] == ""


def test_kannada_report():
    result = reporter(sample_state("Kannada"))
    assert "ಅಪಾಯ ಮುನ್ನೆಚ್ಚರಿಕೆ ಸಲಹೆಗಾರ" in result["message"]
    assert "ಅಪಾಯದ ಮಟ್ಟ: ಹೆಚ್ಚು" in result["message"]
    assert result["caregiver_alert_required"] is True


def test_hindi_report():
    result = reporter(sample_state("Hindi"))
    assert "खतरा एवं सावधानी सलाहकार" in result["message"]
    assert "जोखिम का स्तर: उच्च" in result["message"]
    assert result["caregiver_alert_required"] is True


def test_low_risk_does_not_require_caregiver_alert():
    result = reporter(sample_state("English", "low"))
    assert "Risk level: LOW" in result["message"]
    assert result["caregiver_alert_required"] is False


def test_medium_risk_does_not_require_caregiver_alert():
    result = reporter(sample_state("English", "medium"))
    assert "Risk level: MEDIUM" in result["message"]
    assert result["caregiver_alert_required"] is False


def test_invalid_language_falls_back_to_english():
    result = reporter(sample_state("French"))
    assert "HAZARD PRECAUTION ADVISOR" in result["message"]
    assert result["translation_error"] == ""
