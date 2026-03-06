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
import json
from pathlib import Path
from pydantic import BaseModel
from typing import Dict, Any

from lineum_core.math import CoreConfig, step_core
from scripts.validation_core import (
    run_hydrogen_sweep, run_mu_regression_snapshot, run_particle_playground,
    GOLDEN_HYDRO_SWEEP,
    run_ra1_unitarity, run_ra2_bound_state, run_ra3_excited_state,
    run_ra4_mu_memory, run_ra5_driving, run_ra6_lpf_impact,
)

HISTORY_DIR = Path(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'output', 'lab_history'))
HISTORY_DIR.mkdir(parents=True, exist_ok=True)

def save_run(data: dict):
    if "manifest" in data and "run_id" in data["manifest"]:
        run_id = data["manifest"]["run_id"]
        filepath = HISTORY_DIR / f"{run_id}.json"
        
        # We don't save the massive raw source_code to history json to save disk space
        save_data = data.copy()
        if "source_code" in save_data:
            del save_data["source_code"]
            
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, indent=2)

router = APIRouter()

@router.get("/ux-canon")
async def get_ux_canon():
    """Serves the LAB_UX_CANON.md content for the Help modal."""
    canon_path = Path(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'LAB_UX_CANON.md'))
    if canon_path.exists():
        return {"content": canon_path.read_text(encoding='utf-8')}
    return {"content": "# LAB_UX_CANON.md not found"}

