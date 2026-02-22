import os
import sys
import numpy as np
import pandas as pd
from tqdm import tqdm
import multiprocessing
import unittest.mock

# Disable PyTorch CUDA entirely for this script before math.py gets imported
sys.modules['torch'] = unittest.mock.MagicMock()
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from lineum_core import math as core_math

# Optional explicitly use numpy for harnessing
core_math.USE_PYTORCH = False

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

def get_vortices(psi):
    phase = np.angle(psi)
    d_x = np.angle(np.exp(1j * (np.roll(phase, -1, axis=1) - phase)))
    d_y = np.angle(np.exp(1j * (np.roll(phase, -1, axis=0) - phase)))
    curl = d_x - np.roll(d_x, -1, axis=0) - d_y + np.roll(d_y, -1, axis=1)
    return int(np.sum(np.abs(curl) > np.pi))

def run_harness_test(params):
    variant, seed, mode = params
    size = 128
    
    if mode == "canonical_core":
        steps = 2000
    else:
        steps = 300
    
    # Enable experimental term only if variant requests it
    if variant == "EXP_TERM_ON":
        core_math.EXPERIMENTAL_TERM = 1
    else:
        core_math.EXPERIMENTAL_TERM = 0
        
    np.random.seed(seed)
    
    psi = np.zeros((size, size), dtype=np.complex128)
    delta = np.zeros((size, size), dtype=np.float64)
    phi = np.zeros((size, size), dtype=np.float64)
    
    target_y, target_x = int(size*0.8), int(size*0.8)
    delta[target_y-2:target_y+3, target_x-2:target_x+3] = 50.0 
    
    # A few random obstacles
    kappa = np.ones((size, size), dtype=np.float64)
    for _ in range(30):
        oy, ox = np.random.randint(10, size-10, size=2)
        r = np.random.randint(2, 6)
        Y, X = np.ogrid[:size, :size]
        kappa[np.sqrt((Y - oy)**2 + (X - ox)**2) <= r] = 0.05
        
    sy, sx = int(size*0.2), int(size*0.2)
    
    psi_center_history = []
    vortices_history = []
    c_y, c_x = size//2, size//2
    
    phi_half_life_steps = -1
    phi_peak_seen = False
    phi_peak_val = 0.0
    
    for step in range(steps):
        dist_s = np.sqrt((np.arange(size)[:,None] - sy)**2 + (np.arange(size)[None,:] - sx)**2)
        psi[dist_s <= 3] = 10.0
        
        psi, phi = core_math.evolve(psi, delta, phi, kappa)
        psi *= (kappa > 0.05)
        
        # Track core metrics
        psi_center_history.append(float(np.mean(np.abs(psi[c_y-1:c_y+2, c_x-1:c_x+2]))))
        vortices_history.append(get_vortices(psi))
        
        # Track Phi Half-Life surrogate
        curr_phi_mean = float(np.mean(phi))
        if curr_phi_mean > phi_peak_val:
            phi_peak_val = curr_phi_mean
            phi_peak_seen = True
        elif phi_peak_seen and curr_phi_mean < phi_peak_val * 0.5 and phi_half_life_steps == -1:
            phi_half_life_steps = step

    sbr_mean, f0_mean = window_sbr_and_f0(psi_center_history, dt=1.0, W=128, hop=64)
    vortices_mean = float(np.mean(vortices_history))
    
    # Topology neutrality N1 proxy
    N1 = float(np.mean(np.abs(np.fft.fft2(np.abs(psi)))[1:5, 1:5]))

    return {
        'mode': mode,
        'variant': variant,
        'seed': seed,
        'steps': steps,
        'sbr_mean': sbr_mean,
        'f0_mean_hz': f0_mean,
        'vortices_mean': vortices_mean,
        'N1_topology_neutrality': N1,
        'phi_half_life_steps': phi_half_life_steps
    }

def main():
    mode = os.environ.get("MODE", "exp")
    
    tasks = []
    if mode == "canonical_core":
        seeds = [41]
    else:
        seeds = [42, 101, 777]
        
    for s in seeds:
        tasks.append(("Baseline", s, mode))
        tasks.append(("EXP_TERM_ON", s, mode))

    print(f"Running fail-fast term harness...")
    pool = multiprocessing.Pool(processes=min(multiprocessing.cpu_count(), len(tasks)))
    results = list(tqdm(pool.imap(run_harness_test, tasks), total=len(tasks)))
    pool.close(); pool.join()
    
    df = pd.DataFrame(results)
    
    # Group and compare
    grouped = df.groupby('variant').mean(numeric_only=True).reset_index()
    
    out_dir = os.path.join(os.path.dirname(__file__), "..", "output_term_harness")
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, "term_ablation_summary.csv")
    grouped.to_csv(out_file, index=False)
    
    print("\n--- Fail-Fast Export Summary ---")
    print(grouped.to_string(index=False))
    print(f"\nSaved to: {out_file}")

if __name__ == '__main__':
    main()
