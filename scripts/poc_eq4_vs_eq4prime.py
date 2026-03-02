import numpy as np
import matplotlib.pyplot as plt
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from lineum_core import math as core_math

def _cap_complex_magnitude_legacy(complex_array, cap):
    mag = np.abs(complex_array)
    mask = mag > cap
    if np.any(mask):
        scale = np.ones_like(mag, dtype=np.float64)
        scale[mask] = cap / (mag[mask] + 1e-30)
        return complex_array * scale
    return complex_array

def diffuse_complex(grid, k, rate):
    laplacian = (np.roll(grid, 1, axis=0) + np.roll(grid, -1, axis=0) +
                 np.roll(grid, 1, axis=1) + np.roll(grid, -1, axis=1) - 4 * grid)
    return rate * laplacian * k

def diffuse_real(grid, k, rate):
    laplacian = (np.roll(grid, 1, axis=0) + np.roll(grid, -1, axis=0) +
                 np.roll(grid, 1, axis=1) + np.roll(grid, -1, axis=1) - 4 * grid)
    return rate * laplacian * k

def evolve_eq4_legacy(psi, delta, phi, kappa):
    """
    Original Eq-4 with HARD CLIPS, NO SOFT BRAKES.
    Runs with the same DT=0.1 to perfectly isolate the model difference.
    NO NOISE as per audit constraints.
    """
    size = psi.shape[0]
    
    delta_clamped = np.clip(delta, 0.0, 1.0)
    linon_effect = delta_clamped * core_math.sigmoid(kappa, k=0.1)
    linon_complex = linon_effect * np.exp(1j * np.angle(psi))
    
    fluctuation = np.zeros_like(psi) # No noise
    
    phi_int = np.clip(phi, 0.0, float(core_math.PHI_INTERACTION_CAP))
    
    # HARD CLIP INTERACTION
    interaction_factor = np.clip(0.04 * phi_int * kappa, -0.1, 0.1)
    interaction_term = interaction_factor * psi
    int_mag = np.abs(interaction_term)
    int_mask = int_mag > 10.0
    if np.any(int_mask):
        interaction_term[int_mask] *= 10.0 / int_mag[int_mask]
        
    # HARD CLIP PHI FLOW
    grad_phi_y, grad_phi_x = np.gradient(phi)
    phi_flow_term = core_math.DRIFT_STRENGTH * (grad_phi_x + 1j * grad_phi_y) * kappa
    flow_mag = np.abs(phi_flow_term)
    flow_mask = flow_mag > 10.0
    if np.any(flow_mask):
        phi_flow_term[flow_mask] *= 10.0 / flow_mag[flow_mask]
        
    psi_next = psi.copy()
    psi_next += phi_flow_term * core_math.DT
    psi_next = _cap_complex_magnitude_legacy(psi_next, core_math.PSI_AMP_CAP)
    
    psi_next += ((linon_complex + fluctuation) * kappa + interaction_term) * core_math.DT
    psi_next -= core_math.DISSIPATION_RATE * psi_next * core_math.DT
    psi_next += diffuse_complex(psi_next, kappa, rate=core_math.PSI_DIFFUSION) * kappa * core_math.DT
    
    amp2 = np.clip(np.abs(psi_next).astype(np.float64, copy=False), 0.0, 100.0)
    amp2 = amp2**2
    local_input = np.clip(amp2 * amp2, 0.0, 1e4)
    reaction = 0.5 * kappa
    
    phi_next = phi.copy()
    phi_next += kappa * reaction * (local_input - phi_next)
    phi_next += kappa * core_math.PHI_DIFFUSION * diffuse_real(phi_next, kappa, rate=1.0)
    phi_next = np.clip(phi_next, 0.0, float(core_math.PHI_CAP))
    
    return psi_next, phi_next