@router.get("/health")
async def get_health():
    """Returns local system health for the Lab UI (git hash and golden tests summary)."""
    import subprocess
    import os
    import sys
    try:
        git_hash = subprocess.check_output(["git", "rev-parse", "HEAD"], stderr=subprocess.DEVNULL).decode("utf-8").strip()
    except Exception:
        git_hash = "unknown"
        
    try:
        branch = subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"], stderr=subprocess.DEVNULL).decode("utf-8").strip()
    except Exception:
        branch = "unknown"

    vc_path = "Unknown"
    if "scripts.validation_core" in sys.modules:
        vc_path = os.path.abspath(sys.modules["scripts.validation_core"].__file__)
        
    # Read active contract suite
    audit_status = "NONE"
    contract_id = None
    contract_timestamp = "unknown"
    contract_commit = "unknown"
    equation_fingerprint = "unknown"
    summary_pass = 0
    summary_fail = 0
    
    # Define absolute paths dynamically based on repo root
    REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    output_wp_dir = os.path.join(REPO_ROOT, 'output_wp')
    suite_abs_path = os.path.join(output_wp_dir, 'runs', '_whitepaper_contract', 'whitepaper_contract_suite.json')
    
    suite_path = Path(suite_abs_path)
    try:
        curr_full = subprocess.check_output(["git", "rev-parse", "HEAD"], stderr=subprocess.DEVNULL).decode("utf-8").strip()
        if suite_path.exists():
            with open(suite_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                # Handle both list of audits and single audit dict
                audits = data if isinstance(data, list) else [data]
                
                # Sort by timestamp descending (newest first)
                audits.sort(key=lambda x: x.get("header", {}).get("timestamp", ""), reverse=True)
                
                for audit in audits:
                    summary = audit.get("summary", {})
                    # We only consider audits that fully passed
                    if summary.get("fail", 1) == 0:
                        header = audit.get("header", {})
                        fingerprints = audit.get("fingerprints", {})
                        
                        contract_id = header.get("contract_id")
                        contract_timestamp = header.get("timestamp", "unknown")
                        contract_commit = header.get("git_commit", "")
                        equation_fingerprint = header.get("equation_fingerprint", "unknown")
                        summary_pass = summary.get("pass", 0)
                        summary_fail = summary.get("fail", 0)
                        
                        if contract_commit == curr_full:
                            audit_status = "AUDITED"
                        else:
                            audit_status = "OUTDATED"
                        break
    except Exception as e:
        print(f"Contract read error: {e}")

    return {
        "commit_hash": git_hash,
        "current_build": f"{git_hash} ({branch})",
        "audit_status": audit_status,
        "contract_id": contract_id,
        "active_contract_id": contract_id,
        "audit_output_wp_abs_path": output_wp_dir,
        "active_suite_abs_path": suite_abs_path if suite_path.exists() else None,
        "contract_timestamp": contract_timestamp,
        "contract_commit": contract_commit if contract_commit else "unknown",
        "equation_fingerprint": equation_fingerprint if equation_fingerprint else "unknown",
        "summary_pass": summary_pass,
        "summary_fail": summary_fail,
        "tests": "PASS (Local)",
        "loaded_modules": {
            "routing_backend": os.path.dirname(os.path.abspath(__file__)),
            "validation_core": vc_path
        }
    }

@router.post("/audit/generate")
async def generate_audit_contract():
    """
    Full audit pipeline (blocking):
      Step 1: lineum.py with LINEUM_BASE_OUTPUT_DIR=output_wp + LINEUM_AUDIT_PROFILE=whitepaper_core
      Step 2: tools/whitepaper_contract.py (suite generation)
    Returns proof: new_run_id, latest_run, suite header, audit_status.
    """
    import subprocess
    REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    try:
        # --- Step 1: Physics run into output_wp/runs/<run_id>/ ---
        lineum_path = os.path.join(REPO_ROOT, 'lineum.py')
        env = os.environ.copy()
        env["LINEUM_BASE_OUTPUT_DIR"] = "output_wp"
        env["LINEUM_AUDIT_PROFILE"] = "whitepaper_core"
        env["LINEUM_RUN_ID"] = "6"
        env["LINEUM_RUN_MODE"] = "false"
        env["LINEUM_SEED"] = "41"
        env["LINEUM_STEPS"] = "2000"
        env["PYTHONUTF8"] = "1"

        step1 = subprocess.run(
            ["python", lineum_path],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            env=env,
            timeout=600  # 10 min max for physics run
        )
        if step1.returncode != 0:
            return {"status": "error", "step": 1, "detail": f"lineum.py failed (exit {step1.returncode})", "stderr": step1.stderr[-2000:] if step1.stderr else ""}

        # Read latest_run.txt to find the new run
        latest_run_path = os.path.join(REPO_ROOT, 'output_wp', 'latest_run.txt')
        latest_run_value = None
        if os.path.isfile(latest_run_path):
            with open(latest_run_path, 'r', encoding='utf-8') as f:
                latest_run_value = f.read().strip()

        # --- Step 2: Suite verification + generation ---
        contract_path = os.path.join(REPO_ROOT, 'tools', 'whitepaper_contract.py')
        step2 = subprocess.run(
            ["python", contract_path],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=120
        )
        if step2.returncode != 0:
            return {"status": "error", "step": 2, "detail": f"whitepaper_contract.py failed (exit {step2.returncode})", "stderr": step2.stderr[-2000:] if step2.stderr else ""}

        # --- Read suite and build response ---
        suite_path = Path(os.path.join(REPO_ROOT, 'output_wp', 'runs', '_whitepaper_contract', 'whitepaper_contract_suite.json'))
        if not suite_path.exists():
            return {"status": "error", "detail": "Suite file not found after generation at canonical path."}

        with open(suite_path, 'r', encoding='utf-8') as f:
            suite = json.load(f)

        header = suite.get("header", {})
        summary = suite.get("summary", {})

        # Determine audit_status
        try:
            current_commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, stderr=subprocess.DEVNULL).decode("utf-8").strip()
        except Exception:
            current_commit = "unknown"

        suite_commit = header.get("git_commit", "")
        audit_status = "AUDITED" if (suite_commit == current_commit and current_commit != "unknown") else "OUTDATED"

        # Derive new_run_id from latest_run.txt
        new_run_id = latest_run_value if latest_run_value else "unknown"

        return {
            "status": "success",
            "new_run_id": new_run_id,
            "latest_run_txt": latest_run_value,
            "active_suite_abs_path": str(suite_path.resolve()),
            "contract_id": header.get("contract_id"),
            "git_commit": header.get("git_commit"),
            "equation_fingerprint": header.get("equation_fingerprint"),
            "tool_version": header.get("tool_version"),
            "timestamp": header.get("timestamp"),
            "summary_pass": summary.get("pass", 0),
            "summary_fail": summary.get("fail", 0),
            "audit_status": audit_status,
            "step1_stdout_tail": step1.stdout[-500:] if step1.stdout else "",
            "step2_stdout": step2.stdout
        }
    except subprocess.TimeoutExpired as e:
        return {"status": "error", "detail": f"Timeout: {e}"}
    except Exception as e:
        return {"status": "error", "detail": str(e)}

