import numpy as np
import scipy.ndimage
import json
import os

# --- Constants & Context ---
GRID_SIZE = 64
TICKS_PER_CHUNK = 200
PSI_AMP_CAP = 1e6 # CFL Limit (Must stay)
GRAD_CAP = 1e6    # CFL Limit (Must stay)
PHI_CAP = 1e6     # Global structural limit
NOISE_STRENGTH = 0.005
DT = 1.0

# --- Seed Generation ---
def generate_terrain(seed):
    np.random.seed(seed)
    kappa = np.random.rand(GRID_SIZE, GRID_SIZE) * 0.5 + 0.1
    kappa = scipy.ndimage.gaussian_filter(kappa, sigma=2.0)
    return kappa

# --- Math Core Helpers ---
def sigmoid(x, k=5):
    return 1 / (1 + np.exp(-k * (x - 0.0)))

def diffuse_complex(field, kappa, rate=0.05):
    k_up = np.roll(kappa, 1, axis=0)
    k_dn = np.roll(kappa, -1, axis=0)
    k_lf = np.roll(kappa, 1, axis=1)
    k_rt = np.roll(kappa, -1, axis=1)
    sum_neighbors = (np.roll(field, 1, axis=0) * k_up + np.roll(field, -1, axis=0) * k_dn +
                     np.roll(field, 1, axis=1) * k_lf + np.roll(field, -1, axis=1) * k_rt)
    active_neighbors = k_up + k_dn + k_lf + k_rt
    return rate * (sum_neighbors - active_neighbors * field)

