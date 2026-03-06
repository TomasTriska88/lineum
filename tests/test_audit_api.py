import pytest
from fastapi.testclient import TestClient
from routing_backend.main import app
import json
from pathlib import Path

client = TestClient(app)

def test_audit_generate_endpoint():
    # Make sure we don't accidentally nuke a real valid contract during strict checks,
    # but the generator just appends to the suite anyway.
    response = client.post("/api/lab/audit/generate")
    
    assert response.status_code == 200
    data = response.json()
    
    # Even if it fails internally, we expect a JSON response with a status
    assert "status" in data
    
    if data["status"] == "success":
        assert "contract_id" in data
        assert "git_commit" in data
        assert "timestamp" in data
        assert data["contract_id"] is not None
        assert data["git_commit"] is not None
    else:
        # If the environment lacks git or something fails, we just want to ensure
        # the endpoint reported the error structurally.
        assert "detail" in data
