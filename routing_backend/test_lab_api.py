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
        
        # Assert sweeping logic returned results (length depends on GOLDEN config)
        assert len(data["results"]) > 0
        
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
        assert msg["max_steps"] == 1000

def test_lab_ra_timeseries_endpoints():
    """
    Test that RA endpoints return JSON timeseries_data and do NOT return
    base64 if there are no heatmaps (e.g. RA-5 and RA-6) or return correctly
    formatted payloads.
    """
    # RA-1
    res1 = client.get("/api/lab/ra/unitarity")
    assert res1.status_code == 200
    data1 = res1.json()
    assert "timeseries_data" in data1
    assert "N_series" in data1["timeseries_data"]
    assert "image_b64" in data1 # Has heatmaps
    
    # RA-5 (Driving vs Dephasing)
    res5 = client.get("/api/lab/ra/driving")
    assert res5.status_code == 200
    data5 = res5.json()
    assert "timeseries_data" in data5
    assert "N_driven" in data5["timeseries_data"]
    assert "N_undriven" in data5["timeseries_data"]
    assert "image_b64" not in data5 # No heatmaps, just timeseries
    
    # RA-6 (LPF Impact)
    res6 = client.get("/api/lab/ra/lpf-impact")
    assert res6.status_code == 200
    data6 = res6.json()
    assert "timeseries_data" in data6
    assert "E_off" in data6["timeseries_data"]
    assert "image_b64" not in data6 # No heatmaps, just timeseries


def test_lab_golden_validation_gate():
    """
    CI Merge Gate: Runs golden VALIDATE scenarios (RA-1 to RA-6).
    Enforces that overall_pass == True and expectation_results are not empty.
    Failure here blocks merge.
    """
    endpoints = [
        "/api/lab/ra/unitarity",
        "/api/lab/ra/bound-state",
        "/api/lab/ra/driving",
        "/api/lab/ra/lpf-impact"
    ]
    
    for ep in endpoints:
        res = client.get(ep)
        assert res.status_code == 200, f"Endpoint {ep} failed with {res.status_code}"
        data = res.json()
        
        # Enforce the CI gate rule
        assert "overall_pass" in data, f"overall_pass missing in {ep}"
        assert data["overall_pass"] is True, f"Scenario {ep} failed Golden Validation (overall_pass != True)"
        
        assert "expectation_results" in data, f"expectation_results missing in {ep}"
        assert len(data["expectation_results"]) > 0, f"No expectation results found for {ep}"
        
        # Also ensure manifest is present and has no Eq4 names
        assert "manifest" in data
        assert "Eq4" not in str(data["manifest"])

def test_audit_path_enforcement():
    """
    Ensure the Whitepaper Audit suite paths are strictly bound to the
    canonical path: output_wp/runs/_whitepaper_contract/whitepaper_contract_suite.json
    """
    response = client.get("/api/lab/health")
    assert response.status_code == 200
    data = response.json()
    
    assert "audit_output_wp_abs_path" in data
    abs_path = data["audit_output_wp_abs_path"]
    
    import os
    assert os.path.isabs(abs_path), f"Path {abs_path} is not absolute!"
    assert "routing_backend" not in abs_path, "Path must not be inside routing_backend!"
    assert abs_path.endswith("output_wp"), f"Path must end with output_wp, got: {abs_path}"
    
    # Canonical suite path enforcement
    suite_path = data.get("active_suite_abs_path")
    if suite_path:
        normalized = suite_path.replace("\\", "/")
        assert "output_wp" in normalized, "Suite path must contain output_wp"
        assert "_whitepaper_contract" in normalized, "Suite path must contain _whitepaper_contract"
        # BINDING: must be under runs/_whitepaper_contract, NOT output_wp/_whitepaper_contract
        assert "/runs/_whitepaper_contract/" in normalized, \
            f"Suite path must be under runs/_whitepaper_contract/, got: {normalized}"
        assert normalized.endswith("output_wp/runs/_whitepaper_contract/whitepaper_contract_suite.json"), \
            f"Suite path must end with canonical suffix, got: {normalized}"

def test_health_active_profile():
    """
    /health must return active_profile when an audit suite exists.
    The profile must be one of: baseline, canonical, wave_core.
    """
    response = client.get("/api/lab/health")
    assert response.status_code == 200
    data = response.json()
    
    assert "active_profile" in data, "active_profile field missing from /health"
    
    # If audit_status is AUDITED or OUTDATED, active_profile must be set
    if data.get("audit_status") in ("AUDITED", "OUTDATED"):
        assert data["active_profile"] is not None, "active_profile must not be null when audit exists"
        assert data["active_profile"] in ("baseline", "canonical", "wave_core"), \
            f"Unexpected profile: {data['active_profile']}"