# --- Engine Simulator ---
def run_simulation(kappa, mode_coupling=False, work_transfer_strength=0.000, 
                   use_mu=False, ticks=500, initial_psi=None):
    
    size = kappa.shape[0]
    psi = np.zeros((size, size), dtype=np.complex128) if initial_psi is None else initial_psi.copy()
    phi = np.zeros((size, size), dtype=np.float64)
    mu = np.full((size, size), 0.1, dtype=np.float64) if use_mu else None
    
    novelties = []
    psi_energies = []
    max_psis = []
    exploded = False
    frozen = False
    
    # Pre-calculated structural values
    scale_ratio = (128.0 / size) ** 2
    dynamic_reaction = 0.00070 * scale_ratio
    linon_base = 0.03
    linon_scaling = 0.02
    
    for t in range(ticks):
        # CFL: Absolute float safety
        psi = np.nan_to_num(psi, nan=0.0)
        amp = np.clip(np.abs(psi), 0.0, PSI_AMP_CAP) # (A) CFL Limit - MUST STAY
        
        # Source injection (Semantic Stimulus)
        if t % 50 == 0:
            psi[size//2-2:size//2+3, size//2-2:size//2+3] += 5.0
            amp = np.clip(np.abs(psi), 0.0, PSI_AMP_CAP)

        # Gradients (CFL Protected)
        grad_x, grad_y = np.gradient(amp)
        grad_x = np.clip(grad_x, -GRAD_CAP, GRAD_CAP) # (A) CFL Limit - MUST STAY
        grad_y = np.clip(grad_y, -GRAD_CAP, GRAD_CAP)
        grad_mag = np.sqrt(np.clip(grad_x*grad_x + grad_y*grad_y, 0.0, 1e12))
        
        # Linon Generation
        probability = sigmoid(amp + grad_mag) * kappa
        linons = (np.random.rand(size, size) < probability).astype(float)
        
        if mode_coupling:
            # (P) Variant P: Smooth saturation instead of hard clip
            raw_linon = linon_base + linon_scaling * amp
            linon_effect = 10.0 * (raw_linon / (10.0 + np.abs(raw_linon))) * linons
        else:
            # (B) Heuristic Hack: Hard clip
            linon_effect = np.clip((linon_base + linon_scaling * amp) * linons, 0.0, 10.0)
            
        linon_complex = linon_effect * np.exp(1j * np.angle(psi))
        
        # Interaction / Drift
        phi_eff = phi if not use_mu else phi * (1.0 + mu)
        phi_int = np.clip(phi_eff, 0.0, 10.0)
        interaction_factor = 0.1 * np.tanh((0.04 * phi_int * kappa) / 0.1)
        interaction_term = interaction_factor * psi
        int_mag = np.abs(interaction_term)
        interaction_term = interaction_term / (1.0 + int_mag / 10.0)
        
        grad_phi_x, grad_phi_y = np.gradient(phi_eff)
        phi_flow_term = -0.004 * (grad_phi_x + 1j * grad_phi_y) * kappa
        flow_mag = np.abs(phi_flow_term)
        phi_flow_term = phi_flow_term / (1.0 + flow_mag / 10.0)
        
        # Apply terms
        psi += phi_flow_term * DT
        psi += ((linon_complex) * kappa + interaction_term) * DT
        psi -= 0.005 * psi * DT # Dissipation
        psi += diffuse_complex(psi, kappa, rate=0.05) * kappa * DT
        
        # --- THE CORE DIFFERENCE: PHI TENSION & ENERGY SATURATION ---
        if mode_coupling:
            # (M) Mode-Coupling: Conservation of Energy (Phi gets delta_E, Psi loses delta_E)
            e_psi = np.abs(psi)**2
            
            # Transfer quantum
            delta_e = work_transfer_strength * e_psi * kappa * DT
            
            phi += delta_e
            phi += kappa * 0.05 * np.real(diffuse_complex(phi, kappa, rate=0.05))
            
            # Psi pays the tax
            psi_mag_new = np.sqrt(np.maximum(e_psi - delta_e, 0.0))
            psi = (psi / (np.sqrt(e_psi) + 1e-12)) * psi_mag_new
            
        else:
            # (B) Heuristic: Hard clips, no energy lost from Psi
            amp2 = np.clip(np.abs(psi)**2, 0.0, 10000.0) # The hack
            local_input = amp2
            phi += kappa * dynamic_reaction * (local_input - phi)
            phi += kappa * 0.05 * np.real(diffuse_complex(phi, kappa, rate=0.05))
            
        phi = np.clip(phi, 0.0, PHI_CAP)
        psi = np.clip(np.nan_to_num(psi), -PSI_AMP_CAP, PSI_AMP_CAP) # Final CFL guard
        
        if use_mu:
            psi_mag_sq = np.abs(psi)**2
            mu += (0.005 * psi_mag_sq - 0.0001 * (mu - 0.1)) * DT
            mu = np.clip(mu, 0.001, 10.0)

        # Logging
        if t > 0 and t % 10 == 0:
            new_phi_mag = np.sum(np.abs(phi))
            novelty = np.abs(new_phi_mag - prev_phi_mag) / (prev_phi_mag + 1e-5)
            novelties.append(float(novelty))
        if t % 10 == 0:
            prev_phi_mag = np.sum(np.abs(phi))
            
        psi_energies.append(float(np.sum(np.abs(psi)**2)))
        max_psis.append(float(np.max(np.abs(psi))))
        
        if np.isnan(np.sum(psi)) or np.max(np.abs(psi)) >= PSI_AMP_CAP * 0.99:
            exploded = True
            break
            
    if not exploded and len(novelties) > 10:
        tail_novelty = np.mean(novelties[-10:])
        if tail_novelty < 1e-5:
            frozen = True
            
    return {
        "exploded": exploded,
        "frozen": frozen,
        "max_psi": np.max(max_psis) if len(max_psis) > 0 else 0,
        "mean_energy": np.mean(psi_energies) if len(psi_energies) > 0 else 0,
        "tail_novelty": float(np.mean(novelties[-10:])) if len(novelties) > 10 else 0.0,
        "final_phi": phi.copy()
    }

# ==========================================
# 1. PARAMETER SWEEP (WORK TRANSFER STRENGTH)
# ==========================================
print("Running Work Transfer Sweep...")
kappa_test = generate_terrain(42)
strengths = [1e-5, 1e-4, 5e-4, 1e-3, 5e-3, 1e-2, 5e-2]
sweep_results = {}

for s in strengths:
    res = run_simulation(kappa_test, mode_coupling=True, work_transfer_strength=s, ticks=400)
    sweep_results[s] = res
    status = "EXPLODED" if res['exploded'] else ("FROZEN" if res['frozen'] else "STABLE")
    print(f"Strength {s:.5f}: {status} | MaxPsi: {res['max_psi']:.2f} | Energy: {res['mean_energy']:.2f} | Novelty: {res['tail_novelty']:.5f}")

# Find best stable parameter
stable_strengths = [s for s in strengths if not sweep_results[s]['exploded'] and not sweep_results[s]['frozen']]
if stable_strengths:
    best_strength = stable_strengths[len(stable_strengths)//2] # Pick a middle ground
else:
    best_strength = 0.001
print(f"\\nSelected optimal safe Mode-Coupling Strength: {best_strength}\\n")

# ==========================================
# 2. THE ABLATION (Baseline vs Coupling vs Mu)
# ==========================================
print("Running Ablation Tests...")
metrics = {}

# A. Baseline
res_base = run_simulation(kappa_test, mode_coupling=False, ticks=500)
metrics['baseline'] = {
    'exploded': res_base['exploded'], 'frozen': res_base['frozen'],
    'max_psi': res_base['max_psi'], 'mean_energy': res_base['mean_energy'], 'novelty': res_base['tail_novelty']
}

# B. Physics Coupling (No hack)
res_phys = run_simulation(kappa_test, mode_coupling=True, work_transfer_strength=best_strength, ticks=500)
metrics['physics_only'] = {
    'exploded': res_phys['exploded'], 'frozen': res_phys['frozen'],
    'max_psi': res_phys['max_psi'], 'mean_energy': res_phys['mean_energy'], 'novelty': res_phys['tail_novelty']
}

# C. Physics + Mu (HDD)
res_mu = run_simulation(kappa_test, mode_coupling=True, work_transfer_strength=best_strength, use_mu=True, ticks=500)
metrics['physics_mu'] = {
    'exploded': res_mu['exploded'], 'frozen': res_mu['frozen'],
    'max_psi': res_mu['max_psi'], 'mean_energy': res_mu['mean_energy'], 'novelty': res_mu['tail_novelty']
}

for name, dat in metrics.items():
    print(f"[{name.upper()}] Status: {('EXPLODED' if dat['exploded'] else ('FROZEN' if dat['frozen'] else 'STABLE'))} | Energy: {dat['mean_energy']:.2f} | Novelty: {dat['novelty']:.5f}")

with open("output_audit_saturation.json", "w") as f:
    # Cannot serialize numpy arrays in standard json dump easily without filtering
    clean_metrics = {"sweep": {}, "ablation": metrics, "best_strength": best_strength}
    for k, v in sweep_results.items():
        clean_metrics["sweep"][str(k)] = {
            "exploded": v["exploded"], "frozen": v["frozen"], 
            "max_psi": v["max_psi"], "mean_energy": v["mean_energy"], "novelty": v["tail_novelty"]
        }
    json.dump(clean_metrics, f, indent=2)

print("\\nSaturation Audit Complete.")
