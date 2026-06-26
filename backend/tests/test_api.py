import base64
import io

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from backend.app.main import create_app


class StubInferenceService:
    def __init__(self, *, healthy=True):
        self.healthy = healthy
        self.load_error = None if healthy else "checkpoint missing"
        self.calls = 0

    @property
    def is_ready(self):
        return self.healthy

    def predict(self, image):
        self.calls += 1
        buffer = io.BytesIO()
        Image.new("RGBA", image.size, (60, 16, 152, 180)).save(buffer, format="PNG")
        encoded = base64.b64encode(buffer.getvalue()).decode("ascii")
        return {
            "mask_png_base64": encoded,
            "overlay_png_base64": encoded,
            "classes_present": [0],
            "resized": False,
            "width": image.width,
            "height": image.height,
        }


@pytest.fixture()
def client():
    app = create_app(inference_service=StubInferenceService())
    return TestClient(app)


def make_png(size=(16, 12)):
    buffer = io.BytesIO()
    Image.new("RGB", size, (24, 80, 140)).save(buffer, format="PNG")
    buffer.seek(0)
    return buffer


def test_health_reports_loaded_model(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy",
        "model_loaded": True,
        "error": None,
    }


def test_predict_returns_renderable_segmentation_response(client):
    response = client.post(
        "/predict",
        files={"file": ("tile.png", make_png(), "image/png")},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["input"] == {"width": 16, "height": 12}
    assert payload["prediction"]["format"] == "png_base64"
    assert base64.b64decode(payload["prediction"]["mask_png_base64"])
    assert base64.b64decode(payload["prediction"]["overlay_png_base64"])
    assert payload["classes"][0] == {
        "id": 0,
        "name": "building",
        "rgb": [60, 16, 152],
        "ignored": False,
    }
    assert payload["disclaimer"] == "Model prediction for demonstration only; not authoritative geospatial analysis."


def test_predict_rejects_non_image_upload(client):
    response = client.post(
        "/predict",
        files={"file": ("notes.txt", io.BytesIO(b"not an image"), "text/plain")},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Upload must be a supported image file."


def test_predict_rejects_oversized_image(client):
    response = client.post(
        "/predict",
        files={"file": ("large.png", make_png(size=(2048, 2048)), "image/png")},
    )

    assert response.status_code == 413
    assert "exceeds the 1048576 pixel limit" in response.json()["detail"]


def test_unhealthy_model_state_fails_health_and_inference():
    app = create_app(inference_service=StubInferenceService(healthy=False))
    client = TestClient(app)

    health = client.get("/health")
    assert health.status_code == 503
    assert health.json() == {
        "status": "unhealthy",
        "model_loaded": False,
        "error": "checkpoint missing",
    }

    response = client.post(
        "/predict",
        files={"file": ("tile.png", make_png(), "image/png")},
    )
    assert response.status_code == 503
    assert response.json()["detail"] == "Model is not loaded; inference is unavailable."
