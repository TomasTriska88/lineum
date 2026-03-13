import pytest
import os
import tempfile
import json
from unittest.mock import patch
from routing_backend.lab_api import _extract_canonical_traceability
from lineum_core.math import ExecutionPolicy
from routing_backend.eval_runner import set_seed
from fastapi.testclient import TestClient
from routing_backend.main import app

def test_canonical_metric_mapping_cl_core_001():
    # Setup dummy suite JSON
    suite_data = {
        "header": {"timestamp": "2026-03-07T12:00:00Z"},
        "runs": [
            {
                "matched_profile": "whitepaper_core",
                "metrics": {
                    "unitarity_error": 0.0001,
                    "f0_mean_hz": 432.0,
                    "sbr_mean": 42.5
                },
                "checks": {
                    "unitarity_error": {"pass": True, "max": 0.01},
                    "f0_mean_hz": {"pass": True, "min": 430, "max": 435},
                    "sbr_mean": {"pass": True, "min": 10}
                }
            }
        ]
    }
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        json.dump(suite_data, f)
        suite_path = f.name
        
    try:
        evaluations = _extract_canonical_traceability(suite_path, "CL-CORE-001", "whitepaper_core")
        
        # Should only contain f0_mean_hz and sbr_mean, NOT unitarity_error
        assert len(evaluations) == 2
        metric_names = [e["metric_name"] for e in evaluations]
        assert "f0_mean_hz" in metric_names
        assert "sbr_mean" in metric_names
        assert "unitarity_error" not in metric_names
        
        f0_eval = next(e for e in evaluations if e["metric_name"] == "f0_mean_hz")
        assert f0_eval["actual_value"] == 432.0
        assert f0_eval["passed"] is True
    finally:
        os.unlink(suite_path)


def test_eval_runner_uses_execution_policy():
    """Verify that eval_runner.set_seed strictly defers to ExecutionPolicy."""
    with patch('lineum_core.math.ExecutionPolicy.init_core_determinism') as mock_init:
        with patch.dict(os.environ, {"LINEUM_RUN_MODE": "false"}):
            set_seed(seed=42)
            mock_init.assert_called_once_with(enforce_canonical=True, seed=42)
        
    with patch('lineum_core.math.ExecutionPolicy.init_core_determinism') as mock_init:
        with patch.dict(os.environ, {"LINEUM_RUN_MODE": "true"}):
            set_seed(seed=99)
            mock_init.assert_called_once_with(enforce_canonical=False, seed=99)


def test_api_aliases():
    """Verify backend aliases for whitepapers -> claims"""
    client = TestClient(app)
    
    # Whitepapers route should redirect
    resp = client.get("/api/lab/whitepapers", follow_redirects=False)
    assert resp.status_code in (301, 302, 303, 307, 308)
    assert "/api/lab/claims" in resp.headers["location"]
    
    # Claims route should redirect to claim_results
    resp2 = client.get("/api/lab/claims", follow_redirects=False)
    assert resp2.status_code in (301, 302, 303, 307, 308)
    assert "/api/lab/claim_results" in resp2.headers["location"]


import importlib.util
has_torch = importlib.util.find_spec('torch') is not None

@pytest.mark.skipif(not has_torch, reason="Requires PyTorch")
def test_execution_policy_canonical_path():
    """Verify device rules for canonical vs exploratory paths"""
    original_device = ExecutionPolicy._device
    
    try:
        # Canonical (enforce_canonical = True) MUST result in CPU mode
        ExecutionPolicy.init_core_determinism(enforce_canonical=True, seed=1)
        assert ExecutionPolicy.get_device().type == "cpu"
        
        # Exploratory (enforce_canonical = False) could be CUDA or CPU depending on hardware
        # We just test it doesn't crash here. The logic is handled by ExecutionPolicy.
        ExecutionPolicy.init_core_determinism(enforce_canonical=False, seed=1)
        
    finally:
        ExecutionPolicy._device = original_device
