import numpy as np
import time
import subprocess
from lineum_core.math import Eq4Config, step_eq4

def get_git_info():
    try:
        commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
        branch = subprocess.check_output(['git', 'rev-parse', '--abbrev-ref', 'HEAD'], text=True).strip()
        return f"{branch}@{commit[:7]}"
    except Exception:
        return "unknown"

def run_hydrogen_sweep(grid_sizes, Z_vals, eps_vals):
    """
    Runs the ground state validation logic for the Hydrogen atom proxy.
    Used by both Pytest (CI) and the Svelte Validation Dashboard (Lab).
    """
    sweeps = list(zip(grid_sizes, Z_vals, eps_vals))
    results = []
    
    # Store the final dense grids for the last sweep to allow Matplotlib rendering
    final_dens = None
    final_V = None
    
    for size, Z, eps in sweeps:
        # Spatial setup
        x = np.linspace(-1, 1, size)
        y = np.linspace(-1, 1, size)
        dx = 2.0 / size
        dV = dx * dx
        
        X, Y = np.meshgrid(x, y)
        R = np.sqrt(X**2 + Y**2)
        
        # Soft Coulomb potential maps directly to the flow scalar `phi`
        V = -Z / np.sqrt(R**2 + eps**2)
        phi_pot = np.clip(-V * 100, 0, 1000)
        
        psi = np.exp(-R**2 / 0.5).astype(np.complex128)
        kappa = np.ones((size, size), dtype=np.float64)
        
        state = {"psi": psi.copy(), "phi": phi_pot.copy(), "kappa": kappa.copy()}
        
        # 1. Imaginary Time Propagation (Diffusion)
        cfg_itp = Eq4Config(dt=0.1, physics_mode_psi="diffusion", use_mode_coupling=False)
        for _ in range(150):
            state = step_eq4(state, cfg_itp)
            N_curr = np.sum(np.abs(state["psi"])**2) * dV
            state["psi"] = state["psi"] / np.sqrt(N_curr)
            
        psi_gs = state["psi"].copy()
        e_dens_gs = np.abs(psi_gs)**2
        
        # Energy Expectation (Exact Lebesgue integral formulation utilizing explicit dx tracking)
        grad_x, grad_y = np.gradient(psi_gs, dx, dx)
        kin_dens = np.abs(grad_x)**2 + np.abs(grad_y)**2
        pot_dens = V * e_dens_gs
        
        E_0 = np.sum(kin_dens) * dV + np.sum(pot_dens) * dV
        
        # 2. Unitary Wave Propagation (Sanity Check)
        cfg_wave = Eq4Config(dt=0.1, physics_mode_psi="wave_baseline", use_mode_coupling=False)
        for _ in range(30):
            state = step_eq4(state, cfg_wave)
            
        e_dens_final = np.abs(state["psi"])**2
        norm_final = np.sum(e_dens_final) * dV # should be 1.0 continuously
        
        grad_x, grad_y = np.gradient(state["psi"], dx, dx)
        kin_end = np.sum(np.abs(grad_x)**2 + np.abs(grad_y)**2) * dV
        pot_end = np.sum(e_dens_final * V) * dV
        E_end = kin_end + pot_end
        
        drift_dE = abs(E_end - E_0) / abs(E_0 + 1e-9)
        
        # Edge metrics
        border_cells = 8 # Fixed physical buffer width invariant of dx grid scaling
        edge_mask = np.ones((size, size), dtype=bool)
        edge_mask[border_cells:-border_cells, border_cells:-border_cells] = False
        
        edge_mass_cells = float(np.sum(e_dens_final[edge_mask]) * dV / norm_final)
        max_edge = float(np.max(e_dens_final[edge_mask]))
        
        r_exp = float(np.sum(R * e_dens_final) * dV / norm_final)
        r2_exp = float(np.sum(R**2 * e_dens_final) * dV / norm_final)
        
        results.append({
            "grid": size, "Z": Z, "eps": eps, 
            "E": float(E_0), "E_end": float(E_end), "drift_dE": float(drift_dE),
            "r": float(r_exp), "r2": float(r2_exp),
            "edge_mass_cells": edge_mass_cells, "max_edge": max_edge
        })
        
        final_dens = e_dens_final
        final_V = V
        
    manifest = {
        "run_id": f"hydro_{int(time.time())}",
        "git": get_git_info(),
        "timestamp": time.time(),
        "config": {
            "physics_mode_psi": "wave_baseline",
            "dt": 0.1,
            "seed": "42"
        }
    }
    
    return {
        "manifest": manifest,
        "results": results,
        "final_dens": final_dens,
        "final_V": final_V
    }

def run_mu_regression_snapshot():
    """
    Runs the Mu memory regression side-by-side snapshot comparison.
    """
    size = 128
    
    def run_reg(kwargs):
        psi = np.zeros((size, size), dtype=np.complex128)
        psi[30:35, 30:35] = 1.0 + 1j
        psi[90:95, 90:95] = 1.0 - 1j
        phi = np.full((size, size), 200.0, dtype=np.float64)
        kappa = np.ones((size, size), dtype=np.float64)
        kappa[60:68, 40:88] = 0.0
        
        state = {"psi": psi, "phi": phi, "kappa": kappa, "mu": np.zeros((size, size), dtype=np.float64)}
        cfg = Eq4Config(**kwargs)
        
        for _ in range(500):
            state["psi"][30:35, 30:35] += (0.1 + 0.1j) * cfg.dt
            state["psi"][90:95, 90:95] += (0.1 - 0.1j) * cfg.dt
            state = step_eq4(state, cfg)
            
        return state["psi"], state["mu"]

    diff_args = {"dt": 0.1, "physics_mode_psi": "diffusion", "use_mode_coupling": True, "use_mu": True}
    wave_args = {"dt": 0.1, "physics_mode_psi": "wave_projected_soft", "wave_lpf_enabled": True, "use_mode_coupling": True, "use_mu": True}
    
    psi_diff, mu_diff = run_reg(diff_args)
    psi_wave, mu_wave = run_reg(wave_args)
    
    manifest = {
        "run_id": f"mureg_{int(time.time())}",
        "git": get_git_info(),
        "timestamp": time.time(),
        "config": {
            "diffusion": diff_args,
            "wave": wave_args
        }
    }
    
    return {
        "manifest": manifest,
        "psi_diff": psi_diff, "mu_diff": mu_diff,
        "psi_wave": psi_wave, "mu_wave": mu_wave
    }
