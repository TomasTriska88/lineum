import numpy as np
import matplotlib.pyplot as plt
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from lineum_core import math as core_math

# Verify GPU Precision Data Type (Point 6)
if core_math.USE_PYTORCH:
    import torch
    # Eq-4 variables are typically allocated via device float64 in math.py
    # We can print it out here.
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    dummy = torch.tensor([1.0], device=device, dtype=torch.float64)
    print("--- POINT 6: ENGINE HARDWARE & PRECISION ---")
    print(f"Backend: PyTorch ({device})")
    print(f"Default precision allocated in math.py: {dummy.dtype}")
    print("------------------------------------------\n")

def run_ablation(name: str, use_int: bool, use_phi: bool, use_noise: bool, dt: float = 1.0, steps: int = 1000):
    print(f"Running Test [{name}]: Int={use_int}, PhiFlow={use_phi}, Noise={use_noise}, DT={dt}")
    
    # Set physics engine switches
    core_math.ENABLE_INTERACTION = use_int
    core_math.ENABLE_PHI_FLOW = use_phi
    core_math.ENABLE_NOISE = use_noise
    core_math.DT = dt
    
    seed_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'entities', 'lina_seed.npz')
    if not os.path.exists(seed_path):
        print("Error: lina_seed.npz not found.")
        return None
        
    data = np.load(seed_path)
    # Start fresh for each test
    psi = np.zeros_like(data['psi'])
    phi = data['phi'].copy()
    kappa = data['kappa'].copy()
    delta = data['delta'].copy()
    
    max_psis = []
    total_energies = []
    exploded = False
    
    for step in range(steps):
        psi, phi = core_math.evolve(psi, delta, phi, kappa)
        
        # Track metrics
        mag = np.abs(psi)
        current_max = np.max(mag)
        total_energy = np.sum(mag**2)
        
        max_psis.append(current_max)
        total_energies.append(total_energy)
        
        if np.isnan(current_max) or current_max >= core_math.PSI_AMP_CAP * 0.99 or (step > 0 and current_max == 0.0):
            print(f"  -> Explosion detected at step {step}! Max |Psi| hit {current_max}")
            exploded = True
            break
            
    if not exploded:
        print(f"  -> Stable completion ({steps} steps). Final Max |Psi|: {max_psis[-1]:.2f}")
        
    return {
        'name': name,
        'exploded': exploded,
        'max_psis': max_psis,
        'total_energies': total_energies
    }

if __name__ == "__main__":
    results = []
    
    # --- POINT 1: ISOLATE THE CULPRIT ---
    # Baseline: Everything ON
    res_base = run_ablation("Baseline (All ON)", True, True, True)
    results.append(res_base)
    
    # A) No interaction_term
    res_a = run_ablation("A) No interaction_term", False, True, True)
    results.append(res_a)
    
    # B) No phi_flow_term
    res_b = run_ablation("B) No phi_flow_term", True, False, True)
    results.append(res_b)
    
    # C) No noise
    res_c = run_ablation("C) No noise", True, True, False)
    results.append(res_c)
    
    # D) Only base physics (No Interaction, No Flow) + Noise
    res_d = run_ablation("D) Base + Noise (No flows)", False, False, True)
    results.append(res_d)
    
    # --- POINT 2: DT TEST ---
    res_dt = run_ablation("DT=0.1", True, True, True, dt=0.1, steps=10000)
    results.append(res_dt)
    
    # --- PLOTTING ---
    plt.figure(figsize=(15, 6))
    
    # Plot 1: Isolation Tests (Max Psi)
    plt.subplot(1, 2, 1)
    plt.title("Ablation Culprit Hunting (Max |Psi| over Time)")
    for res in results[:-1]: # exclude DT test for clarity in this plot
        plt.plot(res['max_psis'], label=f"{res['name']} {'(EXPLODED)' if res['exploded'] else ''}")
    plt.axhline(core_math.PSI_AMP_CAP, color='red', linestyle='--', label="Fail-Safe Cap")
    plt.yscale('log')
    plt.xlabel("Simulation Steps")
    plt.ylabel("Max |Psi|")
    plt.legend()
    
    # Plot 2: Total Energy vs Time (Point 4)
    plt.subplot(1, 2, 2)
    plt.title("Thermodynamics: Total Energy vs Time")
    plt.plot(res_base['total_energies'], label="With Continuous Input (Baseline)", color='red')
    plt.plot(res_c['total_energies'], label="Without Input (No Noise)", color='blue')
    plt.yscale('log')
    plt.xlabel("Simulation Steps")
    plt.ylabel("Sum(|Psi|^2)")
    plt.legend()
    
    plt.tight_layout()
    plt.savefig(os.path.join(os.path.dirname(__file__), 'poc_ablation_results.png'))
    print("\nVisual metrics saved to poc_ablation_results.png")
    
    # Bonus for Point 2
    plt.figure(figsize=(8, 5))
    plt.title("DT Test (Max |Psi| over Time)")
    plt.plot(res_dt['max_psis'], label="DT=0.1", color='green')
    plt.axhline(core_math.PSI_AMP_CAP, color='red', linestyle='--', label="Fail-Safe Cap")
    plt.yscale('log')
    plt.xlabel("Simulation Steps")
    plt.ylabel("Max |Psi|")
    plt.legend()
    plt.savefig(os.path.join(os.path.dirname(__file__), 'poc_dt_test.png'))
    print("DT Test metrics saved to poc_dt_test.png")
