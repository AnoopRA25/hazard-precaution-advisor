
import json
import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

from app.state import HazardState

load_dotenv()

SUPPORTED_LANGUAGES = {"English", "Kannada", "Hindi"}

LABELS = {
    "English": {
        "setting": "Setting",
        "person": "Person",
        "hazards": "Hazards",
        "risk": "Risk level",
        "danger": "Possible danger",
        "reason": "Reason",
        "precautions": "Precautions",
        "disclaimer": "Disclaimer",
        "low": "LOW",
        "medium": "MEDIUM",
        "high": "HIGH",
    },
    "Kannada": {
        "setting": "ಸ್ಥಳ",
        "person": "ವ್ಯಕ್ತಿಯ ಪ್ರಕಾರ",
        "hazards": "ಅಪಾಯಗಳು",
        "risk": "ಅಪಾಯದ ಮಟ್ಟ",
        "danger": "ಸಂಭಾವ್ಯ ಅಪಾಯ",
        "reason": "ಕಾರಣ",
        "precautions": "ಮುನ್ನೆಚ್ಚರಿಕೆಗಳು",
        "disclaimer": "ಹಕ್ಕುತ್ಯಾಗ",
        "low": "ಕಡಿಮೆ",
        "medium": "ಮಧ್ಯಮ",
        "high": "ಹೆಚ್ಚು",
    },
    "Hindi": {
        "setting": "स्थान",
        "person": "व्यक्ति का प्रकार",
        "hazards": "खतरे",
        "risk": "जोखिम का स्तर",
        "danger": "संभावित खतरा",
        "reason": "कारण",
        "precautions": "सावधानियाँ",
        "disclaimer": "अस्वीकरण",
        "low": "कम",
        "medium": "मध्यम",
        "high": "उच्च",
    },
}

PERSON_LABELS = {
    "English": {
        "baby": "baby",
        "child": "child",
        "adult": "adult",
        "elderly": "elderly person",
    },
    "Kannada": {
        "baby": "ಶಿಶು",
        "child": "ಮಗು",
        "adult": "ವಯಸ್ಕ",
        "elderly": "ವಯೋವೃದ್ಧ ವ್ಯಕ್ತಿ",
    },
    "Hindi": {
        "baby": "शिशु",
        "child": "बच्चा",
        "adult": "वयस्क",
        "elderly": "बुज़ुर्ग व्यक्ति",
    },
}

TITLES = {
    "English": "HAZARD PRECAUTION ADVISOR",
    "Kannada": "ಅಪಾಯ ಮುನ್ನೆಚ್ಚರಿಕೆ ಸಲಹೆಗಾರ",
    "Hindi": "खतरा एवं सावधानी सलाहकार",
}

DISCLAIMER = {
    "English": "This is assistive advice, not a guarantee of safety.",
    "Kannada": "ಇದು ಸಹಾಯಕ ಸಲಹೆಯಾಗಿದ್ದು, ಸುರಕ್ಷತೆಯ ಖಾತರಿಯಲ್ಲ.",
    "Hindi": "यह केवल सहायक सलाह है, सुरक्षा की कोई गारंटी नहीं।",
}

EMERGENCY = {
    "English": "In an emergency, contact local emergency services.",
    "Kannada": "ತುರ್ತು ಪರಿಸ್ಥಿತಿಯಲ್ಲಿ ಸ್ಥಳೀಯ ತುರ್ತು ಸೇವೆಗಳನ್ನು ಸಂಪರ್ಕಿಸಿ.",
    "Hindi": "आपात स्थिति में, स्थानीय आपातकालीन सेवाओं से संपर्क करें।",
}

FALLBACK_PRECAUTIONS = {
    "English": (
        "Keep away from suspected hazards and seek qualified help."
    ),
    "Kannada": (
        "ಸಂಭಾವ್ಯ ಅಪಾಯಗಳಿಂದ ದೂರವಿರಿ ಮತ್ತು ಅರ್ಹ ವ್ಯಕ್ತಿಯ ಸಹಾಯ ಪಡೆಯಿರಿ."
    ),
    "Hindi": (
        "संभावित खतरों से दूर रहें और योग्य व्यक्ति की सहायता लें।"
    ),
}


def build_report(state: HazardState) -> dict:
    """Build the report from the graph state."""
    return {
        "title": "HAZARD PRECAUTION ADVISOR",
        "setting": state.get("setting", "unknown"),
        "person": state.get("person_type", "adult"),
        "hazards": state.get("hazards", []),
        "risk_level": state.get("risk_level", "medium").lower(),
        "predicted_danger": state.get(
            "predicted_risk",
            "The scene requires further assessment.",
        ),
        "reason": state.get("reason", ""),
        "precautions": state.get("precautions", []) or [
            FALLBACK_PRECAUTIONS["English"]
        ],
        "disclaimer": DISCLAIMER["English"],
        "emergency": EMERGENCY["English"],
    }


