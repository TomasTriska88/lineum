import os
import sys
import numpy as np
import argparse
from pathlib import Path
from multiprocessing import Pool, cpu_count

# Přidat kořen repozitáře, abychom mohli importovat lineum.py přímo
repo_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(repo_root))

from scipy.ndimage import gaussian_filter

# Pevné spec6_true konstanty
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

def simulate_seed(seed):
    """
    Rychlá headless simulace Eq-4 pro jeden seed.
    Vrací pouze finální počet topologických defektů a net charge v kroku 2000.
    """
    np.random.seed(seed)
    N = GRID_SIZE

    # Inicializace
    phases = np.random.uniform(0, 2*np.pi, (N, N))
    noise_amp = np.random.uniform(0, NOISE_AMP, (N, N))
    psi = (1.0 + noise_amp) * np.exp(1j * phases)
    phi = np.zeros((N, N), dtype=np.float64)
    kappa = get_spec6_kappa()
    
    # Precompute pro evoluci
    dt = 0.01

    # Hlavní smyčka evoluce bez jakéhokoliv I/O (maximální rychlost)
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

    # Po 2000 krocích naskenujeme topologii
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
    parser = argparse.ArgumentParser(description="Massive headless topological limit scan.")
    parser.add_argument("--seeds", type=int, default=10, help="Počet seedů ke skenování")
    args = parser.parse_args()

    num_seeds = args.seeds

    print("==================================================")
    print(" LINEUM: MASSIVE SEED LIMIT SCAN [Hypothesis A3]  ")
    print(f" Targeting: {num_seeds} seeds | {STEPS_PER_SEED} steps each")
    print(f" Spec: Eq-4 spec6_true (128x128)")
    print("==================================================\n")
    
    # Připravit výstupní adresář
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    # Multi-processing setup
    cores = max(1, cpu_count() - 1)
    print(f"[!] Spouštím masivní výpočet na {cores} CPU jádrech...")
    
    results = []
    
    # Pomocí Pool namapujeme funkci na pole seedů
    with Pool(processes=cores) as pool:
        seeds_to_run = list(range(1, num_seeds + 1))
        # Imap_unordered pro plynulé logování jakmile je úkol hotový
        for idx, res in enumerate(pool.imap_unordered(simulate_seed, seeds_to_run), 1):
            results.append(res)
            if idx % 10 == 0 or idx == num_seeds:
                print(f"[Progress] Zpracováno {idx}/{num_seeds} seedů ({(idx/num_seeds)*100:.1f}%)", flush=True)

    # Uložit a analyzovat data
    print("\n[✓] Zpracování dokončeno. Ukládám agregáty...")
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("seed,total_vortices,net_charge,surviving_linons\n")
        for r in sorted(results, key=lambda x: x["seed"]):
            f.write(f"{r['seed']},{r['total_vortices']},{r['net_charge']},{r['surviving_linons']}\n")
            
    vortices_arr = [r["total_vortices"] for r in results]
    limit_max = max(vortices_arr)
    limit_min = min(vortices_arr)
    limit_avg = sum(vortices_arr) / len(vortices_arr)
    
    print("\n================= ZÁVĚREČNÁ ZPRÁVA =================")
    print(f" Analyzováno vesmírů: {len(results)}")
    print(f" => Průměrný počet přeživších částic: {limit_avg:.2f}")
    print(f" => Absolutní MAXIMUM částic (Limit): {limit_max}")
    print(f" => Absolutní MINIMUM částic (Vacuum): {limit_min}")
    print(f" Kompletní data uložena do: {OUTPUT_FILE}")
    print("====================================================")

if __name__ == "__main__":
    main()
