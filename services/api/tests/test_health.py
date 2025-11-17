# services/api/tests/test_health.py
from fastapi.testclient import TestClient

# --- ¡AQUÍ ESTÁ EL ARREGLO CLAVE! ---
# Usamos una importación relativa.
# Le decimos a Python: "Sube un nivel (..) y luego entra en 'app.main'"
from ..app.main import app 

client = TestClient(app)

def test_health_ok():
    response = client.get("/health")
    
    # Aceptamos 200 (OK) o 503 (API viva, pero BD/Redis caídos)
    assert response.status_code == 200 or response.status_code == 503
    
    body = response.json()
    
    if response.status_code == 200:
        assert 'status' in body
        assert body['status'] == 'ok'
    else:
        # Si es 503, esperamos 'detail'
        assert 'detail' in body