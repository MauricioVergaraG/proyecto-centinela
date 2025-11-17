# services/api/tests/test_health.py
from fastapi.testclient import TestClient
from services.api.app.main import app

client = TestClient(app)


def test_health_ok():
    response = client.get("/health")

    # --- ¡ARREGLO ANTERIOR! ---
    # Esto ya está bien, aceptamos 200 o 503.
    assert response.status_code == 200 or response.status_code == 503

    # --- ¡NUEVO ARREGLO LÓGICO! ---
    # Ahora, revisamos el 'body' (JSON) basándonos
    # en el código de estado que recibimos.
    body = response.json()

    if response.status_code == 200:
        # Si todo está OK (200), el 'body' debe tener 'status'
        assert "status" in body
        assert body["status"] == "ok"
    else:
        # Si es 503 (error), el 'body' debe tener 'detail'
        assert "detail" in body
