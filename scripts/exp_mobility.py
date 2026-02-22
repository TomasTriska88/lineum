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

# --- Configure core params for isolation ---
core_math.TEST_EXHALE_MODE = False
core_math.NOISE_STRENGTH = 0.0
core_math.PHI_INTERACTION_CAP = 100.0
core_math.PSI_AMP_CAP = 10.0
core_math.DRIFT_STRENGTH = 0.01
core_math.DISSIPATION_RATE = 0.05
core_math.PSI_DIFFUSION = 0.15
core_math.REACTION_STRENGTH = 0.1
core_math.PHI_DIFFUSION = 0.01

# --- Metric Utilities ---
def sliding_windows_1d(x, W, hop):
    x = np.asarray(x, dtype=float)
    n = len(x)
    if n < W:
        return []
    return [x[i:i+W] for i in range(0, n - W + 1, hop)]

def bootstrap_mean_ci(vals, B=1000, alpha=0.05, rng=np.random):
    vals = np.asarray(vals, dtype=float)
    if vals.size == 0:
        return (float('nan'), (float('nan'), float('nan')))
    n = vals.size
    means = np.empty(B, dtype=float)
    for b in range(B):
        idx = rng.randint(0, n, size=n)
        means[b] = np.mean(vals[idx])
    
    valid_means = means[np.isfinite(means)]
    if valid_means.size == 0:
        return (float(np.nanmean(vals)) if np.any(np.isfinite(vals)) else float('nan'), (float('nan'), float('nan')))
        
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
        if Pp.size == 0:
            continue

        idx0 = int(np.argmax(Pp))
        pmax = float(Pp[idx0])
        
        mask = np.ones_like(Pp, dtype=bool)
        l = max(idx0 - guard, 0)
        r = min(idx0 + guard + 1, Pp.size)
        mask[l:r] = False
        bg = float(np.mean(Pp[mask])) if np.any(mask) else np.nan
        if bg > 0:
            sbr_vals.append(pmax / bg)

        if 0 < idx0 < Pp.size - 1:
            p_prev = float(Pp[idx0 - 1])
            p_curr = float(Pp[idx0])
            p_next = float(Pp[idx0 + 1])
            denom = 2 * p_curr - p_prev - p_next
            if abs(denom) > 1e-12 * p_curr:
                offset = 0.5 * (p_prev - p_next) / denom
                best_idx = idx0 + offset
            else:
                best_idx = float(idx0)
        else:
            best_idx = float(idx0)
            
        f0_vals.append(best_idx * DF)

    sbr_mean, _ = bootstrap_mean_ci(sbr_vals) if sbr_vals else (float('nan'), None)
    f0_mean, _ = bootstrap_mean_ci(f0_vals) if f0_vals else (float('nan'), None)
    
    return sbr_mean, f0_mean

def gini_coefficient(x):
    """Compute Gini coefficient of a numpy array."""
    x = np.asarray(x).flatten()
    if np.amin(x) < 0:
        x -= np.amin(x) 
    x = np.sort(x)
    index = np.arange(1, x.shape[0] + 1)
    n = x.shape[0]
    return ((np.sum((2 * index - n  - 1) * x)) / (n * np.sum(x))) if np.sum(x) > 0 else 0

def get_vortices(psi):
    """Count phase singularities (vortices) in psi."""
    phase = np.angle(psi)
    # Simple winding number proxy
    d_x = np.angle(np.exp(1j * (np.roll(phase, -1, axis=1) - phase)))
    d_y = np.angle(np.exp(1j * (np.roll(phase, -1, axis=0) - phase)))
    curl = d_x - np.roll(d_x, -1, axis=0) - d_y + np.roll(d_y, -1, axis=1)
    vortex_mask = np.abs(curl) > np.pi
    return int(np.sum(vortex_mask))

