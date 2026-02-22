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
    eta, rho, seed = params
    
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
    # Generate 40 random high-friction obstacles
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

    # 2. Simulation Loop
    for step in range(steps):
        # Inject agents
        dist_s = np.sqrt((np.arange(size)[:,None] - sy)**2 + (np.arange(size)[None,:] - sx)**2)
        psi[dist_s <= 3] = 10.0
        
        # Evolve (1 step)
        psi, phi = evolve(psi, delta, phi, kappa)
        psi *= (kappa > 0.05)
        
        # Measure traffic (absolute amplitude roughly maps to traffic)
        # Using amp^2 to approximate J_t
        J_t = np.clip(np.abs(psi)**2, 0, 10.0) 
        
        # Accumulate occupancy
        cell_occupancy += J_t
        
        # Erosion Dynamics (plasticity) -> Update Kappa
        if eta > 0 or rho > 0:
            erosion_term = eta * J_t
            relaxation_term = rho * (kappa_0 - kappa)
            kappa = np.clip(kappa - erosion_term + relaxation_term, kappa_min, kappa_max)

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
                'eta': eta, 'rho': rho, 'seed': seed, 'step': step + 1,
                'top20_share': top20_share, 'top10_share': top10_share, 
                'top1_share': top1_share, 'gini': gini
            })

    # Final summary for this run
    final_res = metrics_timeseries[-1].copy()
    
    return final_res, metrics_timeseries, cell_occupancy

def main():
    etas = [0.0, 0.001, 0.005, 0.02] # Added 0.0 for baseline
    rhos = [0.0, 0.001, 0.01]
    seeds = [17, 23, 41]
    
    tasks = []
    # Baseline
    for s in seeds:
        tasks.append((0.0, 0.0, s))
    # Experiment grid
    for eta in etas[1:]:
        for rho in rhos:
            for s in seeds:
                tasks.append((eta, rho, s))
                
    print(f"Running {len(tasks)} configurations...")
    
    pool = multiprocessing.Pool(processes=min(multiprocessing.cpu_count(), len(tasks)))
    results = list(tqdm(pool.imap(run_erosion_experiment, tasks), total=len(tasks)))
    pool.close()
    pool.join()
    
    # 1. Aggregate Results
    summary_data = []
    all_timeseries = []
    
    for final_res, ts, occ in results:
        summary_data.append(final_res)
        all_timeseries.extend(ts)
        
    df_summary = pd.DataFrame(summary_data)
    df_ts = pd.DataFrame(all_timeseries)
    
    # Group by eta, rho across seeds
    df_grouped = df_summary.groupby(['eta', 'rho']).agg({
        'top20_share': ['mean', 'std'],
        'top10_share': 'mean',
        'top1_share': ['mean', 'max'],
        'gini': 'mean'
    }).reset_index()
    
    # Flatten multi-index columns for easy printing
    df_grouped.columns = ['_'.join(col).strip() if col[1] else col[0] for col in df_grouped.columns.values]
    
    # Make dir
    out_dir = os.path.join(os.path.dirname(__file__), "..", "output_erosion")
    os.makedirs(out_dir, exist_ok=True)
    
    # Save CSVs
    df_ts.to_csv(os.path.join(out_dir, "erosion_timeseries.csv"), index=False)
    df_grouped.to_csv(os.path.join(out_dir, "erosion_summary.csv"), index=False)
    
    # Generate time series plot for best combinations (and baseline)
    plt.figure(figsize=(12, 6))
    
    # Plot baseline
    baseline_df = df_ts[(df_ts['eta'] == 0.0) & (df_ts['rho'] == 0.0)]
    baseline_mean = baseline_df.groupby('step')['top20_share'].mean()
    plt.plot(baseline_mean.index, baseline_mean.values, label='Baseline (eta=0, rho=0)', linestyle='--', color='black', linewidth=2)
    
    # Plot other combinations
    colors = plt.cm.tab10(np.linspace(0, 1, len(etas[1:]) * len(rhos)))
    c_idx = 0
    for eta in etas[1:]:
        for rho in rhos:
            combo_df = df_ts[(df_ts['eta'] == eta) & (df_ts['rho'] == rho)]
            combo_mean = combo_df.groupby('step')['top20_share'].mean()
            plt.plot(combo_mean.index, combo_mean.values, label=f'eta={eta}, rho={rho}', color=colors[c_idx])
            c_idx += 1
            
    plt.title('Top 20% Flow Concentration over Time')
    plt.xlabel('Step')
    plt.ylabel('Top 20 Share')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "top20_timeseries.png"))
    
    # Generate Gini time series
    plt.figure(figsize=(12, 6))
    baseline_gini = baseline_df.groupby('step')['gini'].mean()
    plt.plot(baseline_gini.index, baseline_gini.values, label='Baseline (eta=0, rho=0)', linestyle='--', color='black', linewidth=2)
    
    c_idx = 0
    for eta in etas[1:]:
        for rho in rhos:
            combo_df = df_ts[(df_ts['eta'] == eta) & (df_ts['rho'] == rho)]
            combo_gini = combo_df.groupby('step')['gini'].mean()
            plt.plot(combo_gini.index, combo_gini.values, label=f'eta={eta}, rho={rho}', color=colors[c_idx])
            c_idx += 1
            
    plt.title('Gini Coefficient over Time')
    plt.xlabel('Step')
    plt.ylabel('Gini')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "gini_timeseries.png"))
    
    print("\n--- Summary of Eta & Rho ---")
    print(df_grouped.to_string(index=False))
    print("\nFiles saved to output_erosion/")

if __name__ == '__main__':
    main()
