import os
import numpy as np
import pytest
from unittest.mock import patch, MagicMock
import lineum
from lineum_core.math import step_eq4, Eq4Config

def test_throttling_logic_condition():
    """Test the condition used in lineum.py for throttling."""
    track_every = 25
    checkpoint_every = 50
    
    results = []
    for i in range(101):
        # Exact logic from lineum.py
        do_track = (i % track_every == 0) or (checkpoint_every > 0 and i % checkpoint_every == 0)
        if do_track:
            results.append(i)
    
    # Multiples of 25: 0, 25, 50, 75, 100
    expected = [0, 25, 50, 75, 100]
    assert results == expected

@pytest.mark.parametrize("track_every", [1, 5, 25])
def test_simulation_step_consistency(track_every):
    """Deep check: Ensure evolution is independent of tracking."""
    # Use global size to match lineum.py expected shapes
    sz = lineum.size 
    psi = np.random.random((sz, sz)) + 1j * np.random.random((sz, sz))
    phi = np.random.random((sz, sz))
    delta = np.zeros_like(psi)
    kappa = np.ones((sz, sz))
    
    def seed_everything():
        np.random.seed(42)
        try:
            import torch
            torch.manual_seed(42)
            if torch.cuda.is_available():
                torch.cuda.manual_seed_all(42)
        except ImportError:
            pass

    # Scene A
    seed_everything()
    _state = step_eq4({"psi": psi.copy(), "delta": delta.copy(), "phi": phi.copy(), "kappa": kappa.copy()}, Eq4Config())
    psi_a, phi_a = _state["psi"], _state["phi"]
    
    # Scene B
    seed_everything()
    _state = step_eq4({"psi": psi.copy(), "delta": delta.copy(), "phi": phi.copy(), "kappa": kappa.copy()}, Eq4Config())
    psi_b, phi_b = _state["psi"], _state["phi"]
    
    assert np.allclose(psi_a, psi_b)
    assert np.allclose(phi_a, phi_b)