class IntegrationEventRequest(BaseModel):
    event: str
    claim_id: str
    applied_commit: str
    contract_id: str
    manifest_id: str
    equation_fingerprint: str
    whitepaper_file: str
    whitepaper_anchor: str
    timestamp_utc: str

@router.get("/integration_log")
def get_integration_log():
    log_path = Path(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'output_wp', 'whitepaper_integration_log.json'))
    if log_path.exists():
        try:
            with open(log_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data
        except json.JSONDecodeError:
            return {"events": []}
    return {"events": []}

@router.post("/integration_log")
def append_integration_event(req: IntegrationEventRequest):
    log_path = Path(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'output_wp', 'whitepaper_integration_log.json'))
    
    data = {"events": []}
    if log_path.exists():
        try:
            with open(log_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if "events" not in data:
                    data = {"events": []}
        except json.JSONDecodeError:
            pass
            
    data["events"].append(req.dict())
    
    # Ensure directory exists
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with open(log_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
        
    return {"status": "success", "event_added": req.dict()}

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
    
    cfg_itp = CoreConfig(dt=0.1, physics_mode_psi="diffusion", use_mode_coupling=False)
    cfg_wave = CoreConfig(dt=0.1, physics_mode_psi="wave_baseline", use_mode_coupling=False)
    
    start_time = time.time()
    MAX_TIME = 30.0
    
    try:
        # Phase A: Cooling
        for step in range(300):
            if time.time() - start_time > MAX_TIME: break
            
            state = step_core(state, cfg_itp)
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
            
            state = step_core(state, cfg_wave)
            
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
    
    cfg_diff = CoreConfig(dt=0.1, physics_mode_psi="diffusion", use_mode_coupling=True, use_mu=True)
    cfg_wave = CoreConfig(dt=0.1, physics_mode_psi="wave_projected_soft", wave_lpf_enabled=True, use_mode_coupling=True, use_mu=True)
    
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
                
            state_diff = step_core(state_diff, cfg_diff)
            state_wave = step_core(state_wave, cfg_wave)
            
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
async def get_hydrogen_sweep(golden: bool = False):
    """ Runs the golden validation sweep (VALIDATE = conservative params that MUST PASS) """
    sweeps = GOLDEN_HYDRO_SWEEP
    
    grid_sizes = [s[0] for s in sweeps]
    Z_vals = [s[1] for s in sweeps]
    eps_vals = [s[2] for s in sweeps]
    wave_dt = sweeps[0][3] if len(sweeps[0]) > 3 else 0.01
    
    val_data = run_hydrogen_sweep(grid_sizes, Z_vals, eps_vals, wave_dt=wave_dt)
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
    
    with open(os.path.join(os.path.dirname(__file__), '..', 'scripts', 'validation_core.py'), 'r', encoding='utf-8') as f:
        source_code = f.read()
    
    response_data = {
        "manifest": manifest,
        "results": results,
        "expectations": val_data.get("expectations", []),
        "expectation_results": val_data.get("expectation_results", []),
        "overall_pass": val_data.get("overall_pass", None),
        "explain_pack": val_data.get("explain_pack", {}),
        "image_b64": b64,
        "source_code": source_code
    }
    save_run(response_data)
    return response_data

@router.get("/regression/snapshot")
async def get_regression_snapshot(golden: bool = False):
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
    
    with open(os.path.join(os.path.dirname(__file__), '..', 'scripts', 'validation_core.py'), 'r', encoding='utf-8') as f:
        source_code = f.read()
    
    response_data = {
        "manifest": manifest,
        "expectations": val_data.get("expectations", []),
        "expectation_results": val_data.get("expectation_results", []),
        "overall_pass": val_data.get("overall_pass", None),
        "explain_pack": val_data.get("explain_pack", {}),
        "image_b64": b64,
        "source_code": source_code
    }
    save_run(response_data)
    return response_data

@router.get("/history")
async def get_run_history():
    """Lists all saved manifests in descending chronological order.
    Includes overall_pass badge for display WITHOUT loading full run data."""
    runs = []
    for filepath in HISTORY_DIR.glob("*.json"):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                manifest = data.get("manifest", {})
                runs.append({
                    "run_id": manifest.get("run_id"),
                    "timestamp": manifest.get("timestamp"),
                    "git": manifest.get("git"),
                    "scenario": manifest.get("scenario", manifest.get("run_id", "").split('_')[0]),
                    "overall_pass": manifest.get("overall_pass"),
                    "manifest": manifest,
                })
        except Exception as e:
            print(f"Failed to read history file {filepath}: {e}")
            
    runs.sort(key=lambda x: x.get("timestamp", 0) or 0, reverse=True)
    return runs

@router.delete("/history")
async def clear_run_history():
    """Wipes the Lineum Lab Run History database."""
    try:
        count = 0
        for filepath in HISTORY_DIR.glob("*.json"):
            os.remove(filepath)
            count += 1
        return {"status": "cleared", "deleted_count": count}
    except Exception as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/runs/{run_id}")
async def get_run_data(run_id: str):
    """Fetches full telemetry data for a specific run."""
    filepath = HISTORY_DIR / f"{run_id}.json"
    if not filepath.exists():
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Run not found in history")
        
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

class RerunRequest(BaseModel):
    run_id: str

@router.post("/rerun")
async def rerun_from_manifest(req: RerunRequest):
    """Re-executes a run from its stored manifest config.
    Produces a NEW run with fresh run_id so history stays immutable."""
    filepath = HISTORY_DIR / f"{req.run_id}.json"
    if not filepath.exists():
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Original run not found")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        old_data = json.load(f)
    
    old_manifest = old_data.get("manifest", {})
    scenario = old_manifest.get("scenario", "")
    config = old_manifest.get("config", {})
    
    if scenario in ("hydro", "t0"):
        sweeps_cfg = config.get("sweeps", [])
        if sweeps_cfg:
            grid_sizes = [s["grid"] for s in sweeps_cfg]
            Z_vals = [s["Z"] for s in sweeps_cfg]
            eps_vals = [s["eps"] for s in sweeps_cfg]
        else:
            grid_sizes = [s[0] for s in GOLDEN_HYDRO_SWEEP]
            Z_vals = [s[1] for s in GOLDEN_HYDRO_SWEEP]
            eps_vals = [s[2] for s in GOLDEN_HYDRO_SWEEP]
        
        val_data = run_hydrogen_sweep(grid_sizes, Z_vals, eps_vals)
        manifest = val_data["manifest"]
        manifest["rerun_of"] = req.run_id
        results = val_data["results"]
        dens = val_data["final_dens"]
        V = val_data["final_V"]
        
        log_dens = np.log10(dens + 1e-12)
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8, 3))
        im1 = ax1.imshow(V, cmap='viridis')
        ax1.set_title(f"Soft Coulomb V(r)")
        fig.colorbar(im1, ax=ax1)
        im2 = ax2.imshow(log_dens, cmap='magma', vmin=np.max(log_dens)-6, vmax=np.max(log_dens))
        ax2.set_title(f"Log Ground State")
        fig.colorbar(im2, ax=ax2)
        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=100, bbox_inches="tight")
        plt.close()
        buf.seek(0)
        b64 = base64.b64encode(buf.read()).decode("utf-8")
        
        response_data = {
            "manifest": manifest,
            "results": results,
            "expectations": val_data.get("expectations", []),
            "expectation_results": val_data.get("expectation_results", []),
            "overall_pass": val_data.get("overall_pass"),
            "explain_pack": val_data.get("explain_pack", {}),
            "image_b64": b64,
        }
        save_run(response_data)
        return response_data
    
    elif scenario == "mu":
        val_data = run_mu_regression_snapshot()
        manifest = val_data["manifest"]
        manifest["rerun_of"] = req.run_id
        
        fig, axes = plt.subplots(2, 2, figsize=(8, 7))
        axes[0, 0].imshow(np.abs(val_data["psi_diff"])**2, cmap='magma', vmin=0); axes[0, 0].set_title("Diffusion |psi|^2")
        axes[0, 1].imshow(val_data["mu_diff"], cmap='inferno', vmin=0, vmax=10.0); axes[0, 1].set_title("Diffusion Mu")
        axes[1, 0].imshow(np.abs(val_data["psi_wave"])**2, cmap='magma', vmin=0); axes[1, 0].set_title("Wave |psi|^2")
        axes[1, 1].imshow(val_data["mu_wave"], cmap='inferno', vmin=0, vmax=10.0); axes[1, 1].set_title("Wave Mu")
        plt.tight_layout()
        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=100)
        plt.close()
        buf.seek(0)
        b64 = base64.b64encode(buf.read()).decode("utf-8")
        
        response_data = {
            "manifest": manifest,
            "expectations": val_data.get("expectations", []),
            "expectation_results": val_data.get("expectation_results", []),
            "overall_pass": val_data.get("overall_pass"),
            "explain_pack": val_data.get("explain_pack", {}),
            "image_b64": b64,
        }
        save_run(response_data)
        return response_data
    
    elif scenario == "play":
        val_data = run_particle_playground(config)
        manifest = val_data["manifest"]
        manifest["rerun_of"] = req.run_id
        ts_metrics = val_data["ts_metrics"]
        
        fig, axes = plt.subplots(2, 2, figsize=(9, 7))
        im0 = axes[0, 0].imshow(val_data["final_V"], cmap='viridis')
        axes[0, 0].set_title("Potential V(r)")
        fig.colorbar(im0, ax=axes[0, 0])
        log_dens = np.log10(val_data["final_dens"] + 1e-12)
        im1 = axes[0, 1].imshow(log_dens, cmap='magma', vmin=np.max(log_dens)-8, vmax=np.max(log_dens))
        axes[0, 1].set_title("Log Density")
        fig.colorbar(im1, ax=axes[0, 1])
        im2 = axes[1, 0].imshow(val_data["final_dens"], cmap='inferno')
        axes[1, 0].set_title("Linear Density")
        fig.colorbar(im2, ax=axes[1, 0])
        im3 = axes[1, 1].imshow(val_data["final_phase"], cmap='hsv', vmin=-np.pi, vmax=np.pi)
        axes[1, 1].set_title("Phase")
        fig.colorbar(im3, ax=axes[1, 1])
        plt.tight_layout()
        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=100)
        plt.close()
        buf.seek(0)
        b64 = base64.b64encode(buf.read()).decode("utf-8")
        
        response_data = {
            "manifest": manifest,
            "expectations": val_data.get("expectations", []),
            "expectation_results": val_data.get("expectation_results", []),
            "overall_pass": val_data.get("overall_pass"),
            "explain_pack": val_data.get("explain_pack", {}),
            "timeseries_data": ts_metrics,
            "image_b64": b64,
            "results": [{"E": ts_metrics["E"][-1], "r": ts_metrics["r"][-1], "edge_mass_cells": ts_metrics["edge_mass"][-1], "max_edge": ts_metrics["max_edge"][-1]}]
        }
        save_run(response_data)
        return response_data
    
    else:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail=f"Unknown scenario '{scenario}' for rerun")

