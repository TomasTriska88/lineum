from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict
import asyncio
import time
import numpy as np
import io
import base64
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')))
from lineum_core.math import Eq4Config, step_eq4
from scripts.validation_core import run_hydrogen_sweep, run_mu_regression_snapshot

router = APIRouter()

@router.websocket("/hydrogen")
async def ws_hydrogen(websocket: WebSocket):
    """
    Streams the Hydrogen 2D Ground State Validation (Wave Core).
    Phase A: Diffusion cooling (Imaginary time)
    Phase B: Unitary wave propagation 
    """
    await websocket.accept()
    
    size = 64
    Z = 2.0
    eps = 0.1
    
    x = np.linspace(-1, 1, size)
    y = np.linspace(-1, 1, size)
    X, Y = np.meshgrid(x, y)
    R = np.sqrt(X**2 + Y**2)
    
    V = -Z / np.sqrt(R**2 + eps**2)
    phi_pot = np.clip(-V * 100, 0, 1000)
    
    psi = np.exp(-R**2 / 0.5).astype(np.complex128)
    kappa = np.ones((size, size), dtype=np.float64)
    state = {"psi": psi.copy(), "phi": phi_pot.copy(), "kappa": kappa.copy()}
    
    cfg_itp = Eq4Config(dt=0.1, physics_mode_psi="diffusion", use_mode_coupling=False)
    cfg_wave = Eq4Config(dt=0.1, physics_mode_psi="wave_baseline", use_mode_coupling=False)
    
    start_time = time.time()
    MAX_TIME = 30.0
    
    try:
        # Phase A: Cooling
        for step in range(300):
            if time.time() - start_time > MAX_TIME: break
            
            state = step_eq4(state, cfg_itp)
            N_curr = np.sum(np.abs(state["psi"])**2)
            state["psi"] = state["psi"] / np.sqrt(N_curr)
            
            if step % 5 == 0:
                dens = np.abs(state["psi"])**2
                log_dens = np.log10(dens + 1e-12)
                # Normalize log_dens for canvas rendering (0-255 roughly)
                min_l, max_l = np.min(log_dens), np.max(log_dens)
                norm_dens = (log_dens - min_l) / (max_l - min_l + 1e-9)
                
                await websocket.send_json({
                    "phase": "Cooling (Imaginary Time)",
                    "step": step,
                    "max_steps": 300,
                    "n_t": N_curr,
                    "dens_flat": norm_dens.flatten().tolist()
                })
                await asyncio.sleep(0.01)

        # Phase B: Wave Propagation
        for step in range(100):
            if time.time() - start_time > MAX_TIME: break
            
            state = step_eq4(state, cfg_wave)
            
            if step % 2 == 0:
                dens = np.abs(state["psi"])**2
                
                # Calculate edge mass
                border = int(size * 0.1)
                edge_mask = np.ones((size, size), dtype=bool)
                edge_mask[border:-border, border:-border] = False
                edge_mass = np.sum(dens[edge_mask]) / np.sum(dens)
                
                log_dens = np.log10(dens + 1e-12)
                min_l, max_l = np.min(log_dens), np.max(log_dens)
                norm_dens = (log_dens - min_l) / (max_l - min_l + 1e-9)
                
                N_curr = np.sum(dens)
                
                await websocket.send_json({
                    "phase": "Unitary Wave Validation",
                    "step": step,
                    "max_steps": 100,
                    "n_t": N_curr,
                    "edge_mass": edge_mass,
                    "dens_flat": norm_dens.flatten().tolist()
                })
                await asyncio.sleep(0.01)
                
        await websocket.close()
    except WebSocketDisconnect:
        print("Hydrogen lab client disconnected.")
    except Exception as e:
        print(f"Hydrogen lab error: {e}")

