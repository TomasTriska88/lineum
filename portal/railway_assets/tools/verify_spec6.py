
import numpy as np
import pandas as pd
import scipy.signal
import scipy.stats
import json
from pathlib import Path
import warnings

warnings.filterwarnings('ignore')

RUN_DIR = r"c:\Users\Tomáš\Documents\GitHub\lineum-core\output_wp\runs\spec6_false_s41_20260215_023130"
PREFIX = "spec6_false_s41"
RESULTS_FILE = "verification_results.json"

results = {}

def load_data():
    path = Path(RUN_DIR)
    try:
        phi = pd.read_csv(path / f"{PREFIX}_phi_center_log.csv")
    except: phi = None
    try:
        topo = pd.read_csv(path / f"{PREFIX}_topo_log.csv")
    except: topo = None
    try:
        traj = pd.read_csv(path / f"{PREFIX}_trajectories.csv")
    except: traj = None
    return phi, topo, traj

def iid_bootstrap_ci(data, func, n_resamples=200):
    try:
        data = np.array(data, dtype=float)
        if len(data) < 10: return None, None
        res = scipy.stats.bootstrap((data,), func, n_resamples=n_resamples, method='percentile')
        return [float(res.confidence_interval.low), float(res.confidence_interval.high)]
    except:
        return [None, None]

def block_bootstrap_ci(data, func, block_size, n_resamples=200):
    """
    Circular Block Bootstrap for autocorrelated time series.
    """
    try:
        data = np.array(data, dtype=float)
        n = len(data)
        if n < 10 or block_size <= 0: return [None, None]
        
        block_size = int(block_size)
        # Ideally block_size ~ correlation length.
        
        stats = []
        for _ in range(n_resamples):
            # Resample blocks
            indices = np.random.randint(0, n, n) # Starting positions for blocks
            # This is a simplification (moving block bootstrap usually implies constructing a new series of length n by joining blocks)
            # Efficient Circular Block Bootstrap:
            
            new_data = np.zeros(n)
            current_idx = 0
            while current_idx < n:
                start_ptr = np.random.randint(0, n)
                chunk = np.take(data, range(start_ptr, start_ptr + block_size), mode='wrap')
                
                needed = n - current_idx
                if len(chunk) > needed:
                    chunk = chunk[:needed]
                
                new_data[current_idx:current_idx + len(chunk)] = chunk
                current_idx += len(chunk)
            
            stats.append(func(new_data))
            
        alpha = 0.05
        low = np.percentile(stats, 100 * (alpha / 2))
        high = np.percentile(stats, 100 * (1 - alpha / 2))
        return [float(low), float(high)]
    except Exception as e:
        print(f"Block bootstrap failed: {e}")
        return [None, None]

