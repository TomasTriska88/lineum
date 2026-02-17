import pandas as pd
import numpy as np
from scipy.optimize import curve_fit, OptimizeWarning
import os
import sys
import warnings

# Suppress optimization warnings for cleaner output
warnings.simplefilter("ignore", OptimizeWarning)

# Paths - Relative to repo root if run from root, or absolute
# Defaulting to standard path for reproducibility
DEFAULT_RUN_DIR = r"output_wp\runs\spec6_false_s41_20260215_023130"

def get_file_path(filename, run_dir):
    # Try current directory first, then absolute path
    if os.path.exists(filename):
        return filename
    
    path = os.path.join(run_dir, filename)
    if os.path.exists(path):
        return path
        
    # Fallback to absolute if script is run from tools/
    abs_path = os.path.join(os.getcwd(), "..", run_dir, filename)
    if os.path.exists(abs_path):
        return abs_path
        
    return None

def calculate_sbr_robust(signal):
    """
    Calculates Signal-to-Background Ratio (SBR) using Robust Statistics.
    SBR = Variance(Signal) / MAD(Signal)^2
    In pure noise, this ratio converges to a constant (~1.0 for Gaussian).
    In signal, Variance >> MAD^2.
    """
    if len(signal) == 0: return 0.0
    
    # Robust estimator of noise floor
    median = np.median(signal)
    abs_dev = np.abs(signal - median)
    mad = np.median(abs_dev)
    
    if mad == 0: return 0.0 # Avoid division by zero
    
    variance = np.var(signal)
    
    # Scale MAD to Sigma for consistency (Sigma ~ 1.4826 * MAD)
    # But for SBR definition from report (Var/MAD^2), we use raw MAD or scaled?
    # Report says: "Var(x) / MAD^2(x)". Let's simplify to RMS / MAD.
    # Actually, let's stick to the report formula: SBR = Var / (1.4826 * MAD)^2
    # This aligns SBR=1.0 for Gaussian Noise.
    
    sigma_est = 1.4826 * mad
    sbr = variance / (sigma_est ** 2)
    
    return sbr

def analyze_run(run_dir=DEFAULT_RUN_DIR):
    print(f"--- ANALYZING RUN: {run_dir} ---")
    
    phi_log = get_file_path("spec6_false_s41_phi_center_log.csv", run_dir)
    topo_log = get_file_path("spec6_false_s41_topo_log.csv", run_dir)
    
    # 1. SBR & PHI ANALYSIS
    if phi_log:
        try:
            df = pd.read_csv(phi_log)
            # Assuming 'phi_0_0' or 'phi_central' is the signal
            col = 'phi_0_0' if 'phi_0_0' in df.columns else 'phi_central'
            if col in df.columns:
                signal = df[col].values
                
                # SBR
                sbr = calculate_sbr_robust(signal)
                print(f"METRIC_SBR: {sbr:.4f} (Interpretation: <2.0 = Noise, >10.0 = Signal)")
                
                # MODE 24 (Spectral)
                signal_detrend = signal - np.mean(signal)
                fft_vals = np.fft.fft(signal_detrend)
                power = np.abs(fft_vals)**2
                freqs = np.fft.fftfreq(len(signal_detrend))
                
                mask = freqs > 0
                power = power[mask]
                freqs = freqs[mask]
                
                idx_max = np.argmax(power)
                f0 = freqs[idx_max]
                print(f"METRIC_F0: {f0:.6f}")
                
                target_f = 24 * f0
                if target_f < 0.5:
                    idx_24 = np.argmin(np.abs(freqs - target_f))
                    power_24 = power[idx_24]
                    mean_power = np.mean(power)
                    ratio_24 = power_24 / mean_power
                    print(f"METRIC_MODE_24_RATIO: {ratio_24:.4e}")
                else:
                    print(f"METRIC_MODE_24_RATIO: N/A (Frequency {target_f:.4f} > Nyquist)")
                    
            else:
                print("DEBUG: Phi column not found.")
        except Exception as e:
            print(f"Phi Error: {e}")
    else:
        print("DEBUG: Phi Log not found.")

    # 2. TOPOLOGY (Cv)
    if topo_log:
        try:
            df = pd.read_csv(topo_log)
            col = 'count' if 'count' in df.columns else 'total_vortices'
            if col in df.columns:
                vals = df[col].values
                mean_v = np.mean(vals)
                std_v = np.std(vals)
                if mean_v > 0:
                    cv = std_v / mean_v
                    print(f"METRIC_CV: {cv:.4f} (Interpretation: <0.1 = Stable, >1.0 = Chaotic)")
                else:
                    print("METRIC_CV: 0.0 (Empty)")
        except Exception as e:
            print(f"Topology Error: {e}")
    else:
        print("DEBUG: Topo Log not found.")

if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "--run":
        analyze_run(sys.argv[2])
    else:
        # Default behavior
        base = os.path.join(os.getcwd(), "..") # Assuming running from tools/
        # Try to find the run folder
        target = os.path.join(base, DEFAULT_RUN_DIR)
        analyze_run(target)
