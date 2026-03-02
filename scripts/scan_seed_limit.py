import os
import sys
import numpy as np
import argparse
from pathlib import Path
from multiprocessing import Pool, cpu_count
import multiprocessing
import pathlib

# Add repository root so we can import lineum.py directly.
repo_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

import lineum as sim

# Fixed spec6_true constants
STEPS_PER_SEED = 2000
OUTPUT_FILE = repo_root / "output" / "seed_limit_scan_results.csv"
GRID_SIZE = 128
NOISE_AMP = 1e-4
PSI_DIFFUSION = 0.5
PHI_DIFFUSION = 0.1
REACTION_STRENGTH = 1.0
DISSIPATION_RATE = 0.01

def get_spec6_kappa():
    # Island universe (island to constant would be spec7) -> spec6 is constant 0.5
    kappa = np.ones((GRID_SIZE, GRID_SIZE), dtype=np.float64) * 0.5
    return kappa

def detect_vortices(phase: np.ndarray) -> np.ndarray:
    """Vectorized winding-number detection on 2x2 plaquettes."""
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

def run_single_scan(seed):
    """
    Fast headless simulation of Eq-4 for one seed.
    Returns only the final number of topological defects and net charge at step 2000.
    """
    np.random.seed(seed)
    N = GRID_SIZE

    # Prepare output directory
    out_dir = pathlib.Path("output/scans")
    
    # Initialization
    phases = np.random.uniform(0, 2*np.pi, (N, N))
    noise_amp = np.random.uniform(0, NOISE_AMP, (N, N))
    psi = (1.0 + noise_amp) * np.exp(1j * phases)
    phi = np.zeros((N, N), dtype=np.float64)
    kappa = get_spec6_kappa()
    
    # Precompute for evolution
    dt = 0.01

    # Main evolution loop without any I/O (maximum speed)
    for step in range(1, STEPS_PER_SEED + 1):
        # Laplace (diffusion) using np.roll for periodic boundary conditions
        laplace_psi = (np.roll(psi, 1, axis=0) + np.roll(psi, -1, axis=0) +
                       np.roll(psi, 1, axis=1) + np.roll(psi, -1, axis=1) - 4 * psi)
        laplace_phi = (np.roll(phi, 1, axis=0) + np.roll(phi, -1, axis=0) +
                       np.roll(phi, 1, axis=1) + np.roll(phi, -1, axis=1) - 4 * phi)

        amp_sq = np.abs(psi)**2
        
        # Eq-4 Math
        reaction = (1.0 - amp_sq) * psi
        coupling = -1j * phi * psi
        dpsi_dt = kappa * (PSI_DIFFUSION * laplace_psi + REACTION_STRENGTH * reaction + coupling)
        psi += dpsi_dt * dt

        source = amp_sq - 1.0
        dphi_dt = PHI_DIFFUSION * laplace_phi + source - DISSIPATION_RATE * phi
        phi += dphi_dt * dt

    # Scan topology after 2000 steps
    phase = np.angle(psi)
    raw_vortices = detect_vortices(phase)
    
    num_pos = int(np.sum(raw_vortices == 1))
    num_neg = int(np.sum(raw_vortices == -1))
    total_vortices = num_pos + num_neg
    net_charge = num_pos - num_neg
    
    return {
        "seed": seed,
        "total_vortices": total_vortices,
        "net_charge": net_charge,
        "surviving_linons": total_vortices # In this headless mode, each isolated point is a Linon candidate
    }

def main():
    parser = argparse.ArgumentParser(description="Limit/Vacuum topological scan across seeds.")
    parser.add_argument("--seeds", type=int, default=10, help="Number of seeds to scan")
    parser.add_argument("--cores", type=int, default=multiprocessing.cpu_count(), help="Number of CPU cores to use")
    args = parser.parse_args()

    num_seeds = args.seeds
    cores = args.cores

    print("==================================================")
    print(" LINEUM: MASSIVE SEED LIMIT SCAN [Hypothesis A3]  ")
    print(f" Targeting: {num_seeds} seeds | {STEPS_PER_SEED} steps each")
    print(f" Spec: Eq-4 spec6_true (128x128)")
    print("==================================================\n")
    
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    # Multi-processing setup
    print(f"[!] Running massive computation on {cores} CPU cores...")
    
    results = []
    
    seeds = list(range(1, num_seeds + 1))
    
    # Map function to array of seeds using Pool
    with multiprocessing.Pool(processes=cores) as pool:
        # imap_unordered for smooth logging as soon as task is done
        for idx, result in enumerate(pool.imap_unordered(run_single_scan, seeds), 1):
            results.append(result)
            if idx % 10 == 0 or idx == num_seeds:
                print(f"[Progress] Processed {idx}/{num_seeds} seeds ({(idx/num_seeds)*100:.1f}%)", flush=True)

    # Save and analyze data
    print("\n[✓] Processing complete. Saving aggregates...")
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("seed,total_vortices,net_charge,surviving_linons\n")
        for r in sorted(results, key=lambda x: x["seed"]):
            f.write(f"{r['seed']},{r['total_vortices']},{r['net_charge']},{r['surviving_linons']}\n")
            
    vortices_arr = [r["total_vortices"] for r in results]
    limit_max = max(vortices_arr)
    limit_min = min(vortices_arr)
    limit_avg = sum(vortices_arr) / len(vortices_arr)
    
    print("\n================= FINAL REPORT =================")
    print(f" Universes analyzed: {len(results)}")
    print(f" => Average surviving particles: {limit_avg:.2f}")
    print(f" => Absolute MAXIMUM particles (Limit): {limit_max}")
    print(f" => Absolute MINIMUM particles (Vacuum): {limit_min}")
    print(f" Complete data saved to: {OUTPUT_FILE}")
    print("====================================================")

if __name__ == "__main__":
    main()