def analyze_phi(phi_df):
    if phi_df is None: return
    
    target_col = phi_df.columns[1] 
    series = phi_df[target_col].values
    
    # --- Tau Calculation ---
    def calc_tau(x):
        try:
            x = np.array(x)
            if np.std(x) == 0: return len(x)
            norm = (x - np.mean(x))
            acf = np.correlate(norm, norm, mode='full')
            acf = acf[acf.size // 2:]
            acf /= acf[0]
            crossings = np.where(acf < 0.5)[0]
            if len(crossings) > 0: return int(crossings[0])
            return len(x)
        except: return 0

    tau_val = calc_tau(series)
    
    # Sensitivity Analysis
    block_sizes = [90, 180, 360, 720]
    tau_sensitivity = {}
    sbr_sensitivity = {}
    
    # Median bootstrap collector for Tau
    tau_distributions = {}

    def get_bootstrap_dist(data, func, blk):
        stats = []
        n = len(data)
        for _ in range(200):
            new_data = np.zeros(n)
            current_idx = 0
            while current_idx < n:
                start_ptr = np.random.randint(0, n)
                chunk = np.take(data, range(start_ptr, start_ptr + blk), mode='wrap')
                needed = n - current_idx
                if len(chunk) > needed: chunk = chunk[:needed]
                new_data[current_idx:current_idx + len(chunk)] = chunk
                current_idx += len(chunk)
            stats.append(func(new_data))
        return stats

    for blk in block_sizes:
        # Tau
        d_tau = get_bootstrap_dist(series, calc_tau, blk)
        tau_distributions[blk] = d_tau
        low = np.percentile(d_tau, 2.5)
        high = np.percentile(d_tau, 97.5)
        tau_sensitivity[blk] = [float(low), float(high)]
        
        # SBR (re-using sbr func defined below)
        def calc_sbr_temp(x):
             try:
                signal = np.var(x)
                if signal == 0: return 0
                noise = scipy.stats.median_abs_deviation(x) ** 2
                if noise == 0: return 9999.0
                return float(signal / noise)
             except: return 0.0

        d_sbr = get_bootstrap_dist(series, calc_sbr_temp, blk)
        low_s = np.percentile(d_sbr, 2.5)
        high_s = np.percentile(d_sbr, 97.5)
        sbr_sensitivity[blk] = [float(low_s), float(high_s)]
    
    # Robust Tau (Median of distribution with L=360)
    tau_robust = float(np.median(tau_distributions[360]))

    results['tau'] = {
        'value': tau_val, 
        'robust_median': tau_robust,
        'sensitivity': tau_sensitivity,
        'block_size_used': 360
    }

    # --- SBR Calculation ---
    def calc_sbr(x):
        try:
            signal = np.var(x)
            if signal == 0: return 0
            noise = scipy.stats.median_abs_deviation(x) ** 2
            if noise == 0: return 9999.0
            return float(signal / noise)
        except: return 0.0

    sbr_val = calc_sbr(series)
    
    results['sbr'] = {
        'value': sbr_val, 
        'sensitivity': sbr_sensitivity
    }
    
    # --- Mode 24 (Band Analysis) ---
    freqs, psd = scipy.signal.welch(series)
    peak_idx = np.argmax(psd[1:]) + 1
    f0 = freqs[peak_idx]
    f24 = 24 * f0
    
    metrics_24 = {'f0': float(f0), 'f24': float(f24)}
    
    if f24 <= 0.5:
        # Band Power Ratio
        # Define band width. Let's say +/- 10% of f0?? No, that's huge at f24.
        # Let's say +/- 1 frequency bin index.
        df = freqs[1] - freqs[0]
        half_width = max(df, f0 * 0.05) # At least one bin, or 5% relative width
        
        def get_band_power(center_freq, hw):
            mask = (freqs >= center_freq - hw) & (freqs <= center_freq + hw)
            if not np.any(mask): return 0
            return np.sum(psd[mask])
            
        power_f0_band = get_band_power(f0, half_width)
        power_24_band = get_band_power(f24, half_width)
        
        # Peak Ratio (Old method)
        idx24 = np.argmin(np.abs(freqs - f24))
        power24_peak = psd[idx24]
        power_f0_peak = psd[peak_idx]
        
        metrics_24['peak_ratio'] = float(power24_peak/power_f0_peak) if power_f0_peak > 0 else 0
        metrics_24['band_ratio'] = float(power_24_band/power_f0_band) if power_f0_band > 0 else 0
        metrics_24['band_width'] = float(half_width)
    
    results['mode_24'] = metrics_24

def analyze_topo(topo_df):
    if topo_df is None: return
    cols = [c for c in topo_df.columns if 'count' in c.lower() or 'vortex' in c.lower() or 'total' in c.lower()]
    if not cols: return
    col = cols[0]
    data = topo_df[col].values
    
    def calc_cv(x):
        try:
            mu = np.mean(x)
            if mu == 0: return 0
            return float(np.std(x) / mu)
        except: return 0
        
    cv_val = calc_cv(data)
    
    # We need a block size for topo. Let's re-calculate tau for topo series.
    def fast_tau(x):
        try:
            norm = (x - np.mean(x))
            if np.std(x)==0: return len(x)
            acf = np.correlate(norm, norm, mode='full')[len(x)-1:]
            acf /= acf[0]
            c = np.where(acf < 0.5)[0]
            return int(c[0]) if len(c)>0 else len(x)
        except: return 10
        
    topo_tau = fast_tau(data)
    topo_blk = max(10, topo_tau)
    
    cv_iid = iid_bootstrap_ci(data, calc_cv)
    cv_block = block_bootstrap_ci(data, calc_cv, topo_blk)
    
    results['cv'] = {
        'value': cv_val, 
        'iid_ci': cv_iid, 
        'block_ci': cv_block,
        'block_size': topo_blk
    }

def analyze_primes(phi_df):
    try:
        npy_path = Path(RUN_DIR) / f"{PREFIX}_frames_phi.npy"
        if not npy_path.exists(): return
            
        frames = np.load(npy_path)
        if len(frames) > 100: frames = frames[-100:]
        mean_field = np.mean(frames, axis=0)
        H, W = mean_field.shape
        
        # Prime Mask
        mask = np.zeros((H, W))
        # Simple Sieve up to H*W
        limit = H*W + 2
        sieve = np.ones(limit, dtype=bool)
        sieve[0:2] = False
        for i in range(2, int(limit**0.5)+1):
            if sieve[i]:
                sieve[i*i:limit:i] = False
        
        for y in range(H):
            for x in range(W):
                if sieve[y*W + x + 1]: mask[y,x] = 1
        
        corr_real = np.corrcoef(mean_field.flatten(), mask.flatten())[0,1]
        
        null_corrs = []
        m_flat = mask.flatten()
        f_flat = mean_field.flatten()
        # Increased permutation budget lightly
        for i in range(50):
            np.random.shuffle(m_flat)
            null_corrs.append(np.corrcoef(f_flat, m_flat)[0,1])
            
        null_avg = np.mean(null_corrs)
        null_std = np.std(null_corrs)
        z_score = (corr_real - null_avg) / null_std if null_std > 0 else 0
        p_val = scipy.stats.norm.sf(abs(z_score))
        
        results['prime_test'] = {
            'correlation': float(corr_real),
            'z_score': float(z_score),
            'p_value': float(p_val),
            'verdict': "SIGNIFICANT" if p_val < 0.05 else "NOT_SIGNIFICANT"
        }
    except Exception as e:
        results['prime_test_error'] = str(e)

if __name__ == "__main__":
    phi, topo, traj = load_data()
    analyze_phi(phi)
    analyze_topo(topo)
    analyze_primes(phi)
    
    with open(RESULTS_FILE, 'w') as f:
        json.dump(results, f, indent=4)
    print("Verification complete. Results saved to JSON.")
