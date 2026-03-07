"""
Tests for the /api/lab/run_preset claim verification endpoint.
Validates:
- Whitelist enforcement (404 for unknown presets)
- Required response fields (manifest_id, resolved_claim_status, etc.)
- Scenario execution returns valid data
- Audit context is included in response
"""
from fastapi.testclient import TestClient
import pytest
from routing_backend.main import app

client = TestClient(app)

VALID_PRESETS = [
    "preset-frequency-sweep",
    "preset-defect-genesis",
    "preset-absolute-zero",
]

def test_unknown_preset_returns_404():
    """Unknown preset_name must be rejected with 404."""
    res = client.get("/api/lab/run_preset?preset_name=nonexistent-preset")
    assert res.status_code == 404
    assert "Unknown preset" in res.json()["detail"]

def test_missing_preset_name_returns_422():
    """Missing preset_name query param must return 422."""
    res = client.get("/api/lab/run_preset")
    assert res.status_code == 422

def test_preset_frequency_sweep_returns_required_fields():
    """
    /run_preset with a valid preset must return all authoritative fields:
    manifest_id, resolved_claim_status, scenario_id, claim_id, audit context.
    """
    res = client.get("/api/lab/run_preset?preset_name=preset-frequency-sweep")
    assert res.status_code == 200
    data = res.json()

    # Required authoritative fields
    assert "manifest_id" in data, "manifest_id missing"
    assert "resolved_claim_status" in data, "resolved_claim_status missing"
    assert "scenario_id" in data, "scenario_id missing"
    assert "claim_id" in data, "claim_id missing"
    assert "audit_status" in data, "audit_status missing"
    assert "active_profile" in data, "active_profile missing"
    assert "contract_id" in data, "contract_id missing"
    assert "overall_pass" in data, "overall_pass missing"

    # Scenario mapping validation
    assert data["scenario_id"] == "preset-frequency-sweep"
    assert data["claim_id"] == "CL-001"

    # manifest_id must not be empty
    assert data["manifest_id"], "manifest_id must not be empty"

def test_resolved_claim_status_is_valid():
    """resolved_claim_status must be one of the 4 allowed values."""
    res = client.get("/api/lab/run_preset?preset_name=preset-frequency-sweep")
    assert res.status_code == 200
    data = res.json()

    allowed = {"SUPPORTED", "CONTRADICTED", "EXPERIMENTAL_SUPPORTED", "EXPERIMENTAL_CONTRADICTED"}
    assert data["resolved_claim_status"] in allowed, \
        f"Unexpected status: {data['resolved_claim_status']}"

def test_canonical_status_requires_audited():
    """
    If audit_status == AUDITED, resolved_claim_status must be
    SUPPORTED or CONTRADICTED (not EXPERIMENTAL_*).
    If audit_status != AUDITED, it must be EXPERIMENTAL_*.
    """
    res = client.get("/api/lab/run_preset?preset_name=preset-frequency-sweep")
    assert res.status_code == 200
    data = res.json()

    if data["audit_status"] == "AUDITED":
        assert data["resolved_claim_status"] in ("SUPPORTED", "CONTRADICTED"), \
            f"AUDITED build must return canonical status, got: {data['resolved_claim_status']}"
    else:
        assert data["resolved_claim_status"].startswith("EXPERIMENTAL_"), \
            f"Non-AUDITED build must return EXPERIMENTAL status, got: {data['resolved_claim_status']}"

def test_preset_defect_genesis_maps_to_cl002():
    """preset-defect-genesis must map to CL-002."""
    res = client.get("/api/lab/run_preset?preset_name=preset-defect-genesis")
    assert res.status_code == 200
    data = res.json()
    assert data["claim_id"] == "CL-002"
    assert data["manifest_id"]

def test_preset_absolute_zero_maps_to_cl010():
    """preset-absolute-zero must map to CL-010."""
    res = client.get("/api/lab/run_preset?preset_name=preset-absolute-zero")
    assert res.status_code == 200
    data = res.json()
    assert data["claim_id"] == "CL-010"
    assert data["manifest_id"]


# ══════════════════════════════════════════════════════════════
# Bulk Verification + Persistence Tests
# ══════════════════════════════════════════════════════════════

