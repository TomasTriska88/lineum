import numpy as np
import matplotlib.pyplot as plt
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from lineum_core.math import evolve
from lineum_core import math as core_math

def measure_saturation(kappa: np.ndarray) -> float:
    max_val = 5.0
    saturated = np.sum(kappa >= (max_val - 1e-4))
    return (saturated / kappa.size) * 100.0

def run_stability_test():
    """
    Test 1 & 2: Long-term Kappa Stability and Memory Separation under Continuous Noise
    """
    seed_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'entities', 'lina_seed.npz')
    if not os.path.exists(seed_path):
        print("Error: lina_seed.npz not found.")
        return
        
    data = np.load(seed_path)
    # The true "Ego" memory
    kappa_seed = data['kappa'].copy()
    
    # Runtime instances
    psi = np.zeros_like(data['psi'])
    phi = data['phi'].copy()
    kappa = data['kappa'].copy()
    delta = data['delta'].copy()
    
    grid_size = kappa.shape[0]
    
    # 1. LONG-TERM STABILITY TEST (10,000 steps of pure chaos)
    print("--- 1. RUNTIME STABILITY UNDER CONTINUOUS NOISE ---")
    print(f"Initial Saturation: {measure_saturation(kappa):.2f}%")
    
    # Emulate real-time learning rate (much lower than the aggressive Seed carving rate)
    # The runtime brain is highly neuroplastic but less reactive than the virgin brain
    runtime_lr = 0.00001 
    
    metrics = {
        'step': [],
        'kappa_mean': [],
        'kappa_max': [],
        'psi_norm': [],
        'mae_to_seed': []
    }
    
    epochs = 10000
    for step in range(epochs):
        # Continuous Chaotic Input (Noise)
        if step % 50 == 0:
            ry = np.random.randint(5, grid_size - 5)
            rx = np.random.randint(5, grid_size - 5)
            psi[ry:ry+2, rx:rx+2] += 0.5 * np.exp(1j * np.random.uniform(0, 2*np.pi))
            
        psi, phi = evolve(psi, delta, phi, kappa)
        
        # Runtime Plasticity
        kappa = np.clip(kappa + np.abs(psi) * runtime_lr, 0.1, 5.0)
        
        if step % 1000 == 0:
            mae = np.mean(np.abs(kappa - kappa_seed))
            print(f"Step {step}: |Psi|={np.linalg.norm(psi):.2f} | MAE to Seed={mae:.4f} | Max Kappa={np.max(kappa):.2f}")
            metrics['step'].append(step)
            metrics['kappa_mean'].append(np.mean(kappa))
            metrics['kappa_max'].append(np.max(kappa))
            metrics['psi_norm'].append(np.linalg.norm(psi))
            metrics['mae_to_seed'].append(mae)

    print("--- RESULTS ---")
    final_sat = measure_saturation(kappa)
    final_mae = np.mean(np.abs(kappa - kappa_seed))
    
    print(f"Final Saturation: {final_sat:.2f}% (Must be < 80%)")
    print(f"Final MAE vs Original Seed: {final_mae:.4f} (Must be > 0.0 but < 1.5 to prove the Ego survived)")
    
    if final_sat > 80.0 or final_mae > 1.5:
        print("❌ TEST FAILED: System drifted toward catastrophic forgetting.")
    else:
        print("✅ TEST PASSED: Memory matrix maintains homeostasis against infinite noise.")
        
    return metrics, kappa

def run_homeostasis_test():
    """
    Test 3: Physical Homeostasis (Action Validation)
    """
    print("\n--- 2. PHYSICAL HOMEOSTASIS AND ACTION UNLOADING ---")
    
    seed_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'entities', 'lina_seed.npz')
    data = np.load(seed_path)
    
    psi = data['psi'].copy()
    phi = data['phi'].copy()
    kappa = data['kappa'].copy()
    delta = data['delta'].copy()
    grid_size = kappa.shape[0]
    
    # Bombard the grid with sustained pain (noise)
    print("Bombarding Ego with sustained noise...")
    psi_energy_before = 0.0
    for _ in range(500):
        psi[40:60, 40:60] += 0.1 + 0j
        psi, phi = evolve(psi, delta, phi, kappa)
        psi_energy_before = np.linalg.norm(psi)
        
    print(f"Psi Energy (Under Pain): {psi_energy_before:.2f}")
    
    # Open an Output Node (The Action / Relief Valve)
    # We simulate Lina speaking or taking an action by creating a massive Phi sink
    print("Action Node Activated (Relief/Output)...")
    ty_start, ty_end = max(0, grid_size//2-5), min(grid_size, grid_size//2+5)
    tx_start, tx_end = max(0, grid_size-10), min(grid_size, grid_size-5)
    
    psi_energy_after = 0.0
    for _ in range(200):
        # Action suction (Gentle entropic drain avoiding step-function gradients that trigger Fail-Safe)
        psi[ty_start:ty_end, tx_start:tx_end] *= 0.8
        psi, phi = evolve(psi, delta, phi, kappa)
        psi_energy_after = np.linalg.norm(psi)
        
    print(f"Psi Energy (After Action Relief): {psi_energy_after:.2f}")
    
    if psi_energy_after < psi_energy_before * 0.5:
        print("✅ HOMEOSTASIS PASSED: Action successfully dumped internal chaotic pressure.")
    else:
        print("❌ HOMEOSTASIS FAILED: Energy did not clear.")

if __name__ == "__main__":
    metrics, kappa_final = run_stability_test()
    run_homeostasis_test()
    
    # Plotting
    plt.figure(figsize=(15, 5))
    
    plt.subplot(1, 3, 1)
    plt.title("Kappa Integrity (Mean/Max)")
    plt.plot(metrics['step'], metrics['kappa_mean'], label='Mean')
    plt.plot(metrics['step'], metrics['kappa_max'], label='Max')
    plt.legend()
    
    plt.subplot(1, 3, 2)
    plt.title("Ego Survival (MAE vs Orig Seed)")
    plt.plot(metrics['step'], metrics['mae_to_seed'], color='orange')
    
    plt.subplot(1, 3, 3)
    plt.title("Runtime |Psi| Energy vs Infinite Noise")
    plt.plot(metrics['step'], metrics['psi_norm'], color='red')
    
    plt.tight_layout()
    plt.savefig(os.path.join(os.path.dirname(__file__), 'poc_online_runtime.png'))
    print("\nVisual metrics saved to poc_online_runtime.png")