# --- Custom evolve logic supporting Mu field variants ---
# Re-implementing parts of _evolve_numpy to inject Mu selectively
def custom_evolve_with_mu(psi, delta, phi, kappa, mu, variant):
    size = psi.shape[0]

    psi = core_math._finite_complex(psi, nan=0.0)
    phi = core_math._finite_clip(phi, lo=0.0, hi=core_math.PHI_CAP, nan=0.0, posinf=core_math.PHI_CAP, neginf=0.0, dtype=np.float64)

    amp = np.abs(psi).astype(np.float64, copy=False)
    amp = core_math._finite_clip(amp, lo=0.0, hi=core_math.PSI_AMP_CAP, nan=0.0, posinf=core_math.PSI_AMP_CAP, neginf=0.0)

    grad_x, grad_y = np.gradient((amp + delta).astype(np.float64, copy=False))
    grad_x = core_math._finite_clip(grad_x, lo=-core_math.GRAD_CAP, hi=core_math.GRAD_CAP, nan=0.0, posinf=core_math.GRAD_CAP, neginf=-core_math.GRAD_CAP)
    grad_y = core_math._finite_clip(grad_y, lo=-core_math.GRAD_CAP, hi=core_math.GRAD_CAP, nan=0.0, posinf=core_math.GRAD_CAP, neginf=-core_math.GRAD_CAP)
    grad_mag = np.sqrt(np.clip(grad_x*grad_x + grad_y*grad_y, 0.0, 1e12))
    
    probability = core_math.sigmoid(amp + grad_mag) * kappa
    random_field = np.random.rand(size, size)
    linons = (random_field < probability).astype(float)
    linon_base = 0.01 if core_math.TEST_EXHALE_MODE else 0.03
    linon_scaling = 0.01 if core_math.TEST_EXHALE_MODE else 0.02
    linon_effect = (linon_base + linon_scaling * amp.clip(min=0)) * linons
    linon_complex = linon_effect * np.exp(1j * np.angle(psi))

    fluctuation = np.random.normal(0.0, core_math.NOISE_STRENGTH, (size, size)) * np.exp(1j * np.angle(psi))

    phi_int = core_math._finite_clip(phi, lo=0.0, hi=float(core_math.PHI_INTERACTION_CAP), nan=0.0, posinf=float(core_math.PHI_INTERACTION_CAP), neginf=0.0, dtype=np.float64)
    
    interaction_term = 0.04 * phi_int * psi * kappa
    grad_phi_x, grad_phi_y = np.gradient(phi)
    
    phi_flow_term = core_math.DRIFT_STRENGTH * (grad_phi_x + 1j * grad_phi_y) * kappa

    # --- INJECT MU VARIANT MODULATIONS ---
    if variant in ['V1', 'V2', 'V3']: # V1: Drift only
        phi_flow_term *= mu
    
    if variant in ['V2', 'V3']: # V2: Drift + Interaction
        interaction_term *= mu
        
    psi += phi_flow_term
    psi += (linon_complex + fluctuation) * kappa + interaction_term
    psi -= core_math.DISSIPATION_RATE * psi
    
    # Diffusion term
    diff_term = core_math.diffuse_complex(psi, kappa, rate=core_math.PSI_DIFFUSION) * kappa
    if variant == 'V3': # V3: Drift + Interaction + Diffusion
        diff_term *= mu
        
    psi += diff_term

    amp2 = core_math._finite_clip(np.abs(psi).astype(np.float64, copy=False), lo=0.0, hi=core_math.PSI_AMP_CAP, nan=0.0, posinf=core_math.PSI_AMP_CAP, neginf=0.0)
    local_input = np.clip(amp2 * amp2, 0.0, 1e4)

    phi += kappa * core_math.REACTION_STRENGTH * (local_input - phi)
    phi += kappa * core_math.PHI_DIFFUSION * core_math.diffuse_real(phi, kappa, rate=0.05)

    psi = core_math._finite_complex(psi, nan=0.0)
    phi = core_math._finite_clip(phi, lo=0.0, hi=core_math.PHI_CAP, nan=0.0, posinf=core_math.PHI_CAP, neginf=0.0, dtype=np.float64)
    psi = core_math._cap_complex_magnitude(psi, core_math.PSI_AMP_CAP)

    return psi, phi


