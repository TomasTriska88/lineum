from fastapi.testclient import TestClient
from portal.src.lib.data.routing_backend.main import app

client = TestClient(app)

print("--- Testing REST Regression ---")
try:
    response = client.get("/api/lab/regression/snapshot")
    assert response.status_code == 200
    data = response.json()
    assert "image_b64" in data
    print("REST Regression OK")
except Exception as e:
    import traceback
    traceback.print_exc()

print("--- Testing WS Regression ---")
try:
    with client.websocket_connect("/api/lab/regression") as websocket:
        msg = websocket.receive_json()
        assert "step" in msg
        assert "max_steps" in msg
        assert "diff_mu" in msg
        assert "wave_mu" in msg
        assert msg["max_steps"] == 1000
    print("WS Regression OK")
except Exception as e:
    import traceback
    traceback.print_exc()
