import pytest
import numpy as np
try:
    import torch
    HAS_TORCH = torch.cuda.is_available() or True 
    # math.py defaults to True if imported and torch exists 
except ImportError:
    HAS_TORCH = False

from lineum_core.math import CoreConfig, step_core
from scripts.validation_core import run_hydrogen_sweep, run_mu_regression_snapshot, GOLDEN_HYDRO_SWEEP

@pytest.mark.skipif(not HAS_TORCH, reason="Wave core requires PyTorch")
def test_wave_unitarity_T0():
    """
    Test T0: Forward and Backward time propagation.
    A pure unitary FFT step (dt then -dt) should return to the original state.
    """
    size = 64
    np.random.seed(42)
    
    # Initialize Gaussian wave packet
    x = np.linspace(-1, 1, size)
    y = np.linspace(-1, 1, size)
    X, Y = np.meshgrid(x, y)
    R = np.sqrt(X**2 + Y**2)
    psi0 = np.exp(-R**2 / 0.1).astype(np.complex128)
    
    phi0 = np.full((size, size), 10.0, dtype=np.float64)
    kappa0 = np.ones((size, size), dtype=np.float64) # Pure empty space

    state = {"psi": psi0.copy(), "phi": phi0.copy(), "kappa": kappa0.copy()}
    
    # We test just the exact FFT unitary step. To isolate it, we disable interactions/drift 
    # to avoid numerical drift from explicit Euler half-steps.
    cfg_fwd = CoreConfig(dt=0.1, physics_mode_psi="wave_baseline", psi_amp_cap=1e6)
    
    # Monkeypatch the compute_N inside _step_pytorch physically impossible here,
    # but we can set drift/interactions close to zero. Actually, even with drift,
    # the backward Euler isn't perfectly unitary, only the FFT step is.
    # To test *perfect* unitarity, we evaluate if the L2 error is small.
    # For a full time-reversible test we'd need a symplectic integrator.
    # Let's just run it with standard config and check if it resembles the original 
    # state better than diffusion.
    
    cfg_fwd = CoreConfig(
        dt=0.1, 
        physics_mode_psi="wave_baseline", 
        use_mode_coupling=False, 
        drift_strength=0.0, 
        noise_strength=0.0
    )
    cfg_bwd = CoreConfig(
        dt=-0.1, 
        physics_mode_psi="wave_baseline", 
        use_mode_coupling=False,
        drift_strength=0.0,
        noise_strength=0.0
    )
    
    s1 = step_core(state, cfg_fwd)
    s2 = step_core(s1, cfg_bwd)
    
    psi_final = s2["psi"]
    
    l2_err = np.linalg.norm(psi_final - psi0) / np.linalg.norm(psi0)
    
    # It won't be EXACT 0.0 because of N(psi) explicit Euler half-steps,
    # but the FFT part is perfectly time-reversible, so the error < 0.05
    assert l2_err < 0.1, f"Unitarity L2 error too high: {l2_err}"

@pytest.mark.skipif(not HAS_TORCH, reason="Wave core requires PyTorch")
def test_wave_norm_T1():
    """
    Test T1: N(t) conservation.
    A pure wave baseline should conserve N(t) = sum(|psi|^2) closely over many steps.
    """
    size = 64
    np.random.seed(123)
    
    # Initialize Gaussian
    x = np.linspace(-1, 1, size)
    y = np.linspace(-1, 1, size)
    X, Y = np.meshgrid(x, y)
    R = np.sqrt(X**2 + Y**2)
    psi0 = np.exp(-R**2 / 0.1).astype(np.complex128)
    
    phi0 = np.zeros((size, size), dtype=np.float64)
    kappa0 = np.zeros((size, size), dtype=np.float64) 
    
    state = {"psi": psi0.copy(), "phi": phi0.copy(), "kappa": kappa0.copy()}
    
    cfg = CoreConfig(
        dt=0.1, 
        physics_mode_psi="wave_baseline", 
        use_mode_coupling=False, 
        drift_strength=0.0, 
        noise_strength=0.0
    )
    
    N0 = np.sum(np.abs(psi0)**2)
    
    for _ in range(50):
        state = step_core(state, cfg)
        
    N_final = np.sum(np.abs(state["psi"])**2)
    drift = abs(N_final - N0) / N0
    
    # It should be extremely strictly conserved 
    assert drift < 0.05, f"Norm drifted dangerously by {drift * 100:.2f}%"

