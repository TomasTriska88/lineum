import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from tqdm import tqdm
import multiprocessing

# Disable PyTorch CUDA entirely for this script before math.py gets imported
import unittest.mock
sys.modules['torch'] = unittest.mock.MagicMock()

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from lineum_core.math import evolve
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

def run_erosion_experiment(params):
    mode, p_norm, eta, rho, seed = params
    
    # 1. Setup scenario
    size = 128
    steps = 300
    np.random.seed(seed)
    
    psi = np.zeros((size, size), dtype=np.complex128)
    delta = np.zeros((size, size), dtype=np.float64)
    phi = np.zeros((size, size), dtype=np.float64)
    
    # Target Delta
    target_y, target_x = int(size*0.8), int(size*0.8)
    delta[target_y-2:target_y+3, target_x-2:target_x+3] = 50.0 # STRONG pull
    
    # Obstacles
    kappa_0 = np.ones((size, size), dtype=np.float64)
    for _ in range(40):
        oy, ox = np.random.randint(10, size-10, size=2)
        r = np.random.randint(2, 6)
        Y, X = np.ogrid[:size, :size]
        dist = np.sqrt((Y - oy)**2 + (X - ox)**2)
        kappa_0[dist <= r] = 0.05
        
    kappa = kappa_0.copy()
    kappa_min, kappa_max = 0.05, 1.0
    
    # Agents (100 agents, opposite target)
    sy, sx = int(size*0.2), int(size*0.2)
    
    cell_occupancy = np.zeros((size, size), dtype=np.float64)
    metrics_timeseries = []
    psi_center_history = []

    # 2. Simulation Loop
    for step in range(steps):
        # Inject agents
        dist_s = np.sqrt((np.arange(size)[:,None] - sy)**2 + (np.arange(size)[None,:] - sx)**2)
        psi[dist_s <= 3] = 10.0
        
        # Evolve (1 step)
        psi, phi = evolve(psi, delta, phi, kappa)
        psi *= (kappa > 0.05)
        
        # Collect center amp for core SBR/f0 metrics
        # Measuring average absolute psi around the center of the grid to ensure non-zero readings
        c_y, c_x = size // 2, size // 2
        center_amp = float(np.mean(np.abs(psi[c_y-1:c_y+2, c_x-1:c_x+2])))
        psi_center_history.append(center_amp)
        
        J_t = np.clip(np.abs(psi)**p_norm, 0, 10.0) 
        cell_occupancy += J_t
        
        # Erosion Dynamics (plasticity) -> Update Kappa
        if eta > 0 or rho > 0:
            traffic_term = eta * J_t
            relaxation_term = rho * (kappa_0 - kappa)
            if mode == 'down': # kappa drops: 'traffic clog' 
                kappa = np.clip(kappa - traffic_term + relaxation_term, kappa_min, kappa_max)
            elif mode == 'up': # kappa rises: 'path erosion / smoothing'
                kappa = np.clip(kappa + traffic_term + relaxation_term, kappa_min, kappa_max)

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
                'mode': mode, 'p_norm': p_norm, 'eta': eta, 'rho': rho, 'seed': seed, 'step': step + 1,
                'top20_share': top20_share, 'top10_share': top10_share, 
                'top1_share': top1_share, 'gini': gini
            })

    # End of run: Evaluate windowed SBR and f0 from center amplitudes
    sbr_mean, f0_mean = window_sbr_and_f0(psi_center_history, dt=1.0, W=128, hop=64)
            
    final_res = metrics_timeseries[-1].copy()
    final_res['sbr_mean'] = sbr_mean
    final_res['f0_mean_hz'] = f0_mean
    
    return final_res, metrics_timeseries

