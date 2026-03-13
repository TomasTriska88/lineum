import os
import sys
import json
import pytest
torch = pytest.importorskip("torch")
import numpy as np

# Add repo root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from lineum_core.math import step_core, CoreConfig

def run_sim(grid_size=64, steps=10, device_str='cpu', seed=42):
    torch.manual_seed(seed)
    np.random.seed(seed)
    torch.use_deterministic_algorithms(True, warn_only=True)
    
    # Force device mock via environment for the duration of this run
    # (Since we haven't refactored math.py yet, we'll patch torch.cuda.is_available temporarily to force CPU, 
    # but for CUDA we let it be).
    
    x = np.linspace(-1, 1, grid_size)
    dx = 2.0 / grid_size
    dV = dx * dx
    X, Y = np.meshgrid(x, x)
    R = np.sqrt(X**2 + Y**2)

    psi = np.exp(-R**2 / 0.3).astype(np.complex128)
    psi /= np.sqrt(np.sum(np.abs(psi)**2) * dV)
    kappa = np.ones((grid_size, grid_size), dtype=np.float64)
    phi = np.zeros((grid_size, grid_size), dtype=np.float64)

    state = {"psi": psi.copy(), "phi": phi, "kappa": kappa}
    cfg = CoreConfig(dt=0.005, physics_mode_psi="wave_baseline", use_mode_coupling=False)

    metrics = []
    
    # Store original is_available
    orig_is_available = torch.cuda.is_available
    try:
        if device_str == 'cpu':
            torch.cuda.is_available = lambda: False
        
        for step in range(steps):
            state = step_core(state, cfg)
            amp_sum = np.sum(np.abs(state["psi"])**2)
            metrics.append(float(amp_sum))
            
    finally:
        torch.cuda.is_available = orig_is_available

    return {
        "final_psi": state["psi"],
        "metrics": metrics
    }

def compare_runs(run1, run2, tolerance=1e-12):
    psi_diff = np.abs(run1["final_psi"] - run2["final_psi"])
    max_psi_diff = np.max(psi_diff)
    
    metrics1 = np.array(run1["metrics"])
    metrics2 = np.array(run2["metrics"])
    metrics_diff = np.max(np.abs(metrics1 - metrics2))
    
    bitwise = max_psi_diff == 0.0 and metrics_diff == 0.0
    audit = max_psi_diff < tolerance and metrics_diff < tolerance
    
    return bitwise, audit, max_psi_diff, metrics_diff

if __name__ == "__main__":
    print("Running CPU vs CPU...")
    cpu1 = run_sim(device_str='cpu')
    cpu2 = run_sim(device_str='cpu')
    cpu_bit, cpu_audit, cpu_psi_d, cpu_met_d = compare_runs(cpu1, cpu2)
    print(f"CPU Bitwise Deterministic: {cpu_bit} (max diff: {cpu_psi_d})")
    print(f"CPU Audit Deterministic: {cpu_audit}")

    print("\nRunning CUDA vs CUDA...")
    if torch.cuda.is_available():
        cuda1 = run_sim(device_str='cuda')
        cuda2 = run_sim(device_str='cuda')
        cuda_bit, cuda_audit, cuda_psi_d, cuda_met_d = compare_runs(cuda1, cuda2)
        print(f"CUDA Bitwise Deterministic: {cuda_bit} (max diff: {cuda_psi_d})")
        print(f"CUDA Audit Deterministic: {cuda_audit}")
        
        print("\nRunning CPU vs CUDA cross-check...")
        cross_bit, cross_audit, cross_psi_d, cross_met_d = compare_runs(cpu1, cuda1, tolerance=1e-5)
        print(f"Cross Bitwise: {cross_bit} (max diff: {cross_psi_d})")
        print(f"Cross Audit (tol=1e-5): {cross_audit}")
    else:
        print("CUDA not available on this system.")