def run_empirical_comparison(steps=2000):
    print(f"--- EMPIRICAL COMPARISON: Eq-4 vs Eq-4' (Steps: {steps}, DT=0.1, Noise=OFF) ---")
    
    core_math.DT = 0.1
    core_math.ENABLE_NOISE = False # Turn off noise for Eq-4'
    core_math.ENABLE_PYTORCH_IF_AVAILABLE = False # Force Numpy for parity
    
    seed_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'entities', 'lina_seed.npz')
    data = np.load(seed_path)
    
    # Initialize Eq-4 (Legacy) arrays
    psi_legacy = np.zeros_like(data['psi'])
    phi_legacy = data['phi'].copy()
    kappa_legacy = data['kappa'].copy()
    delta = data['delta'].copy()
    
    # Initialize Eq-4' (Current) arrays
    psi_prime = np.zeros_like(data['psi'])
    phi_prime = data['phi'].copy()
    kappa_prime = data['kappa'].copy()
    
    # Add a slight pulse to delta to kickstart the system (since Noise is OFF)
    # The grid is flat zero otherwise.
    delta[40:60, 40:60] = 1.0 
    # Just single pulse then drop delta
    
    metrics = {
        'mae_psi': [], 'mae_phi': [], 'mae_kappa': [],
        'egy_legacy': [], 'egy_prime': [],
        'laplace_diff': []
    }
    
    os.makedirs('snapshots', exist_ok=True)
    
    for step in range(steps):
        # Pulse dissipates naturally
        if step > 50:
            delta.fill(0.0)
            
        psi_legacy, phi_legacy = evolve_eq4_legacy(psi_legacy, delta, phi_legacy, kappa_legacy)
        psi_prime, phi_prime = core_math.evolve(psi_prime, delta, phi_prime, kappa_prime)
        
        # Calculate MAE
        metrics['mae_psi'].append(np.mean(np.abs(psi_legacy - psi_prime)))
        metrics['mae_phi'].append(np.mean(np.abs(phi_legacy - phi_prime)))
        metrics['mae_kappa'].append(np.mean(np.abs(kappa_legacy - kappa_prime)))
        
        # Energy
        metrics['egy_legacy'].append(np.sum(np.abs(psi_legacy)**2))
        metrics['egy_prime'].append(np.sum(np.abs(psi_prime)**2))
        
        # Structural Differences (Laplacian absolute sum difference)
        laplace_legacy = np.sum(np.abs(diffuse_complex(psi_legacy, np.ones_like(psi_legacy), 1.0)))
        laplace_prime = np.sum(np.abs(diffuse_complex(psi_prime, np.ones_like(psi_prime), 1.0)))
        metrics['laplace_diff'].append(np.abs(laplace_legacy - laplace_prime))
        
        if step in [0, 100, 500, 1000, 2000, 4999]:
            np.savez_compressed(f'snapshots/snap_{step}.npz', 
                                psi_eq4=psi_legacy, phi_eq4=phi_legacy, kappa_eq4=kappa_legacy,
                                psi_eq4prime=psi_prime, phi_eq4prime=phi_prime, kappa_eq4prime=kappa_prime)
            print(f"  Saved snapshot at step {step}")
            
    # --- PLOTS ---
    plt.figure(figsize=(15, 10))
    
    plt.subplot(2, 2, 1)
    plt.title("Mean Absolute Error (Eq-4 vs Eq-4')")
    plt.plot(metrics['mae_psi'], label='MAE Psi')
    plt.plot(metrics['mae_phi'], label='MAE Phi')
    plt.plot(metrics['mae_kappa'], label='MAE Kappa', linestyle='--')
    plt.yscale('log')
    plt.legend()
    
    plt.subplot(2, 2, 2)
    plt.title("Energy Trajectory: sum(|Psi|^2)")
    plt.plot(metrics['egy_legacy'], label='Eq-4 (Hard Clips)', color='red')
    plt.plot(metrics['egy_prime'], label="Eq-4' (Soft Brakes)", color='blue')
    plt.yscale('log')
    plt.legend()
    
    plt.subplot(2, 2, 3)
    plt.title("Structural Difference (Laplacian |Psi| Sum Diff)")
    plt.plot(metrics['laplace_diff'], color='purple')
    plt.yscale('log')
    
    plt.tight_layout()
    plt.savefig('poc_eq4_empirical_compare.png')
    print("Plots saved to poc_eq4_empirical_compare.png")

if __name__ == "__main__":
    run_empirical_comparison(steps=2000)
