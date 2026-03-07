"""Tests for wave-core contract profile and multi-profile evaluation."""
import json
import os
import pytest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
CONTRACT_PATH = os.path.join(ROOT, 'contracts', 'lineum-core-1.0.18-core.contract.json')

@pytest.fixture
def contract():
    with open(CONTRACT_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def test_contract_has_three_profiles(contract):
    """Contract must have baseline, canonical, and wave_core profiles."""
    names = [p["name"] for p in contract["profiles"]]
    assert "baseline" in names
    assert "canonical" in names
    assert "wave_core" in names
    assert len(names) == 3

def test_legacy_canonical_unchanged(contract):
    """Legacy canonical profile must retain original thermodynamic anchors."""
    canonical = [p for p in contract["profiles"] if p["name"] == "canonical"][0]
    anchors = canonical["checks"]["numerical_anchors"]
    # These are the original legacy anchors — must not be modified
    assert "f0_mean_hz" in anchors
    assert "topology_neutrality_n1" in anchors
    assert "mean_vortices" in anchors
    assert "sbr_mean" in anchors
    assert "phi_half_life_steps" in anchors
    # Check specific legacy values
    assert anchors["f0_mean_hz"]["min"] == 3.5e+19
    assert anchors["topology_neutrality_n1"]["min"] == 70.0

def test_wave_core_no_legacy_anchors(contract):
    """Wave-core profile must NOT contain legacy-only thermodynamic metrics."""
    wave_core = [p for p in contract["profiles"] if p["name"] == "wave_core"][0]
    anchors = wave_core["checks"]["numerical_anchors"]
    legacy_only = ["f0_mean_hz", "topology_neutrality_n1", "mean_vortices", "sbr_mean", "phi_half_life_steps"]
    for metric in legacy_only:
        assert metric not in anchors, f"Legacy metric {metric} should not be in wave_core profile"

def test_wave_core_metrics_defined(contract):
    """Wave-core profile must define all approved metrics with correct types."""
    wave_core = [p for p in contract["profiles"] if p["name"] == "wave_core"][0]
    anchors = wave_core["checks"]["numerical_anchors"]
    
    # HARD metrics
    assert "M2_total" in anchors
    assert anchors["M2_total"]["severity"] == "fatal"
    assert "target" in anchors["M2_total"]
    assert "rel_tol" in anchors["M2_total"]
    
    assert "low_mass_qp_count" in anchors
    assert anchors["low_mass_qp_count"]["severity"] == "fatal"
    
    assert "net_charge" in anchors
    assert anchors["net_charge"]["target"] == 0
    assert anchors["net_charge"]["abs_tol"] == 0
    
    assert "peak_phi" in anchors
    assert anchors["peak_phi"]["max"] == 1e6
    
    # SUPPORT metrics
    assert "center_amp" in anchors
    assert anchors["center_amp"]["severity"] == "support"
    assert anchors["center_amp"]["min"] == 500
    
    assert "vortices_total" in anchors
    assert anchors["vortices_total"]["severity"] == "support"
    assert anchors["vortices_total"]["min"] == 10
    
    # INFO metrics
    assert "final_particle_count" in anchors
    assert anchors["final_particle_count"]["severity"] == "info"

def test_wave_core_invariants(contract):
    """Wave-core profile must enforce standard invariants."""
    wave_core = [p for p in contract["profiles"] if p["name"] == "wave_core"][0]
    invariants = wave_core["checks"]["invariants"]
    assert invariants["dim"] == "2D"
    assert invariants["bcs"] == "periodic"
    assert invariants["precision"] == "float64"

def test_suite_has_matched_profile():
    """Suite runs must include matched_profile field."""
    suite_path = os.path.join(ROOT, 'output_wp', 'runs', '_whitepaper_contract', 'whitepaper_contract_suite.json')
    if not os.path.exists(suite_path):
        pytest.skip("Suite not generated yet")
    with open(suite_path, 'r', encoding='utf-8') as f:
        suite = json.load(f)
    for run in suite["runs"]:
        assert "matched_profile" in run, f"Run {run['run_id']} missing matched_profile"
        assert run["matched_profile"] in ["baseline", "canonical", "wave_core"]
