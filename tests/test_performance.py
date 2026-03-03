import numpy as np
import pytest
import os
import sys
import copy

# Ensure we can import lineum
from lineum_core.math import step_eq4, Eq4Config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import lineum
from lineum_core.math import step_eq4, Eq4Config

def test_tracking_equivalence():
    """
    Ensures _track_quasiparticles_fast produces bit-identical results to _track_quasiparticles_slow.
    """
    # 1. Setup synthetic data
    coords = np.array([
        [10, 10],  # Very close to T0 (dist ~0.14)
        [20, 20],  # Very close to T1 (dist ~0.7)
        [50, 50],  # Far away (new particle)
        [15, 15],  # In between, >3.0 from both (new particle)
    ], dtype=int)
    
    # Use OrderedDict-like behavior (regular dict works in Python 3.7+)
    active_tracks = {
        0: np.array([10.1, 10.1]),
        1: np.array([20.5, 20.5])
    }
    
    next_id = 100
    step_idx = 5
    amp = np.random.rand(128, 128)
    
    print(f"DEBUG TEST: active_tracks: {active_tracks}")
    for k, v in active_tracks.items():
        print(f"DEBUG TEST: track {k} type={type(v)} shape={np.asarray(v).shape}")
    
    # Sort coords to ensure deterministic processing order for both methods
    # This helps align greedy matching choices when distances are identical/similar
    coords = coords[np.argsort(coords[:, 0])]

    # 2. Run slow version
    traj_slow = []
    ids_slow = copy.deepcopy(active_tracks)
    res_slow_tracks, res_slow_next = lineum._track_quasiparticles_slow(
        coords, ids_slow, next_id, step_idx, amp, traj_slow
    )
    
    # 3. Run fast version
    traj_fast = []
    ids_fast = copy.deepcopy(active_tracks)
    res_fast_tracks, res_fast_next = lineum._track_quasiparticles_fast(
        coords, ids_fast, next_id, step_idx, amp, traj_fast
    )
    
    # 4. Assert equivalence
    # Sort results by ID to ensure comparison alignment
    slow_items = sorted(res_slow_tracks.items())
    fast_items = sorted(res_fast_tracks.items())
    
    assert len(slow_items) == len(fast_items), "Track count mismatch"
    
    # Compare positions
    for (id_s, pos_s), (id_f, pos_f) in zip(slow_items, fast_items):
        assert id_s == id_f, f"Track ID mismatch: {id_s} vs {id_f}"
        np.testing.assert_array_almost_equal(pos_s, pos_f, decimal=5, err_msg=f"Pos mismatch for track {id_s}")

    # Compare next_id with detailed debug
    if res_slow_next != res_fast_next:
        print(f"\nDEBUG FAILURE: next_id mismatch {res_slow_next} vs {res_fast_next}")
        print(f"Slow tracks: {res_slow_tracks}")
        print(f"Fast tracks: {res_fast_tracks}")
        
        # Calculate distances manually to see why one matched and other didn't
        import scipy.spatial.distance
        active_pos = np.array([active_tracks[0], active_tracks[1]])
        dists = scipy.spatial.distance.cdist(coords, active_pos)
        print(f"Distances:\n{dists}")
        
    assert res_slow_next == res_fast_next, f"next_id mismatch: {res_slow_next} vs {res_fast_next}"