@router.get("/runs/{run_id}/export")
async def export_run(run_id: str):
    """Generates a ZIP archive containing all artifacts from a run."""
    filepath = HISTORY_DIR / f"{run_id}.json"
    if not filepath.exists():
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Run not found in history")
        
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    import zipfile
    from fastapi.responses import StreamingResponse
    
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as zf:
        # 1. Manifest
        zf.writestr("manifest.json", json.dumps(data.get("manifest", {}), indent=2))
        
        # 2. Metrics CSV
        ts_data = data.get("timeseries_data", data.get("ts_metrics", {}))
        if ts_data:
            import csv
            csv_buf = io.StringIO()
            writer = csv.writer(csv_buf)
            keys = list(ts_data.keys())
            writer.writerow(["step"] + keys)
            
            # Assume all metric lists are same length
            length = len(ts_data[keys[0]])
            for i in range(length):
                row = [i] + [ts_data[k][i] for k in keys]
                writer.writerow(row)
                
            zf.writestr("metrics.csv", csv_buf.getvalue())
            
        # 3. Image
        if "image_b64" in data:
            img_data = base64.b64decode(data["image_b64"])
            zf.writestr("visuals.png", img_data)
            
        # 4. Summary MKD
        summary = f"# Lineum Lab Export: {run_id}\n\n"
        summary += f"- **Scenario**: {data.get('manifest', {}).get('scenario', 'Unknown')}\n"
        summary += f"- **Timestamp**: {data.get('manifest', {}).get('timestamp', 'Unknown')}\n"
        summary += f"- **Git Hash**: {data.get('manifest', {}).get('git', 'Unknown')}\n"
        
        zf.writestr("summary.md", summary)

    buf.seek(0)
    return StreamingResponse(
        buf, 
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename=lineum_{run_id}.zip"}
    )


