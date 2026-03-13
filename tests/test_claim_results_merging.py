import pytest
from unittest.mock import patch, mock_open
import json
from routing_backend.lab_api import get_claim_results

@pytest.fixture
def mock_static_claims():
    return [
        {
            "id": "CL-CORE-001",
            "status": "SUPPORTED",
            "scenario_id": "preset-core-001"
        },
        {
            "id": "CL-CORE-002",
            "status": "EXPERIMENTAL_RUN",
            "scenario_id": "preset-core-002"
        },
        {
            "id": "CL-CORE-003",
            "status": "UNTESTED",
            "scenario_id": "preset-core-003"
        }
    ]

@pytest.mark.asyncio
async def test_claim_results_no_evidence_is_untested(mock_static_claims):
    """
    State 1: No evidence at all -> plain UNTESTED
    """
    mock_audit_ctx = {
        "audit_status": "NONE",
        "equation_fingerprint": "unknown",
        "contract_id": "missing"
    }

    # Dynamic results are completely empty
    with patch('routing_backend.lab_api._load_claim_results', return_value={}), \
         patch('routing_backend.lab_api._get_audit_context', return_value=mock_audit_ctx), \
         patch('routing_backend.lab_api._get_current_git_commit', return_value="current-hash"), \
         patch('os.path.exists', return_value=True), \
         patch('builtins.open', mock_open(read_data=json.dumps(mock_static_claims))):

        response = await get_claim_results()
        
        # Only SUPPORTED, CONTRADICTED, or EXPERIMENTAL_RUN merge automatically
        # meaning CL-CORE-003 shouldn't even be in the results dict, and if the UI asks, it defaults to UNTESTED
        assert "CL-CORE-003" not in response["results"]


@pytest.mark.asyncio
async def test_claim_results_historical_experimental_remains_experimental(mock_static_claims):
    """
    State 2: Historical experimental evidence -> EXPERIMENTAL_RUN
    """
    mock_audit_ctx = {
        "audit_status": "NONE",
        "equation_fingerprint": "unknown",
        "contract_id": "missing"
    }

    with patch('routing_backend.lab_api._load_claim_results', return_value={}), \
         patch('routing_backend.lab_api._get_audit_context', return_value=mock_audit_ctx), \
         patch('routing_backend.lab_api._get_current_git_commit', return_value="current-hash"), \
         patch('os.path.exists', return_value=True), \
         patch('builtins.open', mock_open(read_data=json.dumps(mock_static_claims))):

        response = await get_claim_results()
        
        # EXPERIMENTAL_RUN should be merged so it doesn't drop to UNTESTED
        assert "CL-CORE-002" in response["results"]
        c2 = response["results"]["CL-CORE-002"]
        
        # Emitted semantics
        assert c2["resolved_claim_status"] == "EXPERIMENTAL_RUN"
        assert c2["verdict"] == "EXPERIMENTAL_RUN"
        assert c2["evidence_provenance"] == "EXPERIMENTAL_RUN"
        assert c2["is_stale"] == True  # Synthetic merges are stale by definition


@pytest.mark.asyncio
async def test_historical_canonical_evidence_survives_stale_dynamic_claim_payload(mock_static_claims):
    """
    State 3: Historical canonical evidence + stale current build -> STALE_EVIDENCE
    (Explicit fix for the Claims UI paradox)
    """
    mock_audit_ctx = {
        "audit_status": "REVALIDATION_REQUIRED",
        "equation_fingerprint": "hash123",
        "contract_id": "mock-contract"
    }

    with patch('routing_backend.lab_api._load_claim_results', return_value={}), \
         patch('routing_backend.lab_api._get_audit_context', return_value=mock_audit_ctx), \
         patch('routing_backend.lab_api._get_current_git_commit', return_value="current-hash"), \
         patch('os.path.exists', return_value=True), \
         patch('builtins.open', mock_open(read_data=json.dumps(mock_static_claims))):

        response = await get_claim_results()
        
        assert "CL-CORE-001" in response["results"]
        c1 = response["results"]["CL-CORE-001"]
        
        # Emitted semantics must map to STALE_EVIDENCE, not UNTESTED
        assert c1["resolved_claim_status"] == "SUPPORTED"
        assert c1["verdict"] == "SUPPORTED"
        assert c1["evidence_provenance"] == "STALE_EVIDENCE"
        assert c1["is_stale"] == True


@pytest.mark.asyncio
async def test_claim_results_clean_canonical_is_supported(mock_static_claims):
    """
    State 4: Clean canonical current build -> CANONICAL_SUITE
    """
    mock_audit_ctx = {
        "audit_status": "CANONICAL_AUDITED",
        "equation_fingerprint": "hash123",
        "contract_id": "mock-contract"
    }

    with patch('routing_backend.lab_api._load_claim_results', return_value={}), \
         patch('routing_backend.lab_api._get_audit_context', return_value=mock_audit_ctx), \
         patch('routing_backend.lab_api._get_current_git_commit', return_value="current-hash"), \
         patch('os.path.exists', return_value=True), \
         patch('builtins.open', mock_open(read_data=json.dumps(mock_static_claims))):

        response = await get_claim_results()
        
        assert "CL-CORE-001" in response["results"]
        c1 = response["results"]["CL-CORE-001"]
        
        # Emitted semantics must be flawless
        assert c1["resolved_claim_status"] == "SUPPORTED"
        assert c1["verdict"] == "SUPPORTED"
        assert c1["evidence_provenance"] == "CANONICAL_SUITE"
        assert c1["is_stale"] == False
