import os
import sys
import numpy as np
import pandas as pd
import scipy.ndimage
import gzip
from tqdm import tqdm
import multiprocessing
import unittest.mock
import matplotlib.pyplot as plt

# Disable PyTorch CUDA entirely for this script before math.py gets imported
sys.modules['torch'] = unittest.mock.MagicMock()
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from lineum_core import math as core_math

# We use the NumPy engine
core_math.USE_PYTORCH = False

def radial_profile(data, center):
    y, x = np.indices((data.shape))
    r = np.sqrt((x - center[0])**2 + (y - center[1])**2)
    r = r.astype(int)
    tbin = np.bincount(r.ravel(), data.ravel())
    nr = np.bincount(r.ravel())
    radialprofile = tbin / np.maximum(nr, 1)
    return radialprofile

def spectrum_slope(map_data):
    F = np.fft.fft2(map_data)
    Fshift = np.fft.fftshift(F)
    psd2D = np.abs(Fshift)**2
    
    center = (map_data.shape[1]//2, map_data.shape[0]//2)
    psd1D = radial_profile(psd2D, center)
    
    freqs = np.arange(1, len(psd1D))
    psd = psd1D[1:]
    
    valid = psd > 0
    if not np.any(valid): return float('nan')
    log_f = np.log10(freqs[valid])
    log_p = np.log10(psd[valid])
    
    if len(log_f) < 2: return float('nan')
    slope, _ = np.polyfit(log_f, log_p, 1)
    return float(slope)

def box_counting_dim(Z):
    p = min(Z.shape)
    n = 2**np.floor(np.log(p)/np.log(2))
    n = int(np.log(n)/np.log(2))
    sizes = 2**np.arange(n, 1, -1)
    counts = []
    
    for size in sizes:
        count = 0
        for x in range(0, Z.shape[0] - size + 1, size):
            for y in range(0, Z.shape[1] - size + 1, size):
                if np.any(Z[x:x+size, y:y+size]):
                    count += 1
        counts.append(count)
        
    if len(counts) < 2 or counts[0] == 0: return 0.0
    coeffs = np.polyfit(np.log(sizes), np.log(counts), 1)
    return float(-coeffs[0])

def downsample_corr(map_data, factor=4):
    down = scipy.ndimage.zoom(map_data, 1.0/factor, order=1)
    up = scipy.ndimage.zoom(down, factor, order=1)
    
    min_x = min(up.shape[0], map_data.shape[0])
    min_y = min(up.shape[1], map_data.shape[1])
    
    up_crop = up[:min_x, :min_y]
    md_crop = map_data[:min_x, :min_y]
    
    if up_crop.shape != md_crop.shape: return float('nan')
    corr = np.corrcoef(md_crop.ravel(), up_crop.ravel())[0, 1]
    return float(corr)

def compression_proxy(map_data):
    csv_str = ",".join([f"{x:.4f}" for x in map_data.ravel()])
    return len(gzip.compress(csv_str.encode('utf-8')))

def get_structural_components(binary_map):
    labeled, num_features = scipy.ndimage.label(binary_map)
    return int(num_features)

def custom_evolve_with_mu(psi, delta, phi, kappa, mu, variant):
    if variant == "V1":
        # Drift modulation
        grad_phi_x, grad_phi_y = np.gradient(phi * mu)
        phi_flow = core_math.DRIFT_STRENGTH * (grad_phi_x + 1j * grad_phi_y) * kappa
        psi += phi_flow
        psi, phi = core_math.evolve(psi, delta, phi, kappa)
        psi -= phi_flow # Revert standard drift added by evolve (approximation for scripting)
    elif variant == "V2":
        # Drift + Interaction
        grad_phi_x, grad_phi_y = np.gradient(phi * mu)
        phi_flow = core_math.DRIFT_STRENGTH * (grad_phi_x + 1j * grad_phi_y) * kappa
        psi += phi_flow
        interaction = 0.04 * np.clip(phi * mu, 0.0, core_math.PHI_INTERACTION_CAP) * psi * kappa
        psi += interaction
        psi, phi = core_math.evolve(psi, delta, phi, kappa)
    else:
        psi, phi = core_math.evolve(psi, delta, phi, kappa)
    return psi, phi

def compute_metrics(phi_end, phi_prev, kappa, variant, seed, grid_size, k_thresholds, ds_factors):
    # Base novelty and compression
    l1_diff = np.sum(np.abs(phi_end - phi_prev))
    total_active = np.sum(phi_end) + 1e-9
    novelty_score = float(l1_diff / total_active)
    comp_size = compression_proxy(phi_end)
    
    valid_mask = kappa > 0.1
    phi_masked = phi_end * valid_mask
    
    # Spectrum slope is invariant to thresholding
    slope = spectrum_slope(phi_masked)
    
    results = []
    flat_valid = phi_masked[valid_mask]
    
    if len(flat_valid) > 0:
        for k in k_thresholds:
            thresh = np.percentile(flat_valid, 100 - k)
            binary_map = (phi_masked >= thresh) & valid_mask
            
            struct_count = get_structural_components(binary_map)
            box_dim = box_counting_dim(binary_map)
            
            for ds in ds_factors:
                corr = downsample_corr(phi_masked, factor=ds) # we correlate the masked phi map, not the binary one
                
                results.append({
                    'model': variant,
                    'seed': seed,
                    'grid_size': grid_size,
                    'threshold_pct': k,
                    'downsample_factor': ds,
                    'box_counting_dim': box_dim,
                    'downsample_corr': corr,
                    'spectrum_slope': slope,
                    'novelty_vs_prev': novelty_score,
                    'compression_bytes': comp_size,
                    'structural_components': struct_count
                })
    else:
        for k in k_thresholds:
            for ds in ds_factors:
                results.append({
                    'model': variant,
                    'seed': seed,
                    'grid_size': grid_size,
                    'threshold_pct': k,
                    'downsample_factor': ds,
                    'box_counting_dim': 0.0,
                    'downsample_corr': 0.0,
                    'spectrum_slope': slope,
                    'novelty_vs_prev': novelty_score,
                    'compression_bytes': comp_size,
                    'structural_components': 0
                })
                
    return results

def run_novelty_scenario(params):
    variant, seed, size, mode = params
    steps = 300
    np.random.seed(seed)
    
    psi = np.zeros((size, size), dtype=np.complex128)
    delta = np.zeros((size, size), dtype=np.float64)
    phi = np.zeros((size, size), dtype=np.float64)
    mu = np.ones((size, size), dtype=np.float64) * 0.1 # Fog base
    
    target_y, target_x = int(size*0.8), int(size*0.8)
    delta[target_y-2:target_y+3, target_x-2:target_x+3] = 50.0
    
    kappa = np.ones((size, size), dtype=np.float64)
    num_obstacles = 40 if size == 128 else 100
    for _ in range(num_obstacles):
        oy, ox = np.random.randint(5, size-5, size=2)
        r = np.random.randint(2, 6)
        Y, X = np.ogrid[:size, :size]
        kappa[np.sqrt((Y - oy)**2 + (X - ox)**2) <= r] = 0.05
        
    sy, sx = int(size*0.2), int(size*0.2)
    
    phi_history = {}
    time_series_data = []
    
    for step in range(steps):
        dist_s = np.sqrt((np.arange(size)[:,None] - sy)**2 + (np.arange(size)[None,:] - sx)**2)
        psi[dist_s <= 3] = 10.0
        
        if variant == "Baseline":
            psi, phi = core_math.evolve(psi, delta, phi, kappa)
        else:
            psi, phi = custom_evolve_with_mu(psi, delta, phi, kappa, mu, variant)
        
        psi *= (kappa > 0.05)
        J_t = np.clip(np.abs(psi)**2, 0, 10.0)
        
        if variant != "Baseline":
            mu += 0.02 * J_t - 0.001 * (mu - 0.1)
            mu = np.clip(mu, 0.05, 1.0)
            
        phi_history[step] = phi.copy()
            
        if mode == "time_series" and step % 25 == 0 and step >= 25:
            # Quick metric for time series (default threshold 5%, ds 4x)
            prev = phi_history[step - 25]
            m = compute_metrics(phi, prev, kappa, variant, seed, size, [5], [4])[0]
            m['step'] = step
            time_series_data.append(m)

    if mode == "time_series":
        return time_series_data
        
    # Sweep mode calculation at end
    phi_end = phi_history[299]
    phi_prev = phi_history[249]
    k_thresholds = [1, 2, 5, 10, 20]
    ds_factors = [2, 4, 8]
    
    return compute_metrics(phi_end, phi_prev, kappa, variant, seed, size, k_thresholds, ds_factors)

def generate_plots(df_sweep, df_ts):
    out_dir = os.path.join(os.path.dirname(__file__), "..", "output_mobility_v2", "novelty_selfsim_plots")
    os.makedirs(out_dir, exist_ok=True)
    
    # 1. D0 vs k
    plt.figure(figsize=(8, 6))
    for model in df_sweep['model'].unique():
        ds = df_sweep[(df_sweep['model'] == model) & (df_sweep['grid_size'] == 128) & (df_sweep['downsample_factor'] == 4)]
        grouped = ds.groupby('threshold_pct')['box_counting_dim'].mean().reset_index()
        plt.plot(grouped['threshold_pct'], grouped['box_counting_dim'], label=model, marker='o')
    plt.xlabel('Top k% Threshold')
    plt.ylabel('Box Counting Dim D0')
    plt.title('Fractal Dimension vs Threshold')
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.savefig(os.path.join(out_dir, 'D0_vs_k.png'))
    plt.close()
    
    # 2. corr vs k (actually ds changes corr, not k... corr is on the continuous map)
    # Let's plot corr vs downsample factor
    plt.figure(figsize=(8, 6))
    for model in df_sweep['model'].unique():
        # filter to 1 thresold since corr doesnt depend on binary threshold
        ds = df_sweep[(df_sweep['model'] == model) & (df_sweep['grid_size'] == 128) & (df_sweep['threshold_pct'] == 5)]
        grouped = ds.groupby('downsample_factor')['downsample_corr'].mean().reset_index()
        plt.plot(grouped['downsample_factor'], grouped['downsample_corr'], label=model, marker='s')
    plt.xlabel('Downsample Factor')
    plt.ylabel('Pearson Correlation')
    plt.title('Downsample Correlation vs Zoom Factor')
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.savefig(os.path.join(out_dir, 'corr_vs_downsample.png'))
    plt.close()
    
    # 3. slope vs model
    plt.figure(figsize=(8, 6))
    slopes = []
    models = sorted(df_sweep['model'].unique())
    for model in models:
        sl = df_sweep[(df_sweep['model'] == model) & (df_sweep['grid_size'] == 128) & (df_sweep['threshold_pct'] == 5) & (df_sweep['downsample_factor'] == 4)]['spectrum_slope'].mean()
        slopes.append(sl)
    plt.bar(models, slopes, color=['blue', 'orange', 'green'])
    plt.ylabel('Spectrum Slope (log-log)')
    plt.title('Power Spectrum Veining vs Noise')
    plt.grid(True, alpha=0.3, axis='y')
    plt.savefig(os.path.join(out_dir, 'slope_vs_model.png'))
    plt.close()
    
    # 4. Time Series emergence
    if df_ts is not None and not df_ts.empty:
        plt.figure(figsize=(10, 5))
        for model in df_ts['model'].unique():
            ds = df_ts[df_ts['model'] == model]
            plt.plot(ds['step'], ds['novelty_vs_prev'], label=f"{model} Novelty", linestyle='--')
            
        plt.xlabel('Steps')
        plt.ylabel('Novelty vs Prev 25 steps (L1 Norm)')
        plt.title('Structural Emergence over Time')
        plt.grid(True, alpha=0.3)
        plt.legend()
        plt.savefig(os.path.join(out_dir, 'time_series_novelty.png'))
        plt.close()

def main():
    # Sweep Scenarios
    scenarios = []
    models = ["Baseline", "V1", "V2"]
    seeds = [17, 41, 73]
    
    for m in models:
        for s in seeds:
            scenarios.append((m, s, 128, "sweep"))
        # Add grid size check for seed 41
        scenarios.append((m, 41, 256, "sweep"))
                 
    print("Running Novelty & Self-Similarity Sweep...")
    pool = multiprocessing.Pool(processes=min(multiprocessing.cpu_count(), len(scenarios)))
    results = list(tqdm(pool.imap(run_novelty_scenario, scenarios), total=len(scenarios)))
    pool.close(); pool.join()
    
    flat_results = []
    for r in results:
        flat_results.extend(r)
        
    df_sweep = pd.DataFrame(flat_results)
    
    # Time Series Scenarios (Baseline vs V2, seed 41, 128)
    ts_scenarios = [("Baseline", 41, 128, "time_series"), ("V2", 41, 128, "time_series")]
    print("Running Time Series...")
    ts_results = [run_novelty_scenario(p) for p in ts_scenarios]
    
    flat_ts = []
    for r in ts_results:
        flat_ts.extend(r)
    df_ts = pd.DataFrame(flat_ts)
    
    # Export
    out_dir = os.path.join(os.path.dirname(__file__), "..", "output_mobility_v2")
    os.makedirs(out_dir, exist_ok=True)
    sweep_file = os.path.join(out_dir, "novelty_selfsim_sweep_summary.csv")
    df_sweep.to_csv(sweep_file, index=False)
    
    ts_file = os.path.join(out_dir, "novelty_selfsim_timeseries.csv")
    df_ts.to_csv(ts_file, index=False)
    
    # Plots
    generate_plots(df_sweep, df_ts)
    
    print("\n--- Geometric Sweep Subsample ---")
    sub = df_sweep[(df_sweep['threshold_pct']==5) & (df_sweep['downsample_factor']==4) & (df_sweep['grid_size']==128)]
    grouped = sub.groupby('model').mean(numeric_only=True).reset_index()
    print(grouped[['model', 'novelty_vs_prev', 'box_counting_dim', 'downsample_corr', 'spectrum_slope', 'compression_bytes']].to_string(index=False))
    print(f"\nSaved CSVs to: {out_dir}")
    print(f"Saved PNGs to: {os.path.join(out_dir, 'novelty_selfsim_plots')}")

if __name__ == "__main__":
    main()