def main():
    etas = [0.001, 0.005, 0.02]
    rhos = [0.0, 0.001, 0.01]
    seeds = [17, 23, 41]
    
    tasks = []
    
    # 1. Baseline
    for s in seeds:
        tasks.append(('base', 2, 0.0, 0.0, s))
        
    # 2. Double Erosion Test (mode up vs down, p=2)
    for mode in ['down', 'up']:
        for eta in etas:
            for rho in rhos:
                for s in seeds:
                    tasks.append((mode, 2, eta, rho, s))
                    
    # 3. J_t Traffic definitions (p=4 for specific setup)
    # Testing for mode='up', eta=0.02, rho=0.001, p=4
    for s in seeds:
        tasks.append(('up', 4, 0.02, 0.001, s))
                
    print(f"Running {len(tasks)} configurations...")
    
    pool = multiprocessing.Pool(processes=min(multiprocessing.cpu_count(), len(tasks)))
    results = list(tqdm(pool.imap(run_erosion_experiment, tasks), total=len(tasks)))
    pool.close()
    pool.join()
    
    # 1. Aggregate Results
    summary_data = []
    all_timeseries = []
    
    for final_res, ts in results:
        summary_data.append(final_res)
        all_timeseries.extend(ts)
        
    df_summary = pd.DataFrame(summary_data)
    df_ts = pd.DataFrame(all_timeseries)
    
    # Group by config across seeds
    df_grouped = df_summary.groupby(['mode', 'p_norm', 'eta', 'rho']).agg({
        'top20_share': ['mean', 'std'],
        'top10_share': 'mean',
        'top1_share': ['mean', 'max'],
        'gini': 'mean',
        'sbr_mean': 'mean',
        'f0_mean_hz': 'mean'
    }).reset_index()
    
    # Flatten multi-index columns
    df_grouped.columns = ['_'.join(col).strip() if col[1] else col[0] for col in df_grouped.columns.values]
    
    out_dir = os.path.join(os.path.dirname(__file__), "..", "output_erosion_v2")
    os.makedirs(out_dir, exist_ok=True)
    
    # Save CSVs
    df_ts.to_csv(os.path.join(out_dir, "erosion_v2_timeseries.csv"), index=False)
    df_grouped.to_csv(os.path.join(out_dir, "erosion_v2_summary.csv"), index=False)
    
    # Plotting
    plt.figure(figsize=(12, 6))
    
    # Plot baseline
    baseline_df = df_ts[(df_ts['mode'] == 'base') & (df_ts['eta'] == 0.0)]
    baseline_mean = baseline_df.groupby('step')['top20_share'].mean()
    plt.plot(baseline_mean.index, baseline_mean.values, label='Baseline', linestyle='--', color='black', linewidth=2)
    
    # Plot best down
    down_df = df_ts[(df_ts['mode'] == 'down') & (df_ts['eta'] == 0.02) & (df_ts['rho'] == 0.001) & (df_ts['p_norm'] == 2)]
    down_mean = down_df.groupby('step')['top20_share'].mean()
    plt.plot(down_mean.index, down_mean.values, label='Down (Clogging) eta=0.02 rho=0.001 p=2', color='red')

    # Plot best up
    up_df = df_ts[(df_ts['mode'] == 'up') & (df_ts['eta'] == 0.02) & (df_ts['rho'] == 0.001) & (df_ts['p_norm'] == 2)]
    up_mean = up_df.groupby('step')['top20_share'].mean()
    plt.plot(up_mean.index, up_mean.values, label='Up (Erosion) eta=0.02 rho=0.001 p=2', color='green')
    
    # Plot p=4
    p4_df = df_ts[(df_ts['mode'] == 'up') & (df_ts['eta'] == 0.02) & (df_ts['rho'] == 0.001) & (df_ts['p_norm'] == 4)]
    p4_mean = p4_df.groupby('step')['top20_share'].mean()
    plt.plot(p4_mean.index, p4_mean.values, label='Up (Erosion) eta=0.02 rho=0.001 p=4', color='blue')

    plt.title('Top 20% Flow Concentration over Time (Kappa Up vs Down)')
    plt.xlabel('Step')
    plt.ylabel('Top 20 Share')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "v2_top20_timeseries.png"))
    
    print("\n--- Summary of Erosion V2 ---")
    print(df_grouped.to_string(index=False))
    print("\nFiles saved to output_erosion_v2/")

if __name__ == '__main__':
    main()
