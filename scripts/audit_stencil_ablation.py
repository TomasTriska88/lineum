import numpy as np
import scipy.ndimage
import json
import os
import sys

# Add core to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import lineum_core.math as lmath
from lineum_core.math import Eq4Config, step_eq4

# Fix seed and config
np.random.seed(42)
GRID_SIZE = 64
HORIZON = 500

def initialize_fields():
    psi = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.complex128)
    phi = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.float64)
    kappa = np.ones((GRID_SIZE, GRID_SIZE), dtype=np.float64)
    
    # Create interesting topology
    kappa[30:35, 10:50] = 0.01
    kappa[10:50, 30:35] = 0.01
    kappa = scipy.ndimage.gaussian_filter(kappa, sigma=2.0)
    kappa = np.clip(kappa, 0.05, 1.0)
    mu = np.zeros_like(phi)
    
    return {"psi": psi, "phi": phi, "kappa": kappa, "mu": mu}

def generate_sentence_delta(seed_val):
    rng = np.random.RandomState(seed_val)
    d = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.float64)
    for _ in range(5):
        cx, cy = rng.randint(15, GRID_SIZE-15, size=2)
        d[cx-2:cx+3, cy-2:cy+3] += 5.0
    return scipy.ndimage.gaussian_filter(d, sigma=1.5)

def run_ablation(stencil_name):
    print(f"\\n--- Running Ablation for {stencil_name} ---")
    state = initialize_fields()
    cfg = Eq4Config(
        dt=1.0,
        use_mode_coupling=True,
        mode_coupling_strength=0.001,
        use_mu=True,
        stencil_type=stencil_name
    )
    
    metrics = {
        "max_grad_phi": 0.0,
        "max_grad_psi": 0.0,
        "energy_integral": 0.0,
        "novelties": []
    }
    
    last_phi = np.copy(state["phi"])
    
    for t in range(HORIZON):
        if t % 50 == 0:
            state["delta"] = generate_sentence_delta(t)
        else:
            state["delta"] = np.zeros_like(state["phi"])
            
        state = step_eq4(state, cfg)
        
        # Metrics
        p_amp = np.abs(state["psi"])
        g_px, g_py = np.gradient(p_amp)
        g_fx, g_fy = np.gradient(state["phi"])
        
        m_g_p = np.max(np.sqrt(g_px**2 + g_py**2))
        m_g_f = np.max(np.sqrt(g_fx**2 + g_fy**2))
        
        metrics["max_grad_psi"] = max(metrics["max_grad_psi"], float(m_g_p))
        metrics["max_grad_phi"] = max(metrics["max_grad_phi"], float(m_g_f))
        
        metrics["energy_integral"] += float(np.sum(p_amp**2))
        
        novelty = np.mean(np.abs(state["phi"] - last_phi))
        metrics["novelties"].append(float(novelty))
        last_phi = np.copy(state["phi"])
        
        if t % 100 == 0:
            print(f"Tick {t:03d} | E: {np.sum(p_amp**2):.2f} | Novelty: {novelty:.4f}")
            
    metrics["final_mean_novelty"] = float(np.mean(metrics["novelties"][-100:]))
    metrics["final_mu_mass"] = float(np.sum(state["mu"]))
    return metrics, state["phi"]

m4, phi4 = run_ablation("LAP4")
m8, phi8 = run_ablation("LAP8")

diff_mae = np.mean(np.abs(phi4 - phi8))
diff_max = np.max(np.abs(phi4 - phi8))

report = {
    "ablation": {
        "LAP4": m4,
        "LAP8": m8
    },
    "grid_dependency_stats": {
        "final_phi_MAE": float(diff_mae),
        "final_phi_MAX_diff": float(diff_max), 
        "energy_diff_pct": float(abs(m4["energy_integral"] - m8["energy_integral"]) / m4["energy_integral"] * 100),
        "novelty_diff_pct": float(abs(m4["final_mean_novelty"] - m8["final_mean_novelty"]) / m4["final_mean_novelty"] * 100)
    }
}

with open("audit_stencil_ablation.json", "w") as f:
    json.dump(report, f, indent=4)
    
print("\\n=== ABLATION COMPLETE ===")
print(f"LAP4 Energy Integral: {m4['energy_integral']:.2e}")
print(f"LAP8 Energy Integral: {m8['energy_integral']:.2e}")
print(f"Energy difference: {report['grid_dependency_stats']['energy_diff_pct']:.2f}%")
print(f"Novelty difference: {report['grid_dependency_stats']['novelty_diff_pct']:.2f}%")
print(f"Final topology MAE (Grid Dependency): {diff_mae:.4f}")
if diff_mae > 0.5:
    print("CONCLUSION: Strong grid dependency detected. LAP8 materially altered emergence.")
elif diff_mae > 0.05:
    print("CONCLUSION: Mild grid dependency. Structures mostly equivalent, slightly smoothed artifacts.")
else:
    print("CONCLUSION: Topology is mostly invariant to discretization stencils.")