def run_mobility_experiment(params):
    variant, mu_0_val, eta, rho, seed = params
    
    # Setup
    size = 128
    steps = 300
    np.random.seed(seed)
    
    psi = np.zeros((size, size), dtype=np.complex128)
    delta = np.zeros((size, size), dtype=np.float64)
    phi = np.zeros((size, size), dtype=np.float64)
    
    # Target Delta
    target_y, target_x = int(size*0.8), int(size*0.8)
    delta[target_y-2:target_y+3, target_x-2:target_x+3] = 50.0 
    
    # Obstacles
    kappa_0 = np.ones((size, size), dtype=np.float64)
    for _ in range(40):
        oy, ox = np.random.randint(10, size-10, size=2)
        r = np.random.randint(2, 6)
        Y, X = np.ogrid[:size, :size]
        dist = np.sqrt((Y - oy)**2 + (X - ox)**2)
        kappa_0[dist <= r] = 0.05
        
    kappa = kappa_0.copy()
    
    # Mobility field mu
    mu_min, mu_max = 0.05, 1.0
    mu_0 = np.full((size, size), mu_0_val, dtype=np.float64)
    mu = mu_0.copy()
    
    # Agents
    sy, sx = int(size*0.2), int(size*0.2)
    
    cell_occupancy = np.zeros((size, size), dtype=np.float64)
    metrics_timeseries = []
    psi_center_history = []
    vortices_history = []

    # Simulation Loop
    for step in range(steps):
        # Inject agents
        dist_s = np.sqrt((np.arange(size)[:,None] - sy)**2 + (np.arange(size)[None,:] - sx)**2)
        psi[dist_s <= 3] = 10.0
        
        # Evolve with custom Mu variant
        if variant == 'Baseline_Vanilla':
            # Regular Eq-4 without Mu
            psi, phi = core_math.evolve(psi, delta, phi, kappa)
        else:
            psi, phi = custom_evolve_with_mu(psi, delta, phi, kappa, mu, variant)
            
        psi *= (kappa > 0.05)
        
        # Collect core metrics
        c_y, c_x = size // 2, size // 2
        center_amp = float(np.mean(np.abs(psi[c_y-1:c_y+2, c_x-1:c_x+2])))
        psi_center_history.append(center_amp)
        vortices_history.append(get_vortices(psi))
        
        J_t = np.clip(np.abs(psi)**2, 0, 10.0) 
        cell_occupancy += J_t
        
        # Mobility dynamics (erosion towards mu_max)
        if eta > 0 or rho > 0:
            traffic_term = eta * J_t
            relaxation_term = rho * (mu_0 - mu)
            mu = np.clip(mu + traffic_term + relaxation_term, mu_min, mu_max)

        # Periodic snapshot
        if (step + 1) % 25 == 0 or step == steps - 1:
            occ_flat = cell_occupancy.flatten()
            total_occ = np.sum(occ_flat)
            if total_occ > 0:
                occ_sorted = np.sort(occ_flat)[::-1]
                top20_count = int(0.20 * len(occ_sorted))
                top10_count = int(0.10 * len(occ_sorted))
                top1_count = int(0.01 * len(occ_sorted))
                
                top20_share = np.sum(occ_sorted[:top20_count]) / total_occ
                top10_share = np.sum(occ_sorted[:top10_count]) / total_occ
                top1_share = np.sum(occ_sorted[:top1_count]) / total_occ
                gini = gini_coefficient(occ_flat)
            else:
                top20_share, top10_share, top1_share, gini = 0, 0, 0, 0
            
            metrics_timeseries.append({
                'variant': variant, 'mu_base': mu_0_val, 'eta': eta, 'rho': rho, 'seed': seed, 'step': step + 1,
                'top20_share': top20_share, 'top10_share': top10_share, 
                'top1_share': top1_share, 'gini': gini
            })

    # Evaluators post-run
    sbr_mean, f0_mean = window_sbr_and_f0(psi_center_history, dt=1.0, W=128, hop=64)
    vortices_mean = float(np.mean(vortices_history))
    
    # Calculate Correlation between Mu and Phi mapping
    # 1. Pearson corr
    mu_flat = mu.flatten()
    phi_flat = phi.flatten()
    
    if np.std(mu_flat) > 0 and np.std(phi_flat) > 0:
        mu_phi_corr = np.corrcoef(mu_flat, phi_flat)[0, 1]
    else:
        mu_phi_corr = 0.0
        
    # 2. Overlap of top 5% cells
    top5_count = int(0.05 * len(mu_flat))
    mu_top5_idx = set(np.argsort(mu_flat)[-top5_count:])
    phi_top5_idx = set(np.argsort(phi_flat)[-top5_count:])
    
    if top5_count > 0:
        mu_phi_overlap_top5 = len(mu_top5_idx.intersection(phi_top5_idx)) / top5_count
    else:
        mu_phi_overlap_top5 = 0.0
            
    final_res = metrics_timeseries[-1].copy()
    final_res['sbr_mean'] = sbr_mean
    final_res['f0_mean_hz'] = f0_mean
    final_res['vortices_mean'] = vortices_mean
    final_res['mu_phi_corr'] = mu_phi_corr
    final_res['mu_phi_overlap_top5'] = mu_phi_overlap_top5
    
    return final_res, metrics_timeseries, mu, phi

