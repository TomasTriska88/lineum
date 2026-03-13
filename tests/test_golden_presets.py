import pytest
from scripts.validation_core import run_particle_playground

def test_golden_presets_pass_first_run():
    """
    Test that the default presets defined in the Lab UI (H, He, P-State, Double Well, Ring)
    pass all stability expectations unconditionally on their first run.
    This guarantees that the User does not face Auto-Fix workflows for standard presets.
    """
    presets = [
        {"name": "H_ground", "Z": 1.0, "eps": 0.1, "dt": 0.05, "potential_type": "coulomb", "excited_state": 0},
        {"name": "He_ground", "Z": 2.0, "eps": 0.1, "dt": 0.02, "potential_type": "coulomb", "excited_state": 0},
        {"name": "P_state", "Z": 1.0, "eps": 0.1, "dt": 0.05, "potential_type": "coulomb", "excited_state": 1},
        {"name": "Double_well", "Z": 1.0, "eps": 0.1, "dt": 0.05, "potential_type": "double_well", "excited_state": 0},
        {"name": "Ring_pot", "Z": 1.0, "eps": 0.1, "dt": 0.05, "potential_type": "ring", "excited_state": 0},
    ]

    for p in presets:
        config = {
            "mode": "validate",  # Enforce rigorous checking instead of exploration
            "grid_size": 64,
            "Z": p["Z"],
            "eps": p["eps"],
            "dt": p["dt"],
            "potential_type": p["potential_type"],
            "excited_state": p["excited_state"],
            "physics_mode_psi": "wave_projected_soft"
        }

        # Run the core validation function directly
        result = run_particle_playground(config)
        
        # Verify the run completes and generates a verdict
        assert "overall_pass" in result, f"Result missing overall_pass for {p['name']}"
        assert result["overall_pass"] is True, f"Preset {p['name']} failed its golden stability check. Expectations: {result.get('expectation_results')}"

        # Verify edge mass is explicitly below strict tolerance
        ts = result.get("ts_metrics", {})
        if "edge_mass" in ts:
            max_leak = max(ts["edge_mass"])
            # Strict tolerance for localized ground states. Excited lobes or spread potentials (like double_well/ring) occupy more of the spatial grid.
            threshold = 0.25 if (p["excited_state"] > 0 or p["potential_type"] != "coulomb") else 0.10
            assert max_leak < threshold, f"Preset {p['name']} leaked too much wave packet to the edges: {max_leak} >= {threshold}"