def test_verify_all_returns_all_testable():
    """POST /verify_all must return results for all TESTABLE_NOW claims."""
    res = client.post("/api/lab/verify_all")
    assert res.status_code == 200
    data = res.json()

    assert "results" in data
    assert "summary" in data

    # All 3 registry entries should be tested
    results = data["results"]
    assert "CL-001" in results, "CL-001 missing from verify_all results"
    assert "CL-002" in results, "CL-002 missing from verify_all results"
    assert "CL-010" in results, "CL-010 missing from verify_all results"

    # Each result must have resolved_claim_status
    for cid, r in results.items():
        assert "resolved_claim_status" in r
        assert "manifest_id" in r
        assert "checked_at" in r


def test_verify_all_summary_fields():
    """verify_all must return summary with tested/supported/contradicted/experimental/skipped."""
    res = client.post("/api/lab/verify_all")
    assert res.status_code == 200
    summary = res.json()["summary"]

    for field in ["tested_count", "supported", "contradicted", "experimental", "skipped"]:
        assert field in summary, f"Summary missing '{field}'"

    assert summary["tested_count"] == 3, f"Expected 3 tested, got {summary['tested_count']}"


def test_claim_results_returns_saved_data():
    """GET /claim_results must return previously saved claim results."""
    # First run a preset to ensure persistence
    client.get("/api/lab/run_preset?preset_name=preset-frequency-sweep")

    res = client.get("/api/lab/claim_results")
    assert res.status_code == 200
    data = res.json()

    assert "results" in data
    results = data["results"]
    assert "CL-001" in results, "CL-001 not in persisted results"

    cl001 = results["CL-001"]
    assert "resolved_claim_status" in cl001
    assert "manifest_id" in cl001
    assert "checked_at" in cl001
    assert "git_commit" in cl001
    assert "equation_fingerprint" in cl001
    assert "is_stale" in cl001


def test_claim_results_has_stale_count():
    """GET /claim_results must report stale_count."""
    res = client.get("/api/lab/claim_results")
    assert res.status_code == 200
    data = res.json()
    assert "stale_count" in data
    assert isinstance(data["stale_count"], int)


def test_run_preset_persists_context_fields():
    """/run_preset must return and persist checked_at, git_commit, equation_fingerprint."""
    res = client.get("/api/lab/run_preset?preset_name=preset-frequency-sweep")
    assert res.status_code == 200
    data = res.json()

    assert "checked_at" in data, "checked_at missing"
    assert "git_commit" in data, "git_commit missing"
    assert "equation_fingerprint" in data, "equation_fingerprint missing"
    assert data["checked_at"], "checked_at must not be empty"


# ══════════════════════════════════════════════════════════════
# Health Endpoint Tests
# ══════════════════════════════════════════════════════════════

def test_health_returns_all_required_fields():
    """/health must return git_commit, audit_status, active_profile, active_contract_id."""
    res = client.get("/api/lab/health")
    assert res.status_code == 200
    data = res.json()

    # Core identity
    assert "git_commit" in data, "git_commit missing"
    assert len(data["git_commit"]) == 40, f"git_commit must be 40-char SHA, got: {data['git_commit']}"
    assert "git_branch" in data, "git_branch missing"
    assert data["git_branch"], "git_branch must not be empty"

    # Audit truthfulness
    assert "audit_status" in data, "audit_status missing"
    assert data["audit_status"] in ("AUDITED", "OUTDATED", "NONE"), \
        f"Invalid audit_status: {data['audit_status']}"

    # Contract info
    assert "active_contract_id" in data, "active_contract_id missing"
    assert "equation_fingerprint" in data, "equation_fingerprint missing"

    # Active profile
    assert "active_profile" in data, "active_profile missing"

    # Audit paths
    assert "audit_output_wp_abs_path" in data, "audit_output_wp_abs_path missing"
    assert "active_suite_abs_path" in data, "active_suite_abs_path missing"


def test_health_no_build_unknown():
    """/health must not return placeholder 'Build: unknown'."""
    res = client.get("/api/lab/health")
    assert res.status_code == 200
    data = res.json()

    assert data.get("current_build") != "Build: unknown", "current_build must not be placeholder"
    assert data.get("git_commit") != "unknown", "git_commit must not be 'unknown'"