def main():
    etas = [0.02] # Aggressive erosion focusing on structural differences
    rhos = [0.001]
    seeds = [17, 23, 41]
    mu_bases = [1.0, 0.1] # Vacuum vs Fog
    variants = ['V1', 'V2', 'V3']
    
    tasks = []
    
    # 1. True Baseline (standard Lineum without Mu)
    for s in seeds:
         tasks.append(('Baseline_Vanilla', 1.0, 0.0, 0.0, s))
         
    # 2. Add ablations
    for mu_base in mu_bases:
        for var in variants:
            for s in seeds:
                tasks.append((var, mu_base, 0.02, 0.001, s))
                
    print(f"Running {len(tasks)} mobility configurations...")
    
    pool = multiprocessing.Pool(processes=min(multiprocessing.cpu_count(), len(tasks)))
    results = list(tqdm(pool.imap(run_mobility_experiment, tasks), total=len(tasks)))
    pool.close()
    pool.join()
    
    # Aggregate Results
    summary_data = []
    all_timeseries = []
    
    for final_res, ts, _, _ in results:
        summary_data.append(final_res)
        all_timeseries.extend(ts)
        
    df_summary = pd.DataFrame(summary_data)
    df_ts = pd.DataFrame(all_timeseries)
    
    df_grouped = df_summary.groupby(['variant', 'mu_base', 'eta', 'rho']).agg({
        'top20_share': ['mean', 'std'],
        'top10_share': 'mean',
        'top1_share': 'mean',
        'gini': 'mean',
        'sbr_mean': 'mean',
        'f0_mean_hz': 'mean',
        'vortices_mean': 'mean',
        'mu_phi_corr': 'mean',
        'mu_phi_overlap_top5': 'mean'
    }).reset_index()
    
    df_grouped.columns = ['_'.join(col).strip() if col[1] else col[0] for col in df_grouped.columns.values]
    
    out_dir = os.path.join(os.path.dirname(__file__), "..", "output_mobility")
    os.makedirs(out_dir, exist_ok=True)
    
    df_ts.to_csv(os.path.join(out_dir, "mobility_timeseries.csv"), index=False)
    df_grouped.to_csv(os.path.join(out_dir, "mobility_summary.csv"), index=False)
    
    # Plotting Top20 comparison
    plt.figure(figsize=(12, 6))
    
    baseline_df = df_ts[df_ts['variant'] == 'Baseline_Vanilla']
    if not baseline_df.empty:
        baseline_mean = baseline_df.groupby('step')['top20_share'].mean()
        plt.plot(baseline_mean.index, baseline_mean.values, label='Baseline Vanilla', linestyle='--', color='black', linewidth=2)
    
    colors = plt.cm.tab10(np.linspace(0, 1, len(variants) * len(mu_bases)))
    c_idx = 0
    for mu_b in mu_bases:
        for var in variants:
            combo_df = df_ts[(df_ts['variant'] == var) & (df_ts['mu_base'] == mu_b)]
            combo_mean = combo_df.groupby('step')['top20_share'].mean()
            plt.plot(combo_mean.index, combo_mean.values, label=f'{var} (mu={mu_b})', color=colors[c_idx])
            c_idx += 1

    plt.title('Top 20% Flow Concentration over Time (Mobility Field)')
    plt.xlabel('Step')
    plt.ylabel('Top 20 Share')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "mobility_top20_timeseries.png"))
    
    print("\n--- Summary of Mobility Results ---")
    print(df_grouped.to_string(index=False))
    print("\nFiles saved to output_mobility/")

if __name__ == '__main__':
    main()
