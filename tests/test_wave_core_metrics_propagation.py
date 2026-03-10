from unittest.mock import patch, mock_open
import os

from routing_backend.lab_api import verify_all, SCENARIO_REGISTRY
from routing_backend import lab_api

import asyncio

def test_is_audit_grade_flag_injection():
    """
    Test that verify_all properly persists the is_audit_grade flag in claim_results.json.
    This prevents the UI health endpoint from down-rating CANONICAL_SUITE evidence 
    back to EXPERIMENTAL_RUN.
    """
    
    mock_ctx = {
        "audit_status": "AUDITED",
        "contract_id": "test-contract-1.0",
        "active_profile": "wave_core",
        "equation_fingerprint": "abc123mockfingerprint",
        "output_wp_dir": "/mock/dir",
        "suite_abs_path": "/mock/suite.json",
        "contract_timestamp": "2026-01-01T00:00:00Z",
        "contract_commit": "mockcommit",
        "audit_relevant_code_fingerprint": "mockfp",
        "current_audit_relevant_code_fingerprint": "mockfp",
        "summary_pass": 1,
        "summary_fail": 0,
    }

    mock_claims_data = [
        {
            "id": "CL-CORE-001",
            "canonical_claim_set": "REQUIRED_FOR_PROMOTION",
            "testability": "TESTABLE_NOW",
            "verification_spec_status": "APPROVED"
        }
    ]

    # To isolate, we just patch the essential dependencies that verify_all touches
    with patch("routing_backend.lab_api._get_audit_context", return_value=mock_ctx), \
         patch("routing_backend.lab_api._get_current_git_commit", return_value="mockcommit"), \
         patch("routing_backend.lab_api.save_run"), \
         patch("routing_backend.lab_api._save_claim_result"), \
         patch.dict(os.environ, {"NODE_ENV": "development", "VITE_NODE_ENV": "development"}):
         
        # We need to temporarily mock the runner function to avoid executing actual physics
        # (This keeps the unit test fast and decoupled from lineum physics math)
        original_runners = lab_api._RUNNERS.copy()
        
        for k in lab_api._RUNNERS:
            lab_api._RUNNERS[k] = lambda: {"overall_pass": True, "manifest": {}, "expectations": [], "expectation_results": []}

        try:
            # Trigger verify_all synchronously
            res = asyncio.run(verify_all())
            results = res.get("results", {})
            
            # Since the claim CL-CORE-001 was APPROVED and TESTABLE_NOW, it should have been executed.
            assert "CL-CORE-001" in results, "verify_all did not execute the claim scenario"
            
            cl1 = results["CL-CORE-001"]
            
            # Verify the flag injection
            assert "is_audit_grade" in cl1, "is_audit_grade flag is missing from saved claim result"
            assert cl1["is_audit_grade"] is True, "is_audit_grade should be True for AUDITED context"
            assert cl1["resolved_claim_status"] == "SUPPORTED", "Status should be SUPPORTED (not EXPERIMENTAL_SUPPORTED)"

        finally:
            # Restore runners
            lab_api._RUNNERS = original_runners