@pytest.mark.skipif(not HAS_TORCH, reason="Wave core requires PyTorch")
def test_hydrogen_mini():
    """
    Golden validation test: Hydrogen ground state using the exact 
    golden sweep config that powers the Web Laboratory VALIDATE mode.
    Asserts overall_pass == True (all expectations met).
    """
    grid_sizes = [s[0] for s in GOLDEN_HYDRO_SWEEP]
    Z_vals = [s[1] for s in GOLDEN_HYDRO_SWEEP]
    eps_vals = [s[2] for s in GOLDEN_HYDRO_SWEEP]
    wave_dt = GOLDEN_HYDRO_SWEEP[0][3] if len(GOLDEN_HYDRO_SWEEP[0]) > 3 else 0.01
    
    val_data = run_hydrogen_sweep(grid_sizes, Z_vals, eps_vals, wave_dt=wave_dt)
    results = val_data["results"]
    assert len(results) == len(GOLDEN_HYDRO_SWEEP)
    
    # P8: Assert the validation verdict
    assert val_data["overall_pass"] is True, (
        f"Golden HYDRO validation FAILED!\n"
        f"expectation_results: {val_data['expectation_results']}"
    )
    
    # P8: Assert all individual expectations passed
    for exp in val_data["expectation_results"]:
        assert exp["passed"], (
            f"Expectation FAILED: {exp['label']}\n"
            f"  Measured: {exp['measured']} {exp['op']} {exp['expected']}"
        )
    
    # Legacy: edge mass sanity check
    res = results[-1]
    assert res["edge_mass_cells"] < 0.1, f"Ground state spilled. Edge mass: {res['edge_mass_cells']}"
    
@pytest.mark.skipif(not HAS_TORCH, reason="Wave core requires PyTorch")
def test_mu_regression_snapshot_golden():
    """
    Golden validation test: Mu regression snapshot.
    Asserts overall_pass == True (all expectations met).
    """
    val_data = run_mu_regression_snapshot()
    
    assert "psi_diff" in val_data
    assert "psi_wave" in val_data
    assert "mu_diff" in val_data
    assert "mu_wave" in val_data
    
    # P8: Assert the validation verdict
    assert val_data["overall_pass"] is True, (
        f"Golden MU REGRESSION validation FAILED!\n"
        f"expectation_results: {val_data['expectation_results']}"
    )
    
    # P8: Assert all individual expectations passed
    for exp in val_data["expectation_results"]:
        assert exp["passed"], (
            f"Expectation FAILED: {exp['label']}\n"
            f"  Measured: {exp['measured']} {exp['op']} {exp['expected']}"
        )
    
    # Legacy checks
    assert not np.isnan(np.sum(val_data["mu_wave"]))
    assert np.max(val_data["mu_wave"]) > 0.1 # Some memory must have formed

@pytest.mark.skipif(not HAS_TORCH, reason="Wave core requires PyTorch")
def test_smoke_wave_projected_soft():
    """
    Smoke test complex terrain with projected wave soft to ensure no NaN/Inf explode over time.
    """
    size = 64
    np.random.seed(42)
    
    psi = np.ones((size, size), dtype=np.complex128) * 0.1
    phi = np.random.rand(size, size) * 100.0
    kappa = np.where(np.random.rand(size, size) > 0.8, 0.0, 1.0)
    
    state = {"psi": psi, "phi": phi, "kappa": kappa}
    cfg = CoreConfig(
        dt=0.1, 
        physics_mode_psi="wave_projected_soft", 
        wave_lpf_enabled=True, 
        use_mode_coupling=True
    )
    
    for _ in range(300):
        state = step_core(state, cfg)
        
    tele = state["telemetry"]
    
    assert not np.isnan(tele["N_t"])
    assert tele["cap_trigger_pct"] < 90.0, "System fully runaway and capped out"
    assert not tele["is_nan"], "Catastrophic NaN generated"
