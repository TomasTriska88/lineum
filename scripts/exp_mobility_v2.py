import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from tqdm import tqdm
import multiprocessing
import unittest.mock

# Disable PyTorch CUDA entirely for this script before math.py gets imported
sys.modules['torch'] = unittest.mock.MagicMock()
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from lineum_core import math as core_math

# Hard override the PyTorch flag in math module
core_math.USE_PYTORCH = False

# --- Configure core params ---
core_math.TEST_EXHALE_MODE = False
core_math.NOISE_STRENGTH = 0.0
core_math.PHI_INTERACTION_CAP = 100.0
core_math.PSI_AMP_CAP = 10.0
core_math.DRIFT_STRENGTH = 0.01
core_math.DISSIPATION_RATE = 0.05
core_math.PSI_DIFFUSION = 0.15
core_math.REACTION_STRENGTH = 0.1
core_math.PHI_DIFFUSION = 0.01

def sliding_windows_1d(x, W, hop):
    x = np.asarray(x, dtype=float)
    n = len(x)
    if n < W: return []
    return [x[i:i+W] for i in range(0, n - W + 1, hop)]

def bootstrap_mean_ci(vals, B=1000, alpha=0.05, rng=np.random):
    vals = np.asarray(vals, dtype=float)
    if vals.size == 0: return (float('nan'), (float('nan'), float('nan')))
    n = vals.size
    means = np.empty(B, dtype=float)
    for b in range(B):
        idx = rng.randint(0, n, size=n)
        means[b] = np.mean(vals[idx])
    
    valid_means = means[np.isfinite(means)]
    if valid_means.size == 0: return (float('nan'), (float('nan'), float('nan')))
    try:
        lo = float(np.quantile(valid_means, alpha/2))
        hi = float(np.quantile(valid_means, 1 - alpha/2))
    except Exception:
        lo, hi = float('nan'), float('nan')
    return (float(np.nanmean(vals)), (lo, hi))

def window_sbr_and_f0(amplitudes, dt=1.0, W=128, hop=64, guard=2):
    amps = np.asarray(amplitudes, dtype=float)
    sbr_vals, f0_vals = [], []
    SR = 1.0 / dt
    DF = SR / W
    
    for w in sliding_windows_1d(amps, W=W, hop=hop):
        w = w - np.mean(w)
        wh = w * np.hanning(len(w))
        Ffull = np.fft.rfft(wh)
        P = np.abs(Ffull).astype(np.float64, copy=False)**2
        P = np.where(np.isfinite(P), P, 0.0)
        Pp = P
        if Pp.size == 0: continue

        idx0 = int(np.argmax(Pp))
        pmax = float(Pp[idx0])
        
        mask = np.ones_like(Pp, dtype=bool)
        l = max(idx0 - guard, 0)
        r = min(idx0 + guard + 1, Pp.size)
        mask[l:r] = False
        bg = float(np.mean(Pp[mask])) if np.any(mask) else np.nan
        if bg > 0: sbr_vals.append(pmax / bg)

        if 0 < idx0 < Pp.size - 1:
            p_prev = float(Pp[idx0 - 1])
            p_curr = float(Pp[idx0])
            p_next = float(Pp[idx0 + 1])
            denom = 2 * p_curr - p_prev - p_next
            if abs(denom) > 1e-12 * p_curr:
                offset = 0.5 * (p_prev - p_next) / denom
                best_idx = idx0 + offset
            else: best_idx = float(idx0)
        else: best_idx = float(idx0)
            
        f0_vals.append(best_idx * DF)

    sbr_mean, _ = bootstrap_mean_ci(sbr_vals) if sbr_vals else (float('nan'), None)
    f0_mean, _ = bootstrap_mean_ci(f0_vals) if f0_vals else (float('nan'), None)
    return sbr_mean, f0_mean

def gini_coefficient(x):
    x = np.asarray(x).flatten()
    if np.amin(x) < 0: x -= np.amin(x) 
    x = np.sort(x)
    n = x.shape[0]
    return ((np.sum((2 * np.arange(1, n + 1) - n - 1) * x)) / (n * np.sum(x))) if np.sum(x) > 0 else 0

