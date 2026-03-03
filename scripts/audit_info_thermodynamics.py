import numpy as np
import scipy.ndimage
import json
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import lineum_core.math as lmath

# Configurations
GRID_SIZE = 64
HORIZONS = [3000, 10000]

def generate_terrain(seed, size):
    np.random.seed(seed)
    kappa = np.random.rand(size, size) * 0.5 + 0.1
    kappa = scipy.ndimage.gaussian_filter(kappa, sigma=2.0)
    return kappa

def run_thermodynamic_audit(ticks, mode="B", eta=0.005, rho=0.0001):
    """
    mode B: Baseline Eq-4' (RAM only)
    mode C: Eq-4' + mu (HDD track)
    """
    lmath.DT = 1.0
    lmath.USE_MODE_COUPLING = True
    lmath.MODE_COUPLING_STRENGTH = 0.001
    
    use_mu = (mode == "C")
    kappa = generate_terrain(42, GRID_SIZE)
    
    psi = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.complex128)
    phi = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.float64)
    mu = np.full((GRID_SIZE, GRID_SIZE), 0.1, dtype=np.float64) if use_mu else None
    
    total_energy_integral = 0.0
    rtb_maes = []
    
    # 3-Phase Injection Schedule (30% Learn Basin, 30% Chaos, 40% Recall)
    p1 = int(ticks * 0.3)
    p2 = int(ticks * 0.6)
    
    phi_basin_learned = None
    
    # Tracking moving average of energy to detect insidious growth
    energy_sliding_window = []
    avg_energy_curve = []
    
    for t in range(ticks):
        delta = 1.0 + mu if use_mu else np.zeros_like(phi)
        psi, phi = lmath.evolve(psi, delta, phi, kappa)
        
        if use_mu:
            psi_mag_sq = np.abs(psi)**2
            mu += (eta * psi_mag_sq - rho * (mu - 0.1)) * lmath.DT
            mu = np.clip(mu, 0.001, 10.0)
            
        # Standard injections
        if t % 50 == 0:
            if t < p1 or t >= p2:
                # Core basin injection (Task A)
                psi[GRID_SIZE//2-2:GRID_SIZE//2+3, GRID_SIZE//2-2:GRID_SIZE//2+3] += 5.0
            else:
                # Chaos injections (Task B)
                np.random.seed(t) # deterministic chaos
                rx, ry = np.random.randint(10, GRID_SIZE-10, 2)
                psi[rx-2:rx+3, ry-2:ry+3] += 5.0
                
        e_t = float(np.sum(np.abs(psi)**2))
        total_energy_integral += e_t
        
        energy_sliding_window.append(e_t)
        if len(energy_sliding_window) > 100:
            energy_sliding_window.pop(0)
            
        if t % 100 == 0:
            avg_energy_curve.append(np.mean(energy_sliding_window))
            
        if t == p1 - 1:
            phi_basin_learned = phi.copy()
            
        if t >= p2 and t % 50 == 0:
            mae = np.mean(np.abs(phi - phi_basin_learned))
            rtb_maes.append(float(mae))
            
    return {
        "integral_energy": total_energy_integral,
        "energy_per_tick": total_energy_integral / ticks,
        "rtb_score": float(np.mean(rtb_maes)),
        "final_topo_phi": float(np.sum(phi)),
        "final_topo_mu": float(np.sum(mu)) if use_mu else 0.0,
        "energy_curve_start": float(np.mean(avg_energy_curve[10:20])),
        "energy_curve_end": float(np.mean(avg_energy_curve[-10:]))
    }

print("Running E=mc^2=Information Final Rigor Audit...")
results = {}

for horizon in HORIZONS:
    print(f"\\n[ HORIZON: {horizon} TICKS ]")
    # 1. Baseline
    res_B = run_thermodynamic_audit(horizon, mode="B")
    
    # 2. V2 Track sweeps (eta, rho)
    sweeps = [
        (0.005, 0.0001, "std"),
        (0.01, 0.0001, "high_eta"),
        (0.005, 0.001, "high_rho")
    ]
    
    horizon_data = {"B": res_B, "C_sweeps": {}}
    print(f"  Mode B -> Energy Integral: {res_B['integral_energy']:.2e} | RTB: {res_B['rtb_score']:.2f}")
    
    for eta, rho, label in sweeps:
        res_C = run_thermodynamic_audit(horizon, mode="C", eta=eta, rho=rho)
        horizon_data["C_sweeps"][label] = res_C
        growth = (res_C["energy_curve_end"] - res_C["energy_curve_start"]) / res_C["energy_curve_start"] * 100
        print(f"  Mode C ({label}) -> Energy Integral: {res_C['integral_energy']:.2e} | RTB: {res_C['rtb_score']:.2f} | Growth: {growth:.2f}%")
        
    results[f"horizon_{horizon}"] = horizon_data

with open("audit_info_thermodynamics.json", "w") as f:
    json.dump(results, f, indent=2)

print("\\nAudit complete. Artifact saved.")
