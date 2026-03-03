import numpy as np
import scipy.ndimage
import json
import os
import sys

# Add core to path so we can import it and its variables
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import lineum_core.math as lmath

# Ensure CPU mode for deterministic cross-seed testing unless specified
USE_GPU = lmath.USE_PYTORCH

# --- Config ---
N_SEEDS = 30
TICKS_PER_RUN = 300
GRID_SIZES = [64, 128] # We sweep this for the normalization test
DT_SWEEP = [1.0, 0.5]  # Testing time integrations

def generate_terrain(seed, size):
    np.random.seed(seed)
    kappa = np.random.rand(size, size) * 0.5 + 0.1
    kappa = scipy.ndimage.gaussian_filter(kappa, sigma=int(size/32))
    return kappa

def calculate_novelty(phi, prev_phi):
    mag_new = np.sum(np.abs(phi))
    mag_old = np.sum(np.abs(prev_phi))
    # True scale-invariant novelty must not be sensitive to overall magnitude shifts
    # Using relative percentage change
    return np.abs(mag_new - mag_old) / (mag_old + 1e-6)

def run_simulation(seed, size=64, dt=1.0, mode="A", coupling_strength=0.001):
    """
    mode A: Old Baseline (USE_MODE_COUPLING = False, Use Mu = False)
    mode B: Physics Only (USE_MODE_COUPLING = True, Use Mu = False)
    mode C: Physics + Mu (USE_MODE_COUPLING = True, Use Mu = True)
    """
    lmath.DT = dt
    if mode == "A":
        lmath.USE_MODE_COUPLING = False
        use_mu = False
    elif mode == "B":
        lmath.USE_MODE_COUPLING = True
        lmath.MODE_COUPLING_STRENGTH = coupling_strength
        use_mu = False
    elif mode == "C":
        lmath.USE_MODE_COUPLING = True
        lmath.MODE_COUPLING_STRENGTH = coupling_strength
        use_mu = True
        
    kappa = generate_terrain(seed, size)
    psi = np.zeros((size, size), dtype=np.complex128)
    psi[size//2-2:size//2+3, size//2-2:size//2+3] += 10.0 # Initial burst
    
    phi = np.zeros((size, size), dtype=np.float64)
    mu = np.full((size, size), 0.1, dtype=np.float64) if use_mu else None
    delta = np.zeros((size, size), dtype=np.float64)
    
    metrics = {
        "energy": [],
        "novelty": [],
        "max_grad_phi": [],
        "max_grad_psi": []
    }
    
    frozen = False
    exploded = False
    prev_phi = phi.copy()
    
    for t in range(int(TICKS_PER_RUN / dt)):
        if use_mu:
           delta = 1.0 + mu
           
        psi, phi = lmath.evolve(psi, delta, phi, kappa)
        
        if use_mu:
            psi_mag_sq = np.abs(psi)**2
            mu += (0.005 * psi_mag_sq - 0.0001 * (mu - 0.1)) * lmath.DT
            mu = np.clip(mu, 0.001, 10.0)
            
        # Semantic Injection
        if t % int(50/dt) == 0:
            psi[size//2-2:size//2+3, size//2-2:size//2+3] += 5.0

        # Subsample logging to save RAM (10 ticks normalized space)
        if t % max(1, int(10 / dt)) == 0:
            e_t = float(np.sum(np.abs(psi)**2))
            nov_t = float(calculate_novelty(phi, prev_phi))
            
            # Gradients
            g_phi_x, g_phi_y = np.gradient(phi)
            g_psi_x, g_psi_y = np.gradient(np.abs(psi))
            mgp = float(np.max(np.sqrt(g_phi_x**2 + g_phi_y**2)))
            mgps = float(np.max(np.sqrt(g_psi_x**2 + g_psi_y**2)))
            
            metrics["energy"].append(e_t)
            metrics["novelty"].append(nov_t)
            metrics["max_grad_phi"].append(mgp)
            metrics["max_grad_psi"].append(mgps)
            
            prev_phi = phi.copy()

            if np.isnan(e_t) or e_t > 1e12 or mgps > lmath.GRAD_CAP * 0.99:
                exploded = True
                break

    if not exploded and len(metrics["novelty"]) > 5:
        if np.mean(metrics["novelty"][-5:]) < 1e-4:
            frozen = True
            
    return {"metrics": metrics, "exploded": exploded, "frozen": frozen}

def main():
    print("Starting Phase 29 Rigor Sweep for Mode-Coupling...")
    results = {"A": [], "B": [], "C": []}
    
    print(f"\\n--- Running N={N_SEEDS} Multi-Seed Ablation (Size 64, dt=1.0) ---")
    for seed in range(N_SEEDS):
        res_a = run_simulation(seed, mode="A")
        res_b = run_simulation(seed, mode="B")
        res_c = run_simulation(seed, mode="C")
        
        results["A"].append(res_a)
        results["B"].append(res_b)
        results["C"].append(res_c)
        
        sys.stdout.write(f"\\rSeed {seed+1}/{N_SEEDS} Completed.")
        sys.stdout.flush()
    print("\\n\\nAggregating Main Sweep...")
    
    summary = {}
    for mode in ["A", "B", "C"]:
        explodes = sum(1 for r in results[mode] if r["exploded"])
        freezes = sum(1 for r in results[mode] if r["frozen"])
        
        # Average time series curves across seeds
        avg_energy = np.mean([r["metrics"]["energy"] for r in results[mode] if not r["exploded"]], axis=0).tolist()
        avg_nov = np.mean([r["metrics"]["novelty"] for r in results[mode] if not r["exploded"]], axis=0).tolist()
        peak_g_phi = np.max([np.max(r["metrics"]["max_grad_phi"]) for r in results[mode] if not r["exploded"]])
        peak_g_psi = np.max([np.max(r["metrics"]["max_grad_psi"]) for r in results[mode] if not r["exploded"]])
        
        summary[mode] = {
            "explosions_count": explodes,
            "freezes_count": freezes,
            "peak_grad_phi": float(peak_g_phi),
            "peak_grad_psi": float(peak_g_psi),
            "final_mean_energy": avg_energy[-1] if avg_energy else 0.0,
            "final_mean_novelty": avg_nov[-1] if avg_nov else 0.0
        }
        
        print(f"Mode {mode} -> Explosions: {explodes} | Freezes: {freezes} | Final Novelty: {summary[mode]['final_mean_novelty']:.5f} | Peak ∇ψ: {peak_g_psi:.2f}")

    print("\\n--- Running Grid & dt Normalization Checks (Seed 42) ---")
    norm_res = {}
    
    # 1. Base 64x64, dt=1.0
    r_base = run_simulation(42, size=64, dt=1.0, mode="B")
    
    # 2. Rescaled dt=0.5
    r_dt = run_simulation(42, size=64, dt=0.5, mode="B")
    
    # 3. Rescaled space 128x128
    r_space = run_simulation(42, size=128, dt=1.0, mode="B")
    
    nov_base = np.mean(r_base["metrics"]["novelty"][-5:])
    nov_dt = np.mean(r_dt["metrics"]["novelty"][-10:])    # Twice as many steps, take double tail
    nov_space = np.mean(r_space["metrics"]["novelty"][-5:])
    
    print(f"Novelty Normalization Checks:")
    print(f"  Base (64, dt=1): {nov_base:.5f}")
    print(f"  Speed (64, dt=0.5): {nov_dt:.5f}")
    print(f"  Space (128, dt=1): {nov_space:.5f}")
    
    with open("rigor_mode_coupling.json", "w") as f:
        json.dump({"summary": summary, "normalization": {"base": nov_base, "dt_half": nov_dt, "space_double": nov_space}}, f, indent=2)

if __name__ == "__main__":
    main()