def get_vortices(psi):
    phase = np.angle(psi)
    d_x = np.angle(np.exp(1j * (np.roll(phase, -1, axis=1) - phase)))
    d_y = np.angle(np.exp(1j * (np.roll(phase, -1, axis=0) - phase)))
    curl = d_x - np.roll(d_x, -1, axis=0) - d_y + np.roll(d_y, -1, axis=1)
    return int(np.sum(np.abs(curl) > np.pi))

def custom_evolve_with_mu(psi, delta, phi, kappa, mu, variant):
    size = psi.shape[0]
    psi = core_math._finite_complex(psi, nan=0.0)
    phi = core_math._finite_clip(phi, lo=0.0, hi=core_math.PHI_CAP, nan=0.0, posinf=core_math.PHI_CAP, neginf=0.0, dtype=np.float64)
    amp = core_math._finite_clip(np.abs(psi).astype(np.float64, copy=False), lo=0.0, hi=core_math.PSI_AMP_CAP, nan=0.0, posinf=core_math.PSI_AMP_CAP, neginf=0.0)
    
    grad_x, grad_y = np.gradient((amp + delta).astype(np.float64, copy=False))
    grad_x = core_math._finite_clip(grad_x, lo=-core_math.GRAD_CAP, hi=core_math.GRAD_CAP, nan=0.0, posinf=core_math.GRAD_CAP, neginf=-core_math.GRAD_CAP)
    grad_y = core_math._finite_clip(grad_y, lo=-core_math.GRAD_CAP, hi=core_math.GRAD_CAP, nan=0.0, posinf=core_math.GRAD_CAP, neginf=-core_math.GRAD_CAP)
    grad_mag = np.sqrt(np.clip(grad_x*grad_x + grad_y*grad_y, 0.0, 1e12))
    
    probability = core_math.sigmoid(amp + grad_mag) * kappa
    random_field = np.random.rand(size, size)
    linons = (random_field < probability).astype(float)
    linon_base, linon_scaling = 0.03, 0.02
    linon_effect = (linon_base + linon_scaling * amp.clip(min=0)) * linons
    linon_complex = linon_effect * np.exp(1j * np.angle(psi))
    fluctuation = np.random.normal(0.0, core_math.NOISE_STRENGTH, (size, size)) * np.exp(1j * np.angle(psi))

    phi_int = core_math._finite_clip(phi, lo=0.0, hi=float(core_math.PHI_INTERACTION_CAP), nan=0.0, posinf=float(core_math.PHI_INTERACTION_CAP), neginf=0.0, dtype=np.float64)
    interaction_term = 0.04 * phi_int * psi * kappa
    grad_phi_x, grad_phi_y = np.gradient(phi)
    phi_flow_term = core_math.DRIFT_STRENGTH * (grad_phi_x + 1j * grad_phi_y) * kappa

    if variant in ['V1', 'V2']: phi_flow_term *= mu
    if variant in ['V2']: interaction_term *= mu
        
    psi += phi_flow_term
    psi += (linon_complex + fluctuation) * kappa + interaction_term
    psi -= core_math.DISSIPATION_RATE * psi
    psi += core_math.diffuse_complex(psi, kappa, rate=core_math.PSI_DIFFUSION) * kappa
    amp2 = core_math._finite_clip(np.abs(psi).astype(np.float64, copy=False), lo=0.0, hi=core_math.PSI_AMP_CAP, nan=0.0, posinf=core_math.PSI_AMP_CAP, neginf=0.0)
    
    phi += kappa * core_math.REACTION_STRENGTH * (np.clip(amp2 * amp2, 0.0, 1e4) - phi)
    phi += kappa * core_math.PHI_DIFFUSION * core_math.diffuse_real(phi, kappa, rate=0.05)
    psi = core_math._cap_complex_magnitude(core_math._finite_complex(psi, nan=0.0), core_math.PSI_AMP_CAP)
    return psi, phi

def calc_concentration(cell_occupancy):
    occ_flat = cell_occupancy.flatten()
    total_occ = np.sum(occ_flat)
    if total_occ <= 0: return 0, 0, 0, 0
    occ_sorted = np.sort(occ_flat)[::-1]
    t20 = np.sum(occ_sorted[:int(0.20 * len(occ_sorted))]) / total_occ
    t10 = np.sum(occ_sorted[:int(0.10 * len(occ_sorted))]) / total_occ
    t1 = np.sum(occ_sorted[:int(0.01 * len(occ_sorted))]) / total_occ
    return t20, t10, t1, gini_coefficient(occ_flat)

