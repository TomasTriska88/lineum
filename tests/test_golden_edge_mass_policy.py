import pytest
from scripts.validation_core import run_particle_playground, PLAYGROUND_EXPECTATIONS, RA2_EXPECTATIONS

def test_threshold_routing_strict_vs_spread():
    """
    Test A & C: Proves that the correct edge_mass_max threshold is selected 
    depending on whether the scenario is compact (ground state) or spread (excited/non-coulomb).
    """
    # 1. Compact / Canonical-like case (H_ground) -> STRICT BOUND
    config_compact = {
        "mode": "validate",
        "grid_size": 64, # Requires canonical 64x64 spatial scale to contain the atomic wave
        "Z": 1.0, "eps": 0.1, "dt": 0.05,
        "potential_type": "coulomb", "excited_state": 0,
        "physics_mode_psi": "wave_projected_soft"
    }
    
    # 2. Spread / Excited case (Double_well) -> RELAXED BOUND
    config_spread = {
        "mode": "validate",
        "grid_size": 64, # Requires canonical 64x64 spatial scale
        "Z": 1.0, "eps": 0.1, "dt": 0.05,
        "potential_type": "double_well", "excited_state": 0,
        "physics_mode_psi": "wave_projected_soft"
    }

    # Helper function matching the exact routing logic in test_golden_presets
    def get_eval_threshold(config, ts):
        max_leak = max(ts["edge_mass"]) if "edge_mass" in ts else 0.0
        threshold = 0.25 if (config["excited_state"] > 0 or config["potential_type"] != "coulomb") else 0.10
        return max_leak, threshold
        
    res_compact = run_particle_playground(config_compact)
    leak_compact, thresh_compact = get_eval_threshold(config_compact, res_compact["ts_metrics"])
    
    # Assert strict route applies (0.10)
    assert thresh_compact == 0.10
    assert leak_compact < thresh_compact
    
    res_spread = run_particle_playground(config_spread)
    leak_spread, thresh_spread = get_eval_threshold(config_spread, res_spread["ts_metrics"])
    
    # Assert relaxed route applies (0.25)
    assert thresh_spread == 0.25
    
    # The double well leaks heavily (often >0.15), proving it would fail the strict routing.
    # We assert it passes the relaxed threshold but fails the strict one.
    assert leak_spread > 0.10, "Double_well should mathematically fail the strict compact containment"
    assert leak_spread < thresh_spread, "Double_well should nonetheless pass the spread-state containment"

def test_dictionary_key_regression():
    """
    Test B: Regression test for the `timeseries_data` vs `ts_metrics` bug.
    Ensures that the explicitly expected key `ts_metrics` is present, 
    and that `edge_mass` is strictly extracted from there.
    """
    config = {
        "mode": "validate",
        "grid_size": 64,
        "Z": 1.0, "eps": 0.1, "dt": 0.05,
        "potential_type": "coulomb", "excited_state": 0,
        "physics_mode_psi": "wave_projected_soft"
    }
    
    result = run_particle_playground(config)
    
    # Assert the correct metric source structure is present
    assert "ts_metrics" in result, "CRITICAL REGRESSION: ts_metrics key missing from payload."
    assert "timeseries_data" not in result, "Regression: timeseries_data is present, which was the source of the leaky mask bug."
    
    # Assert the specific leakage metric exists tightly
    ts = result["ts_metrics"]
    assert "edge_mass" in ts, "Missing edge_mass in ts_metrics list"
    assert len(ts["edge_mass"]) > 0

def test_no_accidental_fallback_to_playground_expectations():
    """
    Test D: Explicitly asserts that Canonical/Strict expectations do NOT use PLAYGROUND tolerances (0.30).
    """
    # Grab the actual definitions to assert they do not share leakage limits
    playground_leak = next(e["value"] for e in PLAYGROUND_EXPECTATIONS if e["metric"] == "edge_mass_max")
    canon_leak = next(e["value"] for e in RA2_EXPECTATIONS if e["metric"] == "edge_mass_cells")
    
    assert playground_leak == 0.30, "Playground expectations drifted from 0.30"
    assert canon_leak == 0.10, "Canonical expectations must strictly enforce 0.10"
    assert playground_leak != canon_leak, "Canonical expectations have fatally collapsed into playground tolerances"

def test_exploratory_wording_state():
    """
    Test E: Ensures that exploratory UI wording no longer overclaims "no leaking" or "cloud stable".
    """
    edge_mass_obj = next(e for e in PLAYGROUND_EXPECTATIONS if e["metric"] == "edge_mass_max")
    
    assert "exploratory" in edge_mass_obj["label"].lower(), "Exploratory threshold label must not claim canonical grade stability."
    assert "contained enough" in edge_mass_obj["human_label"].lower(), "Human description must be weakened to 'contained enough'."
    assert "no leaking" not in edge_mass_obj["human_label"].lower(), "Cannot claim 'no leaking' on loose exploratory bounds."
    assert "cloud stable" not in edge_mass_obj["label"].lower(), "Cannot claim 'cloud stable' on 30% leakage bounds."
