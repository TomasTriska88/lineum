import pytest
from fastapi.testclient import TestClient
import sys
import os
import asyncio
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from routing_backend.main import app
from routing_backend.engraving_api import active_jobs

client = TestClient(app)

def test_engraving_sse_headers_and_stream():
    """
    Ensure the SSE endpoint returns correct Content-Type and CORS headers,
    and handles missing jobs correctly without crashing.
    """
    # 1. Test missing job
    response = client.get("/api/engraving/stream/nonexistent_job")
    assert response.status_code == 404
    assert response.json() == {"detail": "Job not found"}

    # 2. Mock a job in active_jobs
    job_id = "test_job_123"
    active_jobs[job_id] = {
        "status": "completed",
        "progress": 100,
        "logs": ["Test log"],
        "cancel_requested": False
    }

    # Test the stream returns SSE headers
    response = client.get(f"/api/engraving/stream/{job_id}")
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/event-stream; charset=utf-8"
    assert response.headers["cache-control"] == "no-cache"
    assert "access-control-allow-origin" in response.headers

    # Read the streamed response manually
    import re
    match = re.search(r"data:\s*({.*})", response.text)
    assert match is not None, f"Could not find SSE data event in: {response.text}"
    
    payload = json.loads(match.group(1))
    assert payload["status"] == "completed"
    assert payload["progress"] == 100
    assert "Test log" in payload["logs"]

    # Clean up
    del active_jobs[job_id]

def test_engraving_cancel_job():
    """
    Ensure a running job can be cancelled, updating its dictionary state.
    """
    job_id = "test_job_cancel"
    active_jobs[job_id] = {
        "status": "running",
        "progress": 10,
        "logs": ["Running..."],
        "cancel_requested": False
    }

    res = client.post(f"/api/engraving/cancel/{job_id}")
    assert res.status_code == 200
    assert res.json() == {"status": "cancelling"}
    assert active_jobs[job_id]["cancel_requested"] is True

    # Clean up
    del active_jobs[job_id]
