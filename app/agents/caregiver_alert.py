import os
import json
import urllib.request
from pathlib import Path

from dotenv import load_dotenv

from app.state import HazardState

load_dotenv(
    dotenv_path=Path(__file__).resolve().parents[2] / ".env"
)


def caregiver_alert(state: HazardState) -> dict:
    """Send a Telegram notification only for high-risk assessments."""

    if state.get("risk_level", "medium").lower() != "high":
        return {
            "caregiver_alert_sent": False,
            "caregiver_alert_error": "",
        }

    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not token or not chat_id:
        return {
            "caregiver_alert_sent": False,
            "caregiver_alert_error": (
                "Telegram credentials are missing from .env."
            ),
        }

    hazards = state.get("hazards", [])
    precautions = state.get("precautions", [])

    lines = [
        "🚨 HIGH-RISK SAFETY ALERT",
        "",
        f"Person: {state.get('person_type', 'adult')}",
        f"Setting: {state.get('setting', 'unknown')}",
        f"Risk: {state.get('risk_level', 'high').upper()}",
        f"Possible danger: {state.get('predicted_risk', 'Unknown')}",
        "",
        "Detected hazards:",
    ]

    lines.extend(f"- {hazard}" for hazard in hazards)

    lines.extend(["", "Recommended precautions:"])
    lines.extend(
        f"- {item}" for item in precautions
    )

    lines.extend([
        "",
        "This is an automated advisory. Verify the situation "
        "and seek emergency assistance when necessary.",
    ])

    payload = {
        "chat_id": chat_id,
        "text": "\n".join(lines),
    }

    url = f"https://api.telegram.org/bot{token}/sendMessage"

    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            result = json.load(response)

        if result.get("ok"):
            return {
                "caregiver_alert_sent": True,
                "caregiver_alert_error": "",
            }

        return {
            "caregiver_alert_sent": False,
            "caregiver_alert_error": "Telegram rejected the message.",
        }

    except Exception as exc:
        return {
            "caregiver_alert_sent": False,
            "caregiver_alert_error": (
                f"Telegram delivery failed: {type(exc).__name__}."
            ),
        }
