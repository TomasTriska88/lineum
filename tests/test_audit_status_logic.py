import os
import sys
import json
from unittest.mock import patch, mock_open, MagicMock

from routing_backend.lab_api import _get_audit_context

def test_audit_context_status_resolutions():
    """Test the exact rules for AUDITED, BUILD_NEWER, and REVALIDATION_REQUIRED."""
    
    suite_data = {
        "header": {
            "timestamp": "2026-03-10T12:00:00Z",
            "contract_id": "test-contract-123",
            "git_commit": "aaaa1111",
            "equation_fingerprint": "hash-eq-math",
            "audit_relevant_code_fingerprint": "hash-code-fingerprint"
        },
        "summary": {"pass": 1, "fail": 0},
        "runs": [
            {"matched_profile": "wave_core", "status": "PASS", "metrics": {"test_metric": 1.0}}
        ]
    }
    suite_json = json.dumps(suite_data)
        
    # 1. SCENARIO: Perfect Match (AUDITED)
    with patch('subprocess.check_output', return_value=b"aaaa1111"):
        with patch('routing_backend.lab_api.Path.exists', return_value=True):
            with patch('routing_backend.lab_api.Path.read_text', return_value="AUDITED"):
                with patch('routing_backend.lab_api.open', mock_open(read_data=suite_json)):
                    mock_fp = MagicMock(return_value="hash-code-fingerprint")
                    with patch.dict('sys.modules', {'whitepaper_contract': MagicMock(compute_audit_relevant_fingerprint=mock_fp)}):
                        ctx = _get_audit_context()
                    assert ctx["audit_status"] == "AUDITED"
                    assert ctx["audit_relevant_code_fingerprint"] == "hash-code-fingerprint"
                    assert ctx["active_profile"] == "wave_core"

    # 2. SCENARIO: Equation matches, Git differs (BUILD_NEWER)
    with patch('subprocess.check_output', return_value=b"bbbb2222"): # New commit!
        with patch('routing_backend.lab_api.Path.exists', return_value=True):
            with patch('routing_backend.lab_api.Path.read_text', return_value="AUDITED"):
                with patch('routing_backend.lab_api.open', mock_open(read_data=suite_json)):
                    mock_fp = MagicMock(return_value="hash-code-fingerprint")
                    with patch.dict('sys.modules', {'whitepaper_contract': MagicMock(compute_audit_relevant_fingerprint=mock_fp)}): # Eq still same!
                        ctx = _get_audit_context()
                    assert ctx["audit_status"] == "BUILD_NEWER"
                    assert ctx["current_audit_relevant_code_fingerprint"] == "hash-code-fingerprint"

    # 3. SCENARIO: Equation Differs (REVALIDATION_REQUIRED)
    with patch('subprocess.check_output', return_value=b"bbbb2222"):
        with patch('routing_backend.lab_api.Path.exists', return_value=True):
            with patch('routing_backend.lab_api.Path.read_text', return_value="AUDITED"):
                with patch('routing_backend.lab_api.open', mock_open(read_data=suite_json)):
                    mock_fp = MagicMock(return_value="hash-code-CHANGED")
                    with patch.dict('sys.modules', {'whitepaper_contract': MagicMock(compute_audit_relevant_fingerprint=mock_fp)}): # MATH CHANGED!
                        ctx = _get_audit_context()
                    assert ctx["audit_status"] == "REVALIDATION_REQUIRED"
