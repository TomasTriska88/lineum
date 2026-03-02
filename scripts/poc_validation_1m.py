import numpy as np
import matplotlib.pyplot as plt
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from lineum_core import math as core_math

def run_validation(steps: int = 100000, dt: float = 0.1, check_regime: bool = True):
    print(f"\n--- Running Validation: DT={dt}, Steps={steps} ---")
    core_math.DT = dt
    
    seed_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'entities', 'lina_seed.npz')
    data = np.load(seed_path)
    
    psi = np.zeros_like(data['psi'])
    phi = data['phi'].copy()
    kappa_seed = data['kappa'].copy()
    kappa = data['kappa'].copy()
    delta = data['delta'].copy()
    
    # Metrics
    max_psis = []
    min_psis = []
    mean_psis = []
    total_energies = []
    
    failsafe_triggers = 0
    exploded = False
    
    print(f"Initial: Max Kappa = {np.max(kappa):.4f}, Mean Kappa = {np.mean(kappa):.4f}")
    
    for step in range(steps):
        psi, phi = core_math.evolve(psi, delta, phi, kappa)
        
        mag = np.abs(psi)
        current_max = np.max(mag)
        
        if current_max == 0.0 and step > 0:
            failsafe_triggers += 1
            if failsafe_triggers > 100: # Abort if it's just chain-failing
                exploded = True
                break
        
        if step % 100 == 0 or step == steps - 1:
            max_psis.append(current_max)
            total_energies.append(np.sum(mag**2))
            if check_regime:
                min_psis.append(np.min(mag))
                mean_psis.append(np.mean(mag))
                
        if step % 10000 == 0 and step > 0:
            print(f"  Step {step}/{steps} | Max Psi: {current_max:.2f} | Failsafes: {failsafe_triggers}")
            
    print(f"Final: Max Kappa = {np.max(kappa):.4f}, Mean Kappa = {np.mean(kappa):.4f}")
    mae_kappa = np.mean(np.abs(kappa - kappa_seed))
    print(f"Kappa Drift (MAE to Seed): {mae_kappa:.6f}")
    print(f"Total Failsafe Triggers: {failsafe_triggers}")
    
    return {
        'dt': dt,
        'exploded': exploded,
        'max_psis': max_psis,
        'min_psis': min_psis if check_regime else None,
        'mean_psis': mean_psis if check_regime else None,
        'total_energies': total_energies,
        'mae_kappa': mae_kappa,
        'failsafe_triggers': failsafe_triggers
    }

if __name__ == "__main__":
    # --- POINT 4: DT Safety Margin ---
    print("\n>>> CHECKING DT SAFETY MARGINS (10k steps) <<<")
    res_dt_05 = run_validation(steps=10000, dt=0.05, check_regime=False)
    res_dt_10 = run_validation(steps=10000, dt=0.10, check_regime=False)
    res_dt_20 = run_validation(steps=10000, dt=0.20, check_regime=False)
    
    plt.figure(figsize=(10, 5))
    plt.title("DT Safety Margin (Max |Psi| over 10k steps)")
    plt.plot(res_dt_05['max_psis'], label="DT=0.05")
    plt.plot(res_dt_10['max_psis'], label="DT=0.10")
    plt.plot(res_dt_20['max_psis'], label="DT=0.20")
    plt.yscale('log')
    plt.legend()
    plt.savefig(os.path.join(os.path.dirname(__file__), 'poc_dt_margin.png'))
    print("Saved DT margin plot.")
    
    # --- POINT 1, 2, 3, 5: Long-term 100k Run ---
    print("\n>>> RUNNING 100k LONG-TERM VALIDATION (DT=0.1) <<<")
    res_100k = run_validation(steps=100000, dt=0.1, check_regime=True)
    
    plt.figure(figsize=(15, 5))
    
    plt.subplot(1, 3, 1)
    plt.title("Long-term: Total Energy (Sum |Psi|^2)")
    plt.plot(res_100k['total_energies'], color='red')
    plt.yscale('log')
    
    plt.subplot(1, 3, 2)
    plt.title("Regime Stability (|Psi| Min/Mean/Max)")
    plt.plot(res_100k['max_psis'], label='Max', color='orange')
    plt.plot(res_100k['mean_psis'], label='Mean', color='blue')
    plt.plot(res_100k['min_psis'], label='Min', color='green')
    plt.yscale('log')
    plt.legend()
    
    plt.subplot(1, 3, 3)
    # We load the data again just to plot the final kappa
    seed_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'entities', 'lina_seed.npz')
    d = np.load(seed_path)
    plt.title(f"Final Kappa (MAE Drift: {res_100k['mae_kappa']:.5f})")
    plt.imshow(d['kappa'].T, cmap='inferno', origin='lower')
    plt.colorbar()
    
    plt.tight_layout()
    plt.savefig(os.path.join(os.path.dirname(__file__), 'poc_100k_validation.png'))
    print("Saved 100k validation plots.")
    
    print("\nALL VALIDATION CHECKS COMPLETE.")