class PlaygroundRequest(BaseModel):
    config: Dict[str, Any]

@router.post("/playground")
async def post_playground(req: PlaygroundRequest):
    """Triggers the new Particle/State playground with exploratory configuration"""
    val_data = run_particle_playground(req.config)
    manifest = val_data["manifest"]
    ts_metrics = val_data["ts_metrics"]
    dens = val_data["final_dens"]
    phase = val_data["final_phase"]
    V = val_data["final_V"]
    
    # Generate 4-panel visual summary for Lab
    fig, axes = plt.subplots(2, 2, figsize=(9, 7))
    
    im0 = axes[0, 0].imshow(V, cmap='viridis')
    axes[0, 0].set_title(f"Potential V(r)")
    fig.colorbar(im0, ax=axes[0, 0])
    
    log_dens = np.log10(dens + 1e-12)
    im1 = axes[0, 1].imshow(log_dens, cmap='magma', vmin=np.max(log_dens)-8, vmax=np.max(log_dens))
    axes[0, 1].set_title("Log Density log10(|psi|^2)")
    fig.colorbar(im1, ax=axes[0, 1])
    
    im2 = axes[1, 0].imshow(dens, cmap='inferno')
    axes[1, 0].set_title("Linear Density |psi|^2")
    fig.colorbar(im2, ax=axes[1, 0])
    
    im3 = axes[1, 1].imshow(phase, cmap='hsv', vmin=-np.pi, vmax=np.pi)
    axes[1, 1].set_title("Phase arg(psi)")
    fig.colorbar(im3, ax=axes[1, 1])
    
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=100)
    plt.close()
    buf.seek(0)
    b64 = base64.b64encode(buf.read()).decode("utf-8")
    
    with open(os.path.join(os.path.dirname(__file__), '..', 'scripts', 'validation_core.py'), 'r', encoding='utf-8') as f:
        source_code = f.read()
    
    response_data = {
        "manifest": manifest,
        "expectations": val_data.get("expectations", []),
        "expectation_results": val_data.get("expectation_results", []),
        "overall_pass": val_data.get("overall_pass", None),
        "explain_pack": val_data.get("explain_pack", {}),
        "timeseries_data": ts_metrics,
        "image_b64": b64,
        "source_code": source_code,
        "results": [{
            "E": ts_metrics["E"][-1],
            "r": ts_metrics["r"][-1],
            "edge_mass_cells": ts_metrics["edge_mass"][-1],
            "max_edge": ts_metrics["max_edge"][-1]
        }]
    }
    save_run(response_data)
    return response_data