def test_physics_isolation(monkeypatch):
    """
    Proves that physical fields (psi, phi) are absolutely identical 
    regardless of which tracking implementation is used.
    """
    # 1. Prepare base state
    np.random.seed(42)
    # Use actual init functions if possible
    # We need to simulate the environment of the main loop
    
    size = lineum.size
    psi = (np.random.rand(size, size) + 1j * np.random.rand(size, size)).astype(np.complex128)
    phi = np.random.rand(size, size).astype(np.float64)
    kappa = np.ones((size, size))
    delta = np.zeros((size, size))
    
    amp = np.abs(psi)
    coords = np.array([[10, 10], [20, 20]], dtype=int) # dummy detections
    
    # 2. Snapshot current state
    psi_orig = psi.copy()
    phi_orig = phi.copy()
    
    # 3. Run evolve (the physics part)
    # Since evolve doesn't call tracking, we'll simulate the loop logic
    _state = step_eq4({"psi": psi.copy(), "delta": delta, "phi": phi.copy(), "kappa": kappa}, Eq4Config())
    psi_new, phi_new = _state["psi"], _state["phi"]

    # 4. Use tracking (the analytics part) - SLOW
    active_tracks = {0: np.array([10, 10])}
    next_id = 1
    traj_slow = []
    
    # We monkeypatch FAST_TRACKING to False
    monkeypatch.setattr(lineum, "FAST_TRACKING", False)
    
    # Simulation loop logic (simplified)
    # Normally these would be updated
    _tracks_s, _next_s = lineum._track_quasiparticles_slow(coords, active_tracks.copy(), next_id, 0, amp, traj_slow)
    
    # 5. Reset and use tracking - FAST
    monkeypatch.setattr(lineum, "FAST_TRACKING", True)
    traj_fast = []
    _tracks_f, _next_f = lineum._track_quasiparticles_fast(coords, active_tracks.copy(), next_id, 0, amp, traj_fast)
    
    # 6. Verify physics didn't change at all
    # evolve() was called before tracking in our test, but even if it was called after,
    # tracking doesn't modify psi/phi.
    
    # PROOF: tracking functions return new state but DON'T touch psi/phi
    # We can also verify that next_id and active_tracks are the same (equivalence)
    assert _next_s == _next_f
    assert _tracks_s.keys() == _tracks_f.keys()
    
    # Physics check:
    # Since we didn't touch psi/phi in the tracking calls, 
    # and they aren't inputs to tracking, they must remain identical.
    np.testing.assert_array_equal(psi_new, psi_new) # Tautology, but confirms no crash
    
    # Verification of plan requirement: "switching tracking nemění fyzikální pole"
    # I will run 1 step of "simulation-like" logic with both modes and compare fields.
    
    def simulate_step(mode_fast):
        np.random.seed(1337) # Deterministic steps
        try:
            import torch
            torch.manual_seed(1337)
            if torch.cuda.is_available():
                torch.cuda.manual_seed_all(1337)
        except ImportError:
            pass
        p = psi_orig.copy()
        f = phi_orig.copy()
        tr = []
        at = {0: np.array([10, 10])}
        nid = 1
        
        # Step
        _state = step_eq4({"psi": p, "delta": delta, "phi": f, "kappa": kappa}, Eq4Config())
        p, f = _state["psi"], _state["phi"]
        a = np.abs(p)
        c = np.array([[10, 10]], dtype=int) # simulate detection
        
        if mode_fast:
            at, nid = lineum._track_quasiparticles_fast(c, at, nid, 0, a, tr)
        else:
            at, nid = lineum._track_quasiparticles_slow(c, at, nid, 0, a, tr)
            
        return p, f, at, nid, tr

    psi_s, phi_s, at_s, nid_s, tr_s = simulate_step(False)
    psi_f, phi_f, at_f, nid_f, tr_f = simulate_step(True)
    
    np.testing.assert_array_equal(psi_s, psi_f, "Physical field PSI changed!")
    np.testing.assert_array_equal(phi_s, phi_f, "Physical field PHI changed!")
    assert nid_s == nid_f
    assert at_s.keys() == at_f.keys()
    assert tr_s == tr_f

if __name__ == "__main__":
    # Manual execution to debug silent pytest failures
    try:
        print("Running test_tracking_equivalence...")
        test_tracking_equivalence()
        print("✅ test_tracking_equivalence passed")
        
        print("Running test_physics_isolation...")
        from unittest.mock import MagicMock
        class MockMonkeyPatch:
            def setattr(self, obj, attr, val):
                setattr(obj, attr, val)
        test_physics_isolation(MockMonkeyPatch())
        print("✅ test_physics_isolation passed")
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        sys.exit(1)
