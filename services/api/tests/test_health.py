# services/api/tests/test_health.py
from fastapi.testclient import TestClient
from services.api.main import app

client = TestClient(app)


def test_health_ok():
    response = client.get("/health")

    assert response.status_code == 200
    body = response.json()

    assert "status" in body
    assert body["status"] == "ok"
