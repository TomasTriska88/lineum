import os
import sys
import time
import numpy as np
import warnings
warnings.filterwarnings('ignore')

# Add lineum to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + '/..'))
from lineum_core.math import evolve

def detect_vortices(phase: np.ndarray) -> np.ndarray:
    p00 = phase[:-1, :-1]
    p01 = phase[:-1, 1:]
    p11 = phase[1:, 1:]
    p10 = phase[1:, :-1]

    d1 = np.angle(np.exp(1j * (p01 - p00)))
    d2 = np.angle(np.exp(1j * (p11 - p01)))
    d3 = np.angle(np.exp(1j * (p10 - p11)))
    d4 = np.angle(np.exp(1j * (p00 - p10)))
    winding = (d1 + d2 + d3 + d4) / (2 * np.pi)

    vortices = np.zeros_like(phase, dtype=int)
    block = vortices[:-1, :-1]
    block[winding > 0.5] = 1
    block[winding < -0.5] = -1
    return vortices

def run_seed_native(seed):
    print(f"\n--- [ Starting Universe Seed: {seed} ] ---")
    
    np.random.seed(seed)
    steps_total = 500
    
    try:
        # Initialize Universe (spec6_true)
        # In Run 6 True, KAPPA_MODE="constant" so everything is 1.0. Delta is 0.0 normally.
        psi = np.random.randn(128, 128) + 1j * np.random.randn(128, 128)
        phi = np.zeros((128, 128))
        kappa = np.ones((128, 128))
        delta = np.zeros((128, 128))
        
        print(f"Evolving {steps_total} steps for seed {seed}...")
        for step in range(steps_total):
            psi, phi = evolve(psi, delta, phi, kappa)
            if step % 100 == 0 and step > 0:
                print(f"  Step {step}/{steps_total}...")
                
        # --- Metrics Calculation ---
        
        # 1. Topological Charge
        phase = np.angle(psi)
        raw_vortices = detect_vortices(phase)
        n_plus = int(np.sum(raw_vortices == 1))
        n_minus = int(np.sum(raw_vortices == -1))
        q_total = n_plus - n_minus
        
        # 2. Average Radius
        mag = np.abs(psi)
        y_indices, x_indices = np.indices(mag.shape)
        center_y, center_x = 64, 64
        distances = np.sqrt((y_indices - center_y)**2 + (x_indices - center_x)**2)
        
        total_mass = np.sum(mag)
        if total_mass > 1e-6:
            avg_radius = np.sum(distances * mag) / total_mass
        else:
            avg_radius = 0.0
            
        phi_center = float(np.abs(phi[64, 64]))
        
        print(f"Seed {seed} finished. R={avg_radius:.2f}, Q={q_total} ({n_plus}+, {n_minus}-)")
        
        # Format: seed, metrics_summary_line
        return seed, f"{seed},{steps_total},{phi_center:.2f},{n_plus},{n_minus},{q_total},{avg_radius:.2f}"
        
    except Exception as e:
        print(f"Error on seed {seed}: {e}")
        return seed, f"{seed},ERROR,ERROR,ERROR,ERROR,ERROR,ERROR"

def main():
    total_seeds = 1000
    seeds = list(range(1, total_seeds + 1))
    
    print(f"============================================================")
    print(f" Starting CPU Batch Scan (Periodic Table of Lineum)         ")
    print(f" Scenario: spec6_true | Target: 500 steps per seed          ")
    print(f" Cores utilized: 1 (Sequential) | Total seeds: {total_seeds} ")
    print(f"============================================================")
    
    start_time = time.time()
    
    results = []
    
    # Ensure output directory exists for live writing
    os.makedirs("output", exist_ok=True)
    
    # Initialize CSV file with header
    out_file = "output/periodic_table_scan_1000.csv"
    with open(out_file, "w") as f:
        f.write("seed,steps,phi_center,n_plus,n_minus,q_total,avg_radius\n")

    for i, seed in enumerate(seeds, 1):
        res_seed, res_line = run_seed_native(seed)
        results.append((res_seed, res_line))
        
        elapsed = time.time() - start_time
        rate = elapsed / i
        eta = (total_seeds - i) * rate
        print(f"Processed {i}/{total_seeds} seeds. (Speed: {1/rate:.2f} seeds/sec) ETA: {eta:.1f}s")
        
        # Write live to CSV
        with open(out_file, "a") as f:
            f.write(f"{res_line}\n")

    end_time = time.time()
    print(f"\nScan completed in {end_time - start_time:.1f} seconds.")
    print(f"Results saved to: {out_file}")

if __name__ == "__main__":
    main()