def translate_report(report: dict, language: str) -> dict:
    """Translate dynamic report content using Gemini."""
    if language == "English":
        return report

    api_key = os.getenv("GEMINI_API_KEY")
    model = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")

    if not api_key:
        raise ValueError("GEMINI_API_KEY is not configured.")

    client = genai.Client(api_key=api_key)

    prompt = f"""
Translate the values of this safety report into {language}.

Return ONLY valid JSON with exactly these keys:
title, setting, person, hazards, risk_level, predicted_danger,
reason, precautions, disclaimer, emergency.

Rules:
- Translate all natural-language content into {language}.
- Keep the JSON keys in English.
- Keep hazards and precautions as lists of strings.
- Preserve the meaning and seriousness of every safety warning.
- Do not add or remove hazards or precautions.
- Keep risk_level exactly as one of: low, medium, high.
- Do not change the risk assessment.
- Use clear language suitable for the general public.
- Return valid JSON only.

Report:
{json.dumps(report, ensure_ascii=False)}
"""

    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
        ),
    )

    if not response.text:
        raise ValueError("Gemini returned an empty translation.")

    translated = json.loads(response.text)

    required_keys = set(report.keys())
    if not required_keys.issubset(translated.keys()):
        raise ValueError("Translation response is missing report fields.")

    if not isinstance(translated["hazards"], list):
        raise ValueError("Translated hazards must be a list.")

    if not isinstance(translated["precautions"], list):
        raise ValueError("Translated precautions must be a list.")

    if not all(isinstance(item, str) for item in translated["hazards"]):
        raise ValueError("Every translated hazard must be text.")

    if not all(
        isinstance(item, str) for item in translated["precautions"]
    ):
        raise ValueError("Every translated precaution must be text.")

    # The model must never alter the original risk classification.
    translated["risk_level"] = report["risk_level"]

    return translated


def format_report(report: dict, language: str) -> str:
    """Format the report using localized labels and risk levels."""
    labels = LABELS[language]

    person = str(report.get("person", "adult")).lower()
    risk_level = str(report.get("risk_level", "medium")).lower()

    person_label = PERSON_LABELS[language].get(person, person)
    risk_label = labels.get(risk_level, labels["medium"])

    lines = [
        TITLES[language],
        "",
        f'{labels["setting"]}: {report["setting"]}',
        f'{labels["person"]}: {person_label}',
    ]

    hazards = report.get("hazards", [])
    if hazards:
        lines.append(
            f'{labels["hazards"]}: {", ".join(hazards)}'
        )

    lines.extend([
        f'{labels["risk"]}: {risk_label}',
        f'{labels["danger"]}: {report["predicted_danger"]}',
    ])

    reason = report.get("reason", "")
    if reason:
        lines.append(f'{labels["reason"]}: {reason}')

    lines.extend(["", f'{labels["precautions"]}:'])

    precautions = report.get("precautions", [])
    if precautions:
        lines.extend(
            f"{index}. {item}"
            for index, item in enumerate(precautions, start=1)
        )
    else:
        lines.append(FALLBACK_PRECAUTIONS[language])

    lines.extend([
        "",
        f'{labels["disclaimer"]}: {report["disclaimer"]}',
        report["emergency"],
    ])

    return "\n".join(lines)


def reporter(state: HazardState) -> dict:
    """Generate a readable report in English, Kannada, or Hindi."""
    language = state.get("language", "English")

    if language not in SUPPORTED_LANGUAGES:
        language = "English"

    original_report = build_report(state)
    report = original_report
    translation_error = ""

    if language != "English":
        try:
            report = translate_report(original_report, language)

            # Apply trusted fixed translations for these standard fields.
            report["title"] = TITLES[language]
            report["disclaimer"] = DISCLAIMER[language]
            report["emergency"] = EMERGENCY[language]

            if not report.get("precautions"):
                report["precautions"] = [
                    FALLBACK_PRECAUTIONS[language]
                ]

        except Exception as exc:
            translation_error = (
                f"Translation to {language} failed: {exc}. "
                "The report is provided in English."
            )
            language = "English"
            report = original_report

    risk_level = str(
        state.get("risk_level", "medium")
    ).lower()

    return {
        "message": format_report(report, language),
        "caregiver_alert_required": risk_level == "high",
        "translation_error": translation_error,
    }