@router.websocket("/regression")
async def ws_regression(websocket: WebSocket):
    """
    Streams the Mu Memory regression test comparing Diffusion and Wave side-by-side.
    """
    await websocket.accept()
    
    size = 64 # scaled down for real-time web socket performance
    
    def setup_state():
        x = np.linspace(-1, 1, size)
        y = np.linspace(-1, 1, size)
        X, Y = np.meshgrid(x, y)
        
        psi = np.zeros((size, size), dtype=np.complex128)
        phi = np.full((size, size), 200.0, dtype=np.float64)
        kappa = np.ones((size, size), dtype=np.float64)
        
        # Central obstacle
        kappa[30:34, 20:44] = 0.0
        
        return {
            "psi": psi,
            "phi": phi,
            "kappa": kappa,
            "mu": np.zeros((size, size), dtype=np.float64)
        }
    
    state_diff = setup_state()
    state_wave = setup_state()
    
    cfg_diff = Eq4Config(dt=0.1, physics_mode_psi="diffusion", use_mode_coupling=True, use_mu=True)
    cfg_wave = Eq4Config(dt=0.1, physics_mode_psi="wave_projected_soft", wave_lpf_enabled=True, use_mode_coupling=True, use_mu=True)
    
    start_time = time.time()
    MAX_TIME = 60.0 # longer timeout for regression
    
    try:
        cap_val = cfg_diff.mu_cap
        
        for step in range(1000):
            if time.time() - start_time > MAX_TIME: break
            
            # Driving forces
            pulse_a = (0.1 + 0.1j) * cfg_diff.dt
            pulse_b = (0.1 - 0.1j) * cfg_diff.dt
            
            for s in [state_diff, state_wave]:
                s["psi"][15:18, 15:18] += pulse_a
                s["psi"][45:48, 45:48] += pulse_b
                
            state_diff = step_eq4(state_diff, cfg_diff)
            state_wave = step_eq4(state_wave, cfg_wave)
            
            if step % 10 == 0:
                mu_diff = state_diff["mu"]
                mu_wave = state_wave["mu"]
                
                # Normalize 0..cap_val to 0..1 for UI
                norm_mu_diff = np.clip(mu_diff / cap_val, 0.0, 1.0).flatten().tolist()
                norm_mu_wave = np.clip(mu_wave / cap_val, 0.0, 1.0).flatten().tolist()
                
                psi_diff_norm = np.clip(np.abs(state_diff["psi"])**2 / 5.0, 0.0, 1.0).flatten().tolist()
                psi_wave_norm = np.clip(np.abs(state_wave["psi"])**2 / 5.0, 0.0, 1.0).flatten().tolist()
                
                await websocket.send_json({
                    "step": step,
                    "max_steps": 1000,
                    "diff_mu": norm_mu_diff,
                    "wave_mu": norm_mu_wave,
                    "diff_psi": psi_diff_norm,
                    "wave_psi": psi_wave_norm,
                    "diff_max_mu": float(np.max(mu_diff)),
                    "wave_max_mu": float(np.max(mu_wave)),
                    "diff_n": float(state_diff["telemetry"]["N_t"]),
                    "wave_n": float(state_wave["telemetry"]["N_t"])
                })
                await asyncio.sleep(0.01)
                
        await websocket.close()
    except WebSocketDisconnect:
        print("Regression lab client disconnected.")
    except Exception as e:
        print(f"Regression lab error: {e}")

@router.get("/hydrogen/sweep")
async def get_hydrogen_sweep():
    """ Runs the validation sweep across multi-grids dynamically to ensure the current core math breaks nothing """
    sweeps = [
        (64, 1.0, 0.1),
        (64, 2.0, 0.1),
        (64, 2.0, 0.05),
        (128, 2.0, 0.1),
        (128, 4.0, 0.1)
    ]
    
    grid_sizes = [s[0] for s in sweeps]
    Z_vals = [s[1] for s in sweeps]
    eps_vals = [s[2] for s in sweeps]
    
    val_data = run_hydrogen_sweep(grid_sizes, Z_vals, eps_vals)
    manifest = val_data["manifest"]
    results = val_data["results"]
    dens = val_data["final_dens"]
    V = val_data["final_V"]
    
    # Generate matplotlib plot using last result
    log_dens = np.log10(dens + 1e-12)
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8, 3))
    im1 = ax1.imshow(V, cmap='viridis')
    ax1.set_title(f"Soft Coulomb V(r)\nZ={Z_vals[-1]}, eps={eps_vals[-1]}")
    fig.colorbar(im1, ax=ax1)
    
    im2 = ax2.imshow(log_dens, cmap='magma', vmin=np.max(log_dens)-6, vmax=np.max(log_dens))
    ax2.set_title(f"Log2 Ground State\nEdge Mass: {results[-1]['edge_mass_cells']:.2e}")
    fig.colorbar(im2, ax=ax2)
    
    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=100, bbox_inches="tight")
    plt.close()
    buf.seek(0)
    b64 = base64.b64encode(buf.read()).decode("utf-8")
    
    return {"manifest": manifest, "results": results, "image_b64": b64}

@router.get("/regression/snapshot")
async def get_regression_snapshot():
    val_data = run_mu_regression_snapshot()
    manifest = val_data["manifest"]
    psi_diff = val_data["psi_diff"]
    mu_diff = val_data["mu_diff"]
    psi_wave = val_data["psi_wave"]
    mu_wave = val_data["mu_wave"]
    
    fig, axes = plt.subplots(2, 2, figsize=(8, 7))
    axes[0, 0].imshow(np.abs(psi_diff)**2, cmap='magma', vmin=0); axes[0, 0].set_title("Diffusion |psi|^2")
    axes[0, 1].imshow(mu_diff, cmap='inferno', vmin=0, vmax=10.0); axes[0, 1].set_title(f"Diffusion Mu\nMax: {np.max(mu_diff):.2f}")
    axes[1, 0].imshow(np.abs(psi_wave)**2, cmap='magma', vmin=0); axes[1, 0].set_title("Wave |psi|^2")
    axes[1, 1].imshow(mu_wave, cmap='inferno', vmin=0, vmax=10.0); axes[1, 1].set_title(f"Wave Mu\nMax: {np.max(mu_wave):.2f}")
    
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=100)
    plt.close()
    buf.seek(0)
    b64 = base64.b64encode(buf.read()).decode("utf-8")
    
    return {"manifest": manifest, "image_b64": b64}
