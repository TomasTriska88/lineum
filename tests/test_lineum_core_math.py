import numpy as np
import pytest
from lineum_core.math import (
    evolve, sigmoid, diffuse_complex, diffuse_real,
    _finite_clip, _cap_complex_magnitude, _finite_complex
)

def test_sigmoid():
    assert sigmoid(0.0) == 0.5
    assert sigmoid(100.0) > 0.99
    assert sigmoid(-100.0) < 0.01

def test_diffuse_complex():
    field = np.zeros((5, 5), dtype=np.complex128)
    kappa = np.ones((5, 5), dtype=np.float64)
    field[2, 2] = 1.0 + 1.0j
    diffused = diffuse_complex(field, kappa, rate=0.1)
    # The center should lose 4 * 0.1 = 0.4
    assert np.isclose(diffused[2, 2], -0.4 - 0.4j)
    # The neighbors should gain 0.1
    assert np.isclose(diffused[1, 2], 0.1 + 0.1j)
    assert np.isclose(diffused[3, 2], 0.1 + 0.1j)
    assert np.isclose(diffused[2, 1], 0.1 + 0.1j)
    assert np.isclose(diffused[2, 3], 0.1 + 0.1j)

def test_diffuse_real():
    field = np.zeros((5, 5), dtype=np.float64)
    kappa = np.ones((5, 5), dtype=np.float64)
    field[2, 2] = 1.0
    diffused = diffuse_real(field, kappa, rate=0.1)
    assert np.isclose(diffused[2, 2], -0.4)
    assert np.isclose(diffused[1, 2], 0.1)

def test_finite_clip():
    arr = np.array([0.0, np.inf, -np.inf, np.nan, 5.0])
    clipped = _finite_clip(arr, lo=-1.0, hi=10.0, nan=0.0, posinf=10.0, neginf=-1.0)
    assert np.allclose(clipped, [0.0, 10.0, -1.0, 0.0, 5.0])

def test_cap_complex_magnitude():
    z = np.array([1.0, 10.0, 100.0]) + 0j
    capped = _cap_complex_magnitude(z, cap=5.0)
    assert np.allclose(capped, [1.0, 5.0, 5.0])

def test_finite_complex():
    z = np.array([complex(1.0, 1.0), complex(np.inf, 0.0), complex(0.0, np.nan), complex(np.nan, np.inf)])
    safe_z = _finite_complex(z, nan=0.0)
    assert np.all(np.isfinite(safe_z))

def test_evolve_basic_shapes_and_finiteness():
    """
    Test that the evolve function returns arrays of the correct shape and type
    without any NaN or Inf values, even starting from aggressive conditions.
    """
    size = 16
    psi = np.ones((size, size), dtype=np.complex128) * 0.1
    delta = np.zeros((size, size), dtype=np.float64)
    phi = np.zeros((size, size), dtype=np.float64)
    kappa = np.ones((size, size), dtype=np.float64)

    # Set a random seed to make the linon fluctuation deterministic
    np.random.seed(42)
    
    new_psi, new_phi = evolve(psi, delta, phi, kappa)

    assert new_psi.shape == (size, size)
    assert new_phi.shape == (size, size)
    assert new_psi.dtype == np.complex128
    assert new_phi.dtype == np.float64
    assert np.all(np.isfinite(new_psi))
    assert np.all(np.isfinite(new_phi))
    
    # Phi should naturally increase slightly from 0.0 due to the reaction with psi amplitude
    assert np.any(new_phi > 0.0)
    
    # Run multiple steps to ensure stability
    for _ in range(5):
        new_psi, new_phi = evolve(new_psi, delta, new_phi, kappa)

    assert np.all(np.isfinite(new_psi))
    assert np.all(np.isfinite(new_phi))