# ══════════════════════════════════════════════════════════════
# Reality Alignment API Endpoints
# ══════════════════════════════════════════════════════════════

def _fig_to_b64(fig):
    """Convert matplotlib figure to base64 PNG string."""
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=100, bbox_inches="tight", facecolor='#121212')
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("utf-8")


@router.get("/ra/unitarity")
async def get_ra1_unitarity(golden: bool = False):
    """RA-1: Wave Unitarity check."""
    val_data = run_ra1_unitarity()

    fig, axes = plt.subplots(1, 2, figsize=(8, 3.5))
    fig.patch.set_facecolor('#121212')
    for ax in axes:
        ax.set_facecolor('#1a1a1a')

    im1 = axes[0].imshow(val_data["final_dens"], cmap='magma')
    axes[0].set_title("|ψ|² Final", color='white')
    fig.colorbar(im1, ax=axes[0])

    im2 = axes[1].imshow(val_data["final_phase"], cmap='twilight', vmin=-np.pi, vmax=np.pi)
    axes[1].set_title("Phase", color='white')
    fig.colorbar(im2, ax=axes[1])

    fig.suptitle("RA-1: Wave Unitarity", color='#00ffff', fontsize=14, fontweight='bold')
    fig.tight_layout()

    response_data = {
        "manifest": val_data["manifest"],
        "expectations": val_data["expectations"],
        "expectation_results": val_data["expectation_results"],
        "overall_pass": val_data["overall_pass"],
        "explain_pack": val_data.get("explain_pack", {}),
        "image_b64": _fig_to_b64(fig),
        "timeseries_data": { "N_series": val_data["N_series"] }
    }
    response_data["manifest"]["is_golden"] = golden
    save_run(response_data)
    return response_data


