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
