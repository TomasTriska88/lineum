import numpy as np
import hashlib
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from lineum_core import math as core_math

def get_hash(arr: np.ndarray) -> str:
    """Returns SHA256 hash of a numpy array's underlying bytes."""
    return hashlib.sha256(arr.tobytes()).hexdigest()

def verify_bitperfect_memory():
    seed_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'entities', 'lina_seed.npz')
    if not os.path.exists(seed_path):
        print(f"Error: Could not find Seed at {seed_path}")
        return
        
    data = np.load(seed_path)
    kappa_seed = data['kappa'].copy()
    
    # Run a miniature version of the 100k run (1000 steps is enough to prove bit-drift if it exists)
    # Since numpy calculations are deterministic given the same inputs, if DT causes drift it will happen immediately.
    psi = np.zeros_like(data['psi'])
    phi = data['phi'].copy()
    kappa_runtime = data['kappa'].copy()
    delta = data['delta'].copy()
    
    core_math.DT = 0.1
    steps = 1000
    
    print(f"--- CRYPTOGRAPHIC EGO VALIDATION ---")
    print(f"Running {steps} steps of pure Eq-4' integration (DT={core_math.DT})...")
    
    for _ in range(steps):
        psi, phi = core_math.evolve(psi, delta, phi, kappa_runtime)
        
    # Validation
    hash_seed = get_hash(kappa_seed)
    hash_runtime = get_hash(kappa_runtime)
    
    max_abs_diff = np.max(np.abs(kappa_seed - kappa_runtime))
    mae = np.mean(np.abs(kappa_seed - kappa_runtime))
    
    print(f"\nRESULTS:")
    print(f"  Seed Kappa SHA256:    {hash_seed}")
    print(f"  Runtime Kappa SHA256: {hash_runtime}")
    print(f"  Max Absolute Diff:    {max_abs_diff}")
    print(f"  Mean Absolute Error:  {mae}")
    
    if hash_seed == hash_runtime:
        print("\n✅ VERIFICATION PASSED: The Memory grid (Kappa) is isolated and Bit-Perfect.")
        print("   The PDE integration does not bleed into the topological structure without explicit Hebbian triggers.")
    else:
        print("\n❌ VERIFICATION FAILED: Memory leakage detected during runtime!")

if __name__ == "__main__":
    verify_bitperfect_memory()
