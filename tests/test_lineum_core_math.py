import numpy as np
import pytest
from lineum_core.math import step_core, CoreConfig, _diffuse_complex_numpy, _cap_complex_magnitude_numpy

def test_diffuse_complex_numpy():
    field = np.zeros((5, 5), dtype=np.complex128)
    kappa = np.ones((5, 5), dtype=np.float64)
    field[2, 2] = 1.0 + 1.0j
    diffused = _diffuse_complex_numpy(field, kappa, rate=0.1, stencil_type="LAP4")
    assert np.isclose(diffused[2, 2], -0.4 - 0.4j)
    assert np.isclose(diffused[1, 2], 0.1 + 0.1j)
    assert np.isclose(diffused[3, 2], 0.1 + 0.1j)
    assert np.isclose(diffused[2, 1], 0.1 + 0.1j)
    assert np.isclose(diffused[2, 3], 0.1 + 0.1j)

def test_cap_complex_magnitude_numpy():
    z = np.array([1.0, 10.0, 100.0]) + 0j
    capped = _cap_complex_magnitude_numpy(z, cap=5.0)
    assert np.allclose(capped, [1.0, 5.0, 5.0])

def test_step_core_basic_shapes_and_finiteness():
    """
    Test that the step_core function returns arrays of the correct shape and type
    without any NaN or Inf values, even starting from aggressive conditions.
    """
    size = 16
    psi = np.ones((size, size), dtype=np.complex128) * 0.1
    delta = np.zeros((size, size), dtype=np.float64)
    phi = np.zeros((size, size), dtype=np.float64)
    kappa = np.ones((size, size), dtype=np.float64)

    # Set a random seed to make the linon fluctuation deterministic
    np.random.seed(42)
    
    cfg = CoreConfig()
    state = step_core({"psi": psi, "delta": delta, "phi": phi, "kappa": kappa}, cfg)
    new_psi, new_phi = state["psi"], state["phi"]

    assert new_psi.shape == (size, size)
    assert new_phi.shape == (size, size)
    assert new_psi.dtype == np.complex128
    assert new_phi.dtype == np.float64
    assert np.all(np.isfinite(new_psi))
    assert np.all(np.isfinite(new_phi))
    
    # Run multiple steps to ensure stability
    for _ in range(5):
        state = step_core({"psi": new_psi, "delta": delta, "phi": new_phi, "kappa": kappa}, cfg)
        new_psi, new_phi = state["psi"], state["phi"]

    assert np.all(np.isfinite(new_psi))
    assert np.all(np.isfinite(new_phi))