def run_scenario(scenario_def):
    scen_name, seed, variant, dynamic_obstacle, reset_mu_local = scenario_def
    size = 128
    steps = 450
    np.random.seed(seed)
    
    psi = np.zeros((size, size), dtype=np.complex128)
    delta = np.zeros((size, size), dtype=np.float64)
    phi = np.zeros((size, size), dtype=np.float64)
    
    target_y, target_x = int(size*0.8), int(size*0.8)
    delta[target_y-2:target_y+3, target_x-2:target_x+3] = 50.0 
    
    # Complex Environment: Giant wall passing through the middle with one existing gap, and one potential gap.
    kappa_0 = np.ones((size, size), dtype=np.float64)
    kappa_0[size//2 - 5 : size//2 + 5, :] = 0.05 # Wall
    kappa_0[size//2 - 5 : size//2 + 5, 20:30] = 1.0 # Gap A (Open)
    kappa_0[size//2 - 5 : size//2 + 5, 90:100] = 0.05 # Gap B (Closed initially)
    
    # A few random obstacles
    for _ in range(20):
        oy, ox = np.random.randint(10, size-10, size=2)
        r = np.random.randint(2, 6)
        Y, X = np.ogrid[:size, :size]
        kappa_0[np.sqrt((Y - oy)**2 + (X - ox)**2) <= r] = 0.05
        
    kappa = kappa_0.copy()
    
    mu_0_val, eta, rho = 0.1, 0.02, 0.001
    mu_min, mu_max = 0.05, 1.0
    mu = np.full((size, size), mu_0_val, dtype=np.float64)
    
    sy, sx = int(size*0.2), int(size*0.2)
    cell_occupancy = np.zeros((size, size), dtype=np.float64)
    metrics_ts = []
    psi_center_history = []
    vortices_history = []
    
    freeze_mu = False

    for step in range(steps):
        # --- DYNAMIC EVENTS ---
        if scen_name == "HDD_Test" and step == 200:
            freeze_mu = True
            phi.fill(0.0) # Reset short term memory
            cell_occupancy.fill(0.0) # Reset tracking to see new allocation
            
        if scen_name == "Dynamic_Obstacle" and step == 200:
            # Open Gap B (which is much closer to target)
            kappa[size//2 - 5 : size//2 + 5, 90:100] = 1.0
            if reset_mu_local:
                mu[size//2 - 15 : size//2 + 15, :] = mu_0_val # Reset mu around the wall to forget old paths
        
        # --- EVOLVE ---
        dist_s = np.sqrt((np.arange(size)[:,None] - sy)**2 + (np.arange(size)[None,:] - sx)**2)
        psi[dist_s <= 3] = 10.0
        
        if variant == 'Baseline':
            psi, phi = core_math.evolve(psi, delta, phi, kappa)
        else:
            psi, phi = custom_evolve_with_mu(psi, delta, phi, kappa, mu, variant)
        psi *= (kappa > 0.05)
        
        if scen_name == "Core_Metrics":
            c_y, c_x = size // 2, size // 2
            psi_center_history.append(float(np.mean(np.abs(psi[c_y-1:c_y+2, c_x-1:c_x+2]))))
            vortices_history.append(get_vortices(psi))
        
        J_t = np.clip(np.abs(psi)**2, 0, 10.0) 
        cell_occupancy += J_t
        
        # --- MU UPDATE ---
        if not freeze_mu and variant != 'Baseline':
            mu = np.clip(mu + eta * J_t + rho * (np.full((size, size), mu_0_val) - mu), mu_min, mu_max)

        # --- METRICS ---
        if (step+1) % 10 == 0:
            t20, t10, t1, gini = calc_concentration(cell_occupancy)
            metrics_ts.append({
                'scenario': scen_name, 'variant': variant, 'step': step+1, 'seed': seed,
                'top20': t20, 'gini': gini
            })

    # Strict Pearson correlation (only on non-obstacle cells)
    valid_mask = (kappa > 0.1).flatten()
    mu_flat = mu.flatten()
    phi_flat = phi.flatten()
    
    if np.std(mu_flat[valid_mask]) > 0 and np.std(phi_flat[valid_mask]) > 0:
        pearson_r = np.corrcoef(mu_flat[valid_mask], phi_flat[valid_mask])[0, 1]
    else:
        pearson_r = 0.0
        
    # Jaccard Overlap
    overlaps = {}
    for k in [0.01, 0.05, 0.10]:
        k_cnt = int(k * np.sum(valid_mask))
        if k_cnt > 0:
            m_idx = set(np.argsort(mu_flat[valid_mask])[-k_cnt:])
            p_idx = set(np.argsort(phi_flat[valid_mask])[-k_cnt:])
            intersection = len(m_idx.intersection(p_idx))
            union = len(m_idx.union(p_idx))
            overlaps[f'jaccard_{int(k*100)}'] = intersection / union if union > 0 else 0
        else:
            overlaps[f'jaccard_{int(k*100)}'] = 0

    res = {
        'scenario': scen_name, 'seed': seed, 'variant': variant, 
        'dynamic_obstacle': dynamic_obstacle, 'reset_mu_local': reset_mu_local,
        'final_pearson_r': pearson_r
    }
    res.update(overlaps)
    
    # Core valid
    c_y, c_x = size//2, size//2
    # If Core Metrics scenario, calculate deep metrics
    if scen_name == "Core_Metrics":
        sbr_mean, f0_mean = window_sbr_and_f0(psi_center_history, dt=1.0, W=128, hop=64)
        vortices_mean = float(np.mean(vortices_history))
        res['sbr_mean'] = sbr_mean
        res['f0_mean_hz'] = f0_mean
        res['vortices_mean'] = vortices_mean
    
    return res, metrics_ts, mu, phi

def main():
    seeds = [42, 101, 777]
    tasks = []
    
    # 1. HDD Test
    for s in seeds:
        tasks.append(("HDD_Test", s, 'V2', False, False))
        
    # 2. Dynamic Obstacle Test (Ghost Highways)
    for s in seeds:
        tasks.append(("Dynamic_Obstacle", s, 'V2', True, False)) # Let it relax naturally
        tasks.append(("Dynamic_Obstacle", s, 'V2', True, True))  # Local reset of Mu
        tasks.append(("Dynamic_Obstacle", s, 'Baseline', True, False))
        
    # 3. Core Safety
    for s in seeds:
         tasks.append(("Core_Metrics", s, 'Baseline', False, False))
         tasks.append(("Core_Metrics", s, 'V1', False, False))
         tasks.append(("Core_Metrics", s, 'V2', False, False))

    print(f"Running {len(tasks)} scenarios...")
    pool = multiprocessing.Pool(processes=min(multiprocessing.cpu_count(), len(tasks)))
    results = list(tqdm(pool.imap(run_scenario, tasks), total=len(tasks)))
    pool.close(); pool.join()
    
    summary_data, all_ts = [], []
    for res, ts, mu, phi in results:
        summary_data.append(res)
        all_ts.extend(ts)
        
        # Save viz for first seed of HDD and Dynamic Obstacle
        if res['seed'] == 42:
            out_dir = os.path.join(os.path.dirname(__file__), "..", "output_mobility_v2")
            os.makedirs(out_dir, exist_ok=True)
            plt.figure(figsize=(10, 4))
            plt.subplot(1, 2, 1); plt.title(f"{res['scenario']} Mu"); plt.imshow(mu, cmap='hot')
            plt.subplot(1, 2, 2); plt.title(f"{res['scenario']} Phi"); plt.imshow(phi, cmap='viridis')
            safe_name = f"{res['scenario']}_{res['variant']}_reset{res['reset_mu_local']}".replace(" ", "_")
            plt.savefig(os.path.join(out_dir, f"map_{safe_name}.png"))
            plt.close()
            
    df_ts = pd.DataFrame(all_ts)
    df_sum = pd.DataFrame(summary_data)
    
    out_dir = os.path.join(os.path.dirname(__file__), "..", "output_mobility_v2")
    os.makedirs(out_dir, exist_ok=True)
    df_ts.to_csv(os.path.join(out_dir, "scenario_timeseries.csv"), index=False)
    
    df_grouped = df_sum.groupby(['scenario', 'variant', 'reset_mu_local']).mean(numeric_only=True).reset_index()
    df_grouped.to_csv(os.path.join(out_dir, "scenario_summary.csv"), index=False)
    
    print("\n--- Summary of Scenarios ---")
    print(df_grouped.to_string(index=False))
    
if __name__ == '__main__':
    main()