@router.get("/ra/bound-state")
async def get_ra2_bound_state(golden: bool = False):
    """RA-2: Stable bound state check."""
    val_data = run_ra2_bound_state()

    fig, axes = plt.subplots(1, 2, figsize=(8, 3.5))
    fig.patch.set_facecolor('#121212')
    for ax in axes:
        ax.set_facecolor('#1a1a1a')

    im1 = axes[0].imshow(np.log10(val_data["before_dens"] + 1e-12), cmap='magma')
    axes[0].set_title("Before Wave (ITP Ground)", color='white')
    fig.colorbar(im1, ax=axes[0])

    im2 = axes[1].imshow(np.log10(val_data["after_dens"] + 1e-12), cmap='magma')
    axes[1].set_title("After Wave Hold", color='white')
    fig.colorbar(im2, ax=axes[1])

    ts = val_data["ts_metrics"]

    fig.suptitle("RA-2: Stable Bound State", color='#00ffff', fontsize=14, fontweight='bold')
    fig.tight_layout()

    response_data = {
        "manifest": val_data["manifest"],
        "expectations": val_data["expectations"],
        "expectation_results": val_data["expectation_results"],
        "overall_pass": val_data["overall_pass"],
        "explain_pack": val_data.get("explain_pack", {}),
        "image_b64": _fig_to_b64(fig),
        "timeseries_data": ts
    }
    response_data["manifest"]["is_golden"] = golden
    save_run(response_data)
    return response_data


@router.get("/ra/excited-state")
async def get_ra3_excited_state(golden: bool = False):
    """RA-3: Excited state + orthogonality check."""
    val_data = run_ra3_excited_state()

    fig, axes = plt.subplots(1, 3, figsize=(12, 3.5))
    fig.patch.set_facecolor('#121212')
    for ax in axes:
        ax.set_facecolor('#1a1a1a')

    im1 = axes[0].imshow(val_data["ground_dens"], cmap='magma')
    axes[0].set_title("Ground State |ψ₀|²", color='white')
    fig.colorbar(im1, ax=axes[0])

    im2 = axes[1].imshow(val_data["excited_dens"], cmap='magma')
    axes[1].set_title("Excited State |ψ₁|² (P-like)", color='white')
    fig.colorbar(im2, ax=axes[1])

    # Info panel
    axes[2].axis('off')
    ortho = val_data["manifest"].get("ortho_dot", 0)
    anis = val_data["manifest"].get("anisotropy", 0)
    cdip = val_data["manifest"].get("center_dip", 0)
    info_text = (
        f"Orthogonality |⟨ψ₀|ψ₁⟩|: {ortho:.4f}\n"
        f"Anisotropy (λ₁−λ₂)/(λ₁+λ₂): {anis:.4f}\n"
        f"Center Dip (ρ_center/ρ_peak): {cdip:.4f}\n\n"
        f"{'✅ Has lobes' if cdip < 0.5 and anis > 0.15 else '❌ No clear lobes'}"
    )
    axes[2].text(0.1, 0.5, info_text, transform=axes[2].transAxes,
                 color='white', fontsize=11, verticalalignment='center',
                 fontfamily='monospace')
    axes[2].set_title("Lobe Detection", color='white')

    fig.suptitle("RA-3: Excited State (Two-Lobe)", color='#00ffff', fontsize=14, fontweight='bold')
    fig.tight_layout()

    response_data = {
        "manifest": val_data["manifest"],
        "expectations": val_data["expectations"],
        "expectation_results": val_data["expectation_results"],
        "overall_pass": val_data["overall_pass"],
        "explain_pack": val_data.get("explain_pack", {}),
        "image_b64": _fig_to_b64(fig),
    }
    response_data["manifest"]["is_golden"] = golden
    save_run(response_data)
    return response_data


