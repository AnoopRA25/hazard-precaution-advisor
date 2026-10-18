from copy import deepcopy
from unittest.mock import patch

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


def fake_translation(report, language):
    """Simulate a successful translation without calling Gemini."""
    translated = deepcopy(report)

    if language == "Kannada":
        translated.update({
            "setting": "ಒಳಾಂಗಣ ಮಲಗುವ ಕೋಣೆ",
            "person": "ವಯೋವೃದ್ಧ ವ್ಯಕ್ತಿ",
            "hazards": ["ನಡೆಯುವ ಹಾದಿಯಲ್ಲಿ ವಿದ್ಯುತ್ ಕೇಬಲ್‌ಗಳು"],
            "predicted_danger": "ಕೇಬಲ್‌ಗಳಿಂದ ಎಡವಿ ಬೀಳಬಹುದು.",
            "reason": "ನಡೆಯುವ ಹಾದಿಯಲ್ಲಿ ಎಡವಿ ಬೀಳುವ ಅಪಾಯವಿದೆ.",
            "precautions": [
                "ನಡೆಯುವ ಹಾದಿಯನ್ನು ಕೇಬಲ್‌ಗಳಿಂದ ಮುಕ್ತವಾಗಿಡಿ.",
                "ನೆಲದ ಮೇಲಿರುವ ಅಡೆತಡೆಗಳನ್ನು ತೆರವುಗೊಳಿಸಿ.",
            ],
        })
    elif language == "Hindi":
        translated.update({
            "setting": "घर के अंदर का शयनकक्ष",
            "person": "बुज़ुर्ग व्यक्ति",
            "hazards": ["रास्ते में बिजली के तार"],
            "predicted_danger": "तारों के कारण कोई गिर सकता है।",
            "reason": "चलने के रास्ते में ठोकर लगने का खतरा है।",
            "precautions": [
                "चलने के रास्ते से तार हटाएँ।",
                "फर्श से बिखरी वस्तुएँ हटाएँ।",
            ],
        })

    return translated


def test_english_report():
    result = reporter(sample_state("English"))

    assert "HAZARD PRECAUTION ADVISOR" in result["message"]
    assert "Risk level: HIGH" in result["message"]
    assert result["caregiver_alert_required"] is True
    assert result["translation_error"] == ""


@patch("app.agents.reporter.translate_report", side_effect=fake_translation)
def test_kannada_report(mock_translate):
    result = reporter(sample_state("Kannada"))

    assert "ಅಪಾಯ ಮುನ್ನೆಚ್ಚರಿಕೆ ಸಲಹೆಗಾರ" in result["message"]
    assert "ಅಪಾಯದ ಮಟ್ಟ: ಹೆಚ್ಚು" in result["message"]
    assert "ನಡೆಯುವ ಹಾದಿಯಲ್ಲಿ ವಿದ್ಯುತ್ ಕೇಬಲ್‌ಗಳು" in result["message"]
    assert result["caregiver_alert_required"] is True
    assert result["translation_error"] == ""
    mock_translate.assert_called_once()


@patch("app.agents.reporter.translate_report", side_effect=fake_translation)
def test_hindi_report(mock_translate):
    result = reporter(sample_state("Hindi"))

    assert "खतरा एवं सावधानी सलाहकार" in result["message"]
    assert "जोखिम का स्तर: उच्च" in result["message"]
    assert "रास्ते में बिजली के तार" in result["message"]
    assert result["caregiver_alert_required"] is True
    assert result["translation_error"] == ""
    mock_translate.assert_called_once()


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
