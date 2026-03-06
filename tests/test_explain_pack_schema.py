import pytest
from scripts.validation_core import (
    run_hydrogen_sweep,
    run_mu_regression_snapshot,
    run_particle_playground,
    run_ra1_unitarity,
    run_ra2_bound_state,
    run_ra3_excited_state,
    run_ra4_mu_memory,
    run_ra5_driving,
    run_ra6_lpf_impact
)

MANDATORY_KEYS = {
    "one_liner_human",
    "what_you_see",
    "what_it_is_not",
    "success_criteria_human",
    "next_action_pass",
    "next_action_fail",
    "disclaimers",
    "glossary_terms_used"
}

def verify_pack(res, scenario_name):
    assert "explain_pack" in res, f"Scenario {scenario_name} missing explain_pack"
    pack = res["explain_pack"]
    missing = MANDATORY_KEYS - set(pack.keys())
    assert not missing, f"Scenario {scenario_name} missing mandatory keys: {missing}"
    
    # Check types
    assert isinstance(pack["one_liner_human"], str)
    assert isinstance(pack["what_you_see"], list)
    assert isinstance(pack["what_it_is_not"], list)
    assert isinstance(pack["success_criteria_human"], str)
    assert isinstance(pack["next_action_pass"], str)
    assert isinstance(pack["next_action_fail"], str)
    assert isinstance(pack["disclaimers"], list)
    assert isinstance(pack["glossary_terms_used"], list)

@pytest.mark.fast
def test_explain_pack_hydro():
    res = run_hydrogen_sweep([32], [1.0], [0.1], wave_dt=0.01)
    verify_pack(res, "hydrogen_sweep")

@pytest.mark.fast
def test_explain_pack_mu_reg():
    res = run_mu_regression_snapshot()
    verify_pack(res, "mu_regression")

@pytest.mark.fast
def test_explain_pack_playground():
    config = {"mode": "validate", "grid_size": 32, "Z": 1.0, "eps": 0.1, "dt": 0.1, "physics_mode_psi": "wave_baseline"}
    res = run_particle_playground(config)
    verify_pack(res, "playground")

@pytest.mark.fast
def test_explain_pack_ra_scenarios():
    verify_pack(run_ra1_unitarity(), "ra1")
    verify_pack(run_ra2_bound_state(), "ra2")
    verify_pack(run_ra3_excited_state(), "ra3")
    verify_pack(run_ra4_mu_memory(), "ra4")
    verify_pack(run_ra5_driving(), "ra5")
    verify_pack(run_ra6_lpf_impact(), "ra6")
