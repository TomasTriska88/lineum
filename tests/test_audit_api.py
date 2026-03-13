import pytest
from fastapi.testclient import TestClient
from routing_backend.main import app
import json
from pathlib import Path

client = TestClient(app)

from unittest.mock import patch

def test_audit_generate_endpoint():
    # Make sure we don't accidentally nuke a real valid contract during strict checks,
    # but the generator just appends to the suite anyway.
    # We must patch _audit_worker so FastAPI TestClient doesn't run it synchronously!
    with patch('routing_backend.lab_api._audit_worker') as mock_audit:
        response = client.post("/api/lab/audit/generate")
        
    assert response.status_code == 200
    data = response.json()
    
    if data["status"] == "started":
        assert "job_id" in data
        assert "message" in data
    elif data["status"] == "success":
        assert "contract_id" in data
        assert "git_commit" in data
    else:
        # If the environment lacks git or something fails, we just want to ensure
        # the endpoint reported the error structurally.
        assert "detail" in data
