import pytest
import numpy as np

from routing_backend.text_to_wave_encoder import TextToWaveEncoder
from lineum_core.math import Eq4Config, step_eq4

def create_virgin_state(grid_size=64):
    return {
        "psi": np.zeros((grid_size, grid_size), dtype=np.complex128),
        "phi": np.zeros((grid_size, grid_size), dtype=np.float64),
        "kappa": np.ones((grid_size, grid_size), dtype=np.float64),
        "mu": np.zeros((grid_size, grid_size), dtype=np.float64),
    }

def test_encoder_identity_burn():
    cfg = Eq4Config(use_mu=True, stencil_type="LAP4")
    # Reduce plasticity_tau for faster tests
    encoder = TextToWaveEncoder(grid_size=64, plasticity_tau=30)
    state = create_virgin_state()
    
    # 1. Single input yields basic delta in mu
    text = "The core principle of Lineum is topological stability."
    state1, metrics1 = encoder.encode(text, state, cfg, step_eq4, mode="identity_burn")
    
    mu_delta_1 = np.sum(state1["mu"])
    assert mu_delta_1 > 0, "identity_burn should write to mu"
    assert metrics1["identity_drift_index"] > 0, "Drift index should increase"
    
    # 2. Repeated input yields exponentially larger delta
    state2, metrics2 = encoder.encode(text, state1, cfg, step_eq4, mode="identity_burn")
    
    mu_delta_2 = np.sum(state2["mu"]) - np.sum(state1["mu"])
    assert mu_delta_2 > mu_delta_1, f"Repeated exposure expected to be stronger. {mu_delta_2} vs {mu_delta_1}"

def test_encoder_runtime_mode():
    cfg = Eq4Config(use_mu=True, stencil_type="LAP4") 
    encoder = TextToWaveEncoder(grid_size=64, plasticity_tau=30)
    state = create_virgin_state()
    
    # Runtime Mode should NOT alter mu
    text = "Transient short-term pulse."
    state_rt, metrics = encoder.encode(text, state, cfg, step_eq4, mode="runtime")
    
    mu_delta = np.sum(state_rt["mu"])
    assert mu_delta == 0.0, "runtime mode should NOT write to mu even if cfg.use_mu was originally True"
    assert metrics["identity_drift_index"] == 0.0, "Drift should be zero for pure runtime mode"
    assert metrics["plasticity_retention"] > 0.0, "Phi should still capture the transient memory"