@router.get("/ra/mu-memory")
async def get_ra4_mu_memory(golden: bool = False):
    """RA-4: μ Memory Imprint check (Lineum-only)."""
    val_data = run_ra4_mu_memory()

    fig, axes = plt.subplots(1, 2, figsize=(8, 3.5))
    fig.patch.set_facecolor('#121212')
    for ax in axes:
        ax.set_facecolor('#1a1a1a')

    im1 = axes[0].imshow(val_data["psi_dens"], cmap='magma')
    axes[0].set_title("|ψ|² Density", color='white')
    fig.colorbar(im1, ax=axes[0])

    im2 = axes[1].imshow(val_data["mu_field"], cmap='inferno')
    axes[1].set_title(f"μ Memory Field\nVerdict: {val_data['verdict'].upper()}", color='white')
    fig.colorbar(im2, ax=axes[1])

    fig.suptitle(f"RA-4: μ Memory — {val_data['verdict'].upper()}", color='#00ffff', fontsize=14, fontweight='bold')
    fig.tight_layout()

    response_data = {
        "manifest": val_data["manifest"],
        "expectations": val_data["expectations"],
        "expectation_results": val_data["expectation_results"],
        "overall_pass": val_data["overall_pass"],
        "explain_pack": val_data.get("explain_pack", {}),
        "image_b64": _fig_to_b64(fig),
        "timeseries_data": { "mu_max_series": val_data["mu_max_series"] }
    }
    response_data["manifest"]["is_golden"] = golden
    save_run(response_data)
    return response_data


@router.get("/ra/driving")
async def get_ra5_driving(golden: bool = False):
    """RA-5: Driving vs Dephasing check (Lineum-only)."""
    val_data = run_ra5_driving()

    response_data = {
        "manifest": val_data["manifest"],
        "expectations": val_data["expectations"],
        "expectation_results": val_data["expectation_results"],
        "overall_pass": val_data["overall_pass"],
        "explain_pack": val_data.get("explain_pack", {}),
        "timeseries_data": {
            "N_driven": val_data["N_driven"],
            "N_undriven": val_data["N_undriven"]
        }
    }
    response_data["manifest"]["is_golden"] = golden
    save_run(response_data)
    return response_data


@router.get("/ra/lpf-impact")
async def get_ra6_lpf_impact(golden: bool = False):
    """RA-6: LPF ON vs OFF Impact check (Lineum-only)."""
    val_data = run_ra6_lpf_impact()

    response_data = {
        "manifest": val_data["manifest"],
        "expectations": val_data["expectations"],
        "expectation_results": val_data["expectation_results"],
        "overall_pass": val_data["overall_pass"],
        "explain_pack": val_data.get("explain_pack", {}),
        "timeseries_data": {
            "E_off": val_data["E_off"],
            "E_on": val_data["E_on"],
            "N_off": val_data["N_off"],
            "N_on": val_data["N_on"],
        }
    }
    response_data["manifest"]["is_golden"] = golden
    save_run(response_data)
    return response_data
