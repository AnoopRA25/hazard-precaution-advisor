from io import BytesIO
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.api import app

client = TestClient(app)


def test_home_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "running"


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_invalid_person_type_is_rejected():
    response = client.post(
        "/analyze",
        data={"person_type": "unknown", "language": "English"},
        files={"image": ("test.jpg", b"image-data", "image/jpeg")},
    )
    assert response.status_code == 400


def test_invalid_language_is_rejected():
    response = client.post(
        "/analyze",
        data={"person_type": "adult", "language": "French"},
        files={"image": ("test.jpg", b"image-data", "image/jpeg")},
    )
    assert response.status_code == 400


def test_unsupported_media_type_is_rejected():
    response = client.post(
        "/analyze",
        data={"person_type": "adult", "language": "English"},
        files={"image": ("test.gif", b"not-an-image", "image/gif")},
    )
    assert response.status_code == 415


def test_invalid_image_content_is_rejected():
    response = client.post(
        "/analyze",
        data={"person_type": "adult", "language": "English"},
        files={"image": ("test.jpg", b"not-a-real-image", "image/jpeg")},
    )
    assert response.status_code == 400

def test_analyze_endpoint_returns_report():
    fake_result = {
        "setting": "bedroom",
        "person_type": "elderly",
        "language": "English",
        "hazards": ["loose electrical cables", "scattered objects"],
        "confidence": 0.95,
        "risk_level": "high",
        "predicted_risk": "Fall or trip injury",
        "reason": "Loose cables and scattered objects create trip hazards.",
        "precautions": [
            "Move cables away from walking paths.",
            "Remove scattered objects from the floor.",
        ],
        "guideline_sources": [],
        "message": "High risk detected. Please remove the hazards.",
        "error": "",
        "translation_error": "",
        "caregiver_alert_required": True,
        "caregiver_alert_sent": True,
        "caregiver_alert_error": "",
    }

    from PIL import Image
    from io import BytesIO

    image_buffer = BytesIO()
    Image.new("RGB", (20, 20), color="white").save(
        image_buffer, format="JPEG"
    )
    image_bytes = image_buffer.getvalue()

    with patch("app.api.graph.invoke", return_value=fake_result):
        response = client.post(
            "/analyze",
            data={
                "person_type": "elderly",
                "language": "English",
            },
            files={
                "image": (
                    "bedroom.jpg",
                    image_bytes,
                    "image/jpeg",
                )
            },
        )

    assert response.status_code == 200
    result = response.json()

    assert result["risk_level"] == "high"
    assert result["person_type"] == "elderly"
    assert result["hazards"] == [
        "loose electrical cables",
        "scattered objects",
    ]
    assert result["caregiver_alert_required"] is True
    assert result["caregiver_alert_sent"] is True
    assert result["message"] == (
        "High risk detected. Please remove the hazards."
    )
