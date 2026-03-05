from fastapi.testclient import TestClient
import pytest
import base64
from routing_backend.main import app

client = TestClient(app)

def test_lab_hydrogen_sweep_rest():
    try:
        response = client.get("/api/lab/hydrogen/sweep")
        assert response.status_code == 200
        data = response.json()
        
        assert "results" in data
        assert "image_b64" in data
        
        # Assert sweeping logic returned 5 sweep variations
        assert len(data["results"]) == 5
        
        # Verify image integrity
        img_bytes = base64.b64decode(data["image_b64"])
        assert img_bytes.startswith(b'\x89PNG\r\n\x1a\n') # Valid PNG header
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise

def test_lab_regression_snapshot_rest():
    """
    Test the Mu Memory Substrate regression endpoint comparing diff and wave.
    """
    response = client.get("/api/lab/regression/snapshot")
    assert response.status_code == 200
    data = response.json()
    
    assert "image_b64" in data
    
    img_bytes = base64.b64decode(data["image_b64"])
    assert img_bytes.startswith(b'\x89PNG\r\n\x1a\n')

def test_lab_hydrogen_websocket():
    """
    Test real-time WS streaming of Hydrogen wave collapse
    """
    with client.websocket_connect("/api/lab/hydrogen") as websocket:
        msg = websocket.receive_json()
        assert "step" in msg
        assert "dens_flat" in msg
        assert "n_t" in msg
        # Physics mode check (Phase A starts in diffusion cooling)
        assert msg["phase"] == "Cooling (Imaginary Time)"

def test_lab_regression_websocket():
    """
    Test real-time WS transmission of Mu memory tracking
    """
    with client.websocket_connect("/api/lab/regression") as websocket:
        msg = websocket.receive_json()
        assert "step" in msg
        assert "max_steps" in msg
        assert "diff_mu" in msg
        assert "wave_mu" in msg
        assert msg["max_steps"] == 1000
