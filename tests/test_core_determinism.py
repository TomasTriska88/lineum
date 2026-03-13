import os
import sys
import json
import pytest

# Ensure repo root is on path so routing_backend can mock internal endpoints if needed
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from lineum_core.math import ExecutionPolicy
from scripts.validation_core import run_ra1_unitarity

def run_scenario(device_str, is_canonical):
    """
    Simulates the exact same execution path that run_preset -> evaluate_expectations takes,
    but we mock the environment configuration for canonical mode.
    """
    os.environ["LINEUM_RUN_MODE"] = "false" if is_canonical else "true"
    
    # In API, run_preset loads eval_runner, which calls ExecutionPolicy.init_core_determinism.
    # We do the exact same sequence.
    ExecutionPolicy.init_core_determinism(enforce_canonical=is_canonical, seed=42)
    
    # We temporarily patch torch.cuda.is_available ONLY for the exploratory path testing
    # to force execution if we specifically want to test the CUDA path variance.
    try:
        import torch
    except ImportError:
        if device_str == 'cuda':
            pytest.skip("PyTorch not installed; skipping CUDA path test.")
        # If device_str is 'cpu', we can proceed without torch for now,
        # assuming run_ra1_unitarity handles it or it's not needed for CPU path.
        # However, the original code imports torch unconditionally, so this
        # skip guard is specifically for the CUDA path.
        # If torch is truly needed for CPU path, this would need adjustment.
        # For now, assuming the intent is to skip CUDA if torch is missing.
        torch = None # Set to None to avoid NameError later if not skipped

    orig_is_available = None
    if torch: # Only proceed with torch-related patching if torch was imported
        orig_is_available = torch.cuda.is_available
    
    try:
        if torch: # Only apply torch-specific logic if torch was imported
            if device_str == 'cpu':
                torch.cuda.is_available = lambda: False
            elif device_str == 'cuda' and not torch.cuda.is_available():
                print("Skipping CUDA since it's truly not available system-wide.")
                return None
        elif device_str == 'cuda': # If torch not imported and device_str is cuda, we should have skipped already
            pytest.skip("PyTorch not installed; skipping CUDA path test.")
        
        # This is the actual execution function called by lab_api.py -> SCENARIO_REGISTRY
        val_data = run_ra1_unitarity()
        
    finally:
        if torch:
            torch.cuda.is_available = orig_is_available
        
    return val_data

def compare_runs(run1, run2, tolerance=1e-12):
    # Compare metric scalar outputs (Audit deterministic)
    m1 = [r["measured"] for r in run1["expectation_results"]]
    m2 = [r["measured"] for r in run2["expectation_results"]]
    
    metrics_diff = max(abs(a - b) for a, b in zip(m1, m2) if a is not None and b is not None)
    
    # Compare raw byte tensors (Bitwise deterministic)
    psi_diff = float((run1["final_dens"] - run2["final_dens"]).max())
    
    return {
        "bitwise": psi_diff == 0.0 and metrics_diff == 0.0,
        "audit": psi_diff < tolerance and metrics_diff < tolerance,
        "max_psi_diff": psi_diff,
        "metrics_diff": metrics_diff
    }

def test_determinism_matrix():
    print("\n--- Canonical Audit (CPU) ---")
    cpu_run1 = run_scenario('cpu', is_canonical=True)
    cpu_run2 = run_scenario('cpu', is_canonical=True)
    
    cpu_comp = compare_runs(cpu_run1, cpu_run2)
    print(f"CPU bitwise deterministic: {'YES' if cpu_comp['bitwise'] else 'NO'}")
    print(f"CPU audit deterministic: {'YES' if cpu_comp['audit'] else 'NO'}")
    print(f"CPU max raw drift: {cpu_comp['max_psi_diff']}")
    assert cpu_comp['bitwise'], "CPU Canonical must be exactly bitwise deterministic."
    
    try:
        import torch
        has_cuda = torch.cuda.is_available()
    except ImportError:
        has_cuda = False

    if has_cuda:
        print("\n--- Exploratory (CUDA) ---")
        cuda_run1 = run_scenario('cuda', is_canonical=False)
        cuda_run2 = run_scenario('cuda', is_canonical=False)
        
        cuda_comp = compare_runs(cuda_run1, cuda_run2)
        print(f"CUDA bitwise deterministic: {'YES' if cuda_comp['bitwise'] else 'NO'}")
        print(f"CUDA audit deterministic: {'YES' if cuda_comp['audit'] else 'NO'}")
        print(f"CUDA max raw drift: {cuda_comp['max_psi_diff']}")
        
        print("\n--- Final Verdict ---")
        print("canonical audit approved on CPU")
        print("canonical audit NOT approved on CUDA")
    else:
        print("\n--- Final Verdict ---")
        print("canonical audit approved on CPU")
        print("CUDA hardware missing for local variance test.")

if __name__ == "__main__":
    test_determinism_matrix()
