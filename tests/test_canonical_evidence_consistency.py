import pytest
import os
import json
from unittest.mock import patch, mock_open

from routing_backend.lab_api import verify_all, SCENARIO_REGISTRY
from routing_backend import lab_api
import asyncio

def test_canonical_evidence_consistency():
    """
    Ensures that when a claim is processed as CANONICAL_SUITE (AUDITED status),
    the resulting traceability record MUST explicitly show:
    - deterministic_mode = True
    - execution_device = 'cpu'
    - claim-specific metrics (no fallback sane-defaults like 'unitarity_error' or 'has_no_nan')
    Even if the original evaluating hardware was CUDA with non-deterministic execution.
    """
    mock_ctx = {
        "audit_status": "AUDITED",
        "contract_id": "lineum-contract-1.0",
        "active_profile": "wave_core",
        "equation_fingerprint": "abc123canonical",
        "output_wp_dir": "output_wp/runs/_whitepaper_contract",
        "suite_abs_path": os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "output_wp", "runs", "_whitepaper_contract", "whitepaper_contract_suite.json")),
        "contract_timestamp": "2026-03-10T00:00:00Z",
        "contract_commit": "mockcommit1",
        "audit_relevant_code_fingerprint": "xyz1",
        "current_audit_relevant_code_fingerprint": "xyz1",
        "summary_pass": 1,
        "summary_fail": 0,
    }

    mock_suite_json = {
        "header": {"timestamp": "2026-03-10T12:00:00Z"},
        "runs": [
            {
                "matched_profile": "wave_core",
                "metrics": {
                    "f0_mean_hz": 3.14e18,
                    "sbr_mean": 37000,
                    "topology_neutrality_n1": 42.0,
                    "mean_vortices": 10.0,
                    "phi_half_life_steps": 500,
                    "max_lifespan_steps": 800
                },
                "checks": []
            }
        ]
    }

    # Setup the claim conditions to allow them to test
    mock_claims_data = [
        {"id": "CL-CORE-001", "testability": "TESTABLE_NOW", "verification_spec_status": "APPROVED"},
        {"id": "CL-CORE-002", "testability": "TESTABLE_NOW", "verification_spec_status": "APPROVED"},
        {"id": "CL-CORE-003", "testability": "TESTABLE_NOW", "verification_spec_status": "APPROVED"}
    ]

    with patch("routing_backend.lab_api._get_audit_context", return_value=mock_ctx), \
         patch("routing_backend.lab_api._get_current_git_commit", return_value="mockcommit1"), \
         patch("routing_backend.lab_api.save_run"), \
         patch("routing_backend.lab_api._save_claim_result"), \
         patch.dict(os.environ, {"NODE_ENV": "development", "VITE_NODE_ENV": "development"}):
         
        # We need to simulate the physics execution layer.
        # We simulate that the live environment executing the runner is CUDA/Non-Deterministic.
        # This tests that the lab_api overrides this exploratory footprint for Canonical audits.
        
        # We mock ExecutionPolicy.get_metadata to return CUDA
        with patch("lineum_core.math.ExecutionPolicy.get_metadata", return_value={"execution_device": "cuda", "deterministic_mode": False}):
            original_runners = lab_api._RUNNERS.copy()
            
            # The mocked physics runners return fallback sanity metrics (unitarity_error, has_no_nan)
            # This proves that our metric extraction engine overrides exploratory metrics with the true Canonical metrics.
            fallback_expectation_results = [
                {"metric": "unitarity_error", "measured": 0.0, "expected": 1e-6, "op": "<", "passed": True},
                {"metric": "has_no_nan", "measured": 1.0, "expected": 1.0, "op": "==", "passed": True}
            ]
            
            for k in lab_api._RUNNERS:
                lab_api._RUNNERS[k] = lambda: {"overall_pass": True, "manifest": {}, "expectations": [], "expectation_results": fallback_expectation_results}

            try:
                # Execution
                res = asyncio.run(verify_all())
                results = res.get("results", {})
                
                assert "CL-CORE-001" in results
                assert "CL-CORE-002" in results
                assert "CL-CORE-003" in results
                
                # Validation - CL-CORE-001
                cl1 = results["CL-CORE-001"]
                t1 = cl1["traceability"]
                assert t1["execution_device"] == "cpu", "Canonical detail MUST render cpu, NOT cuda."
                assert t1["deterministic_mode"] is True, "Canonical detail MUST render deterministic_mode = True."
                cl1_metrics = [m["metric_name"] for m in t1["metrics"]]
                assert "f0_mean_hz" in cl1_metrics, "CL-CORE-001 must render spectral metrics."
                assert "unitarity_error" not in cl1_metrics, "CL-CORE-001 canonical detail MUST NOT fallback to generic sanity metrics."
                
                # Validation - CL-CORE-002
                cl2 = results["CL-CORE-002"]
                t2 = cl2["traceability"]
                assert t2["execution_device"] == "cpu", "Canonical detail MUST render cpu"
                assert t2["deterministic_mode"] is True, "Canonical detail MUST render True"
                cl2_metrics = [m["metric_name"] for m in t2["metrics"]]
                assert "topology_neutrality_n1" in cl2_metrics, "CL-CORE-002 must render topology metrics."
                assert "f0_mean_hz" not in cl2_metrics, "CL-CORE-002 rendered wrong metric family."

                # Validation - CL-CORE-003
                cl3 = results["CL-CORE-003"]
                t3 = cl3["traceability"]
                assert t3["execution_device"] == "cpu", "Canonical detail MUST render cpu"
                assert t3["deterministic_mode"] is True, "Canonical detail MUST render True"
                cl3_metrics = [m["metric_name"] for m in t3["metrics"]]
                assert "phi_half_life_steps" in cl3_metrics, "CL-CORE-003 must render lifespan metrics."
                assert "f0_mean_hz" not in cl3_metrics, "CL-CORE-003 rendered wrong metric family."
                
                # Evidence source is validated implicitly by the presence of is_audit_grade
                assert cl1["is_audit_grade"] is True

            finally:
                lab_api._RUNNERS = original_runners
