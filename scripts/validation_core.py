import numpy as np
import time
import subprocess
from lineum_core.math import CoreConfig, step_core

def get_git_info():
    try:
        commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
        branch = subprocess.check_output(['git', 'rev-parse', '--abbrev-ref', 'HEAD'], text=True).strip()
        return f"{branch}@{commit[:7]}"
    except Exception:
        return "unknown"

# ══════════════════════════════════════════════════════════════
# P3 — Machine-Checkable Expectation Engine
# Every VALIDATE scenario defines expectations[] objects.
# After a run, evaluate_expectations() produces:
#   expectation_results[] — per-item { label, expected, measured, passed }
#   overall_pass          — True iff ALL expectations passed
# The frontend ONLY renders these; it does ZERO math.
# ══════════════════════════════════════════════════════════════

def evaluate_expectations(expectations, measured_values):
    """
    Evaluates a list of expectation objects against measured values.
    
    Each expectation: { "metric": str, "op": "<"|">"|"<="|">="|"=="|"!=",
                        "value": float, "label": str }
    measured_values: dict mapping metric names to float values.
    
    Returns: (expectation_results: list[dict], overall_pass: bool)
    """
    ops = {
        "<":  lambda a, b: a < b,
        ">":  lambda a, b: a > b,
        "<=": lambda a, b: a <= b,
        ">=": lambda a, b: a >= b,
        "==": lambda a, b: abs(a - b) < 1e-9,
        "!=": lambda a, b: abs(a - b) >= 1e-9,
    }
    
    results = []
    for exp in expectations:
        metric = exp["metric"]
        op_str = exp["op"]
        threshold = exp["value"]
        label = exp["label"]
        human_label = exp.get("human_label", label)  # fallback to label if missing
        
        measured = measured_values.get(metric)
        if measured is None:
            results.append({
                "label": label,
                "human_label": human_label,
                "metric": metric,
                "op": op_str,
                "expected": threshold,
                "measured": None,
                "passed": False
            })
            continue
            
        passed = ops[op_str](float(measured), float(threshold))
        results.append({
            "label": label,
            "human_label": human_label,
            "metric": metric,
            "op": op_str,
            "expected": threshold,
            "measured": round(float(measured), 6),
            "passed": bool(passed)
        })
    
    overall_pass = all(r["passed"] for r in results)
    return results, overall_pass


def get_explain_pack(scenario: str, passed: bool) -> dict:
    """Returns the strict Layman 100% self-explanatory UI texts based on the run's scenario and PASS/FAIL result."""
    
    # Common disclaimers
    disc = [
        "2D Slice: You are looking at a cross-section. Reality is 3D.",
        "Single-particle analog: This is one scalar field. It's not multi-electron chemistry.",
        "Dimensionless units: Grids and times are scaled arbitrary units for stability.",
        "Periodic boundaries: Things leaving the left side reappear on the right."
    ]

    base = {
        "success_criteria_human": "Expectations met: The wave equation behaves according to known physics without exploding or evaporating." if passed else "Expectations failed: The physics engine blew up, broke conservation laws, or the boundaries were too tight.",
        "next_action_pass": "Compare to History / Export Data",
        "next_action_fail": "Auto-Fix Stability / Enhance Grid",
        "disclaimers": disc,
        "glossary_terms_used": ["Validate", "Explore", "Cloud", "Ground state", "P-state", "Leak"]
    }

    packs = {
        "hydro": {
            "one_liner_human": "Simulating a Hydrogen-like atom's core pulling a particle.",
            "what_you_see": ["A density map of the particle.", "Bright core = higher probability of finding the particle there."],
            "what_it_is_not": ["Not actual quantum chemistry.", "Not a full standard model description."],
        },
        "mu": {
            "one_liner_human": "Testing if the system remembers where the particle was.",
            "what_you_see": ["Particle bouncing off an obstacle.", "Bright 'Mu' map = the memory/damage footprint left behind."],
            "what_it_is_not": ["Not a physical fluid trace.", "Just an internal stability check for Lineum's coupling."],
        },
        "play": {
            "one_liner_human": "Custom Sandbox for tuning particle environments and shapes.",
            "what_you_see": ["The resulting wave density mapped to color.", "Brighter = denser particle cloud."],
            "what_it_is_not": ["Not validation-grade unless locked.", "Free parameters can cause the engine to explode numerically."],
        },
        "ra1": {
            "one_liner_human": "Ensuring the particle doesn't magically appear or vanish (Unitarity).",
            "what_you_see": ["Total mass (Norm) graphed over time.", "A flat line means mass is perfectly conserved!"],
            "what_it_is_not": ["Not a plot of physical size.", "Not modeling particle creation/annihilation."],
        },
        "ra2": {
            "one_liner_human": "Ensuring a trapped particle stays trapped (Bound State).",
            "what_you_see": ["Energy and distance graphed over time.", "Stable flat lines = stable physics."],
            "what_it_is_not": ["Not a free-floating electron.", "Not affected by outside radiation."],
        },
        "ra3": {
            "one_liner_human": "Making sure excited states look like real shapes (P-State Lobes).",
            "what_you_see": ["A shape with two distinct lobes instead of one round blob.", "A dark center node where the particle cannot be."],
            "what_it_is_not": ["Not a chemical bond.", "Not multiple particles (it's one particle split in probability)."],
        },
        "ra4": {
            "one_liner_human": "Confirming the Lineum Memory (Mu) doesn't grow infinitely.",
            "what_you_see": ["Max memory size graphed over time.", "It should flatten out and stop growing."],
            "what_it_is_not": ["Not standard Schrödinger physics (this is a Lineum-only feature)."],
        },
        "ra5": {
            "one_liner_human": "Connecting the 'engine' to the particle (Driving Forces).",
            "what_you_see": ["Two lines comparing active vs inactive pushing.", "The active line should climb indicating energy injection."],
            "what_it_is_not": ["Not a passive system.", "Not standard quantum mechanics (Lineum active driving)."],
        },
        "ra6": {
            "one_liner_human": "Filtering high-frequency noise numerically.",
            "what_you_see": ["Two runs: one with the filter ON, one OFF.", "The lines should differ slightly, showing the filter works."],
            "what_it_is_not": ["Not a physical effect.", "Just a software numerical stabilization tool."],
        }
    }

    # Merge base with specific
    merged = {**base, **packs.get(scenario, packs["play"])}
    
    # Provide safe fallbacks if missing
    if "what_you_see" not in merged: merged["what_you_see"] = ["Data outputs"]
    if "what_it_is_not" not in merged: merged["what_it_is_not"] = ["Not verified"]
    if "one_liner_human" not in merged: merged["one_liner_human"] = "Validation execution"
    
    return merged

# ── Per-Scenario Expectation Definitions ─────────────────────

HYDRO_EXPECTATIONS = [
    {"metric": "edge_mass_cells", "op": "<", "value": 0.10,
     "label": "Edge mass (8-cell border) below 10%",
     "human_label": "The cloud stays in the center, not leaking to edges."},
    {"metric": "drift_dE",        "op": "<", "value": 0.15,
     "label": "Energy drift ΔE/E < 15% after wave hold",
     "human_label": "Energy stays stable — no runaway behavior."},
    {"metric": "norm_final",      "op": ">", "value": 0.80,
     "label": "Norm N(t) stays above 80% of initial",
     "human_label": "The particle doesn't 'evaporate' — most of it survives."},
]

WAVE_SANITY_EXPECTATIONS = [
    {"metric": "norm_drift_pct",  "op": "<", "value": 5.0,
     "label": "Norm drift < 5% over 30 wave steps",
     "human_label": "The wave engine conserves mass — nothing appears or disappears."},
    {"metric": "edge_mass_cells", "op": "<", "value": 0.10,
     "label": "Edge mass (8-cell border) below 10%",
     "human_label": "The cloud stays in the center, not leaking to edges."},
    {"metric": "drift_dE",        "op": "<", "value": 0.15,
     "label": "Energy conservation ΔE/E < 15%",
     "human_label": "Energy stays stable — the physics engine is healthy."},
]

MU_REGRESSION_EXPECTATIONS = [
    {"metric": "mu_wave_max",         "op": ">",  "value": 0.1,
     "label": "Wave mode deposits structural memory (μ > 0.1)",
     "human_label": "Wave mode creates a lasting 'footprint' in memory."},
    {"metric": "mu_diff_max",         "op": ">",  "value": 0.1,
     "label": "Diffusion mode deposits structural memory (μ > 0.1)",
     "human_label": "Diffusion mode also leaves a memory trace."},
    {"metric": "psi_wave_has_no_nan", "op": "==", "value": 1.0,
     "label": "Wave ψ contains no NaN",
     "human_label": "Wave calculation completed without crashing."},
    {"metric": "psi_diff_has_no_nan", "op": "==", "value": 1.0,
     "label": "Diffusion ψ contains no NaN",
     "human_label": "Diffusion calculation completed without crashing."},
]

PLAYGROUND_EXPECTATIONS = [
    {"metric": "edge_mass_max",  "op": "<", "value": 0.30,
     "label": "Max edge mass < 30% (exploratory acceptable containment)",
     "human_label": "The particle cloud stays contained enough for exploratory runs."},
    {"metric": "energy_bounded", "op": "==", "value": 1.0,
     "label": "Energy E(t) remains finite (no NaN/Inf)",
     "human_label": "Energy didn't explode — the simulation stayed sane."},
]


# ── Golden Validate Sweep Configs ────────────────────────────
# Conservative params that MUST PASS on default VALIDATE.  
# Aggressive sweeps (Z>2, 128x128) belong in EXPLORE only.

GOLDEN_HYDRO_SWEEP = [
    # (grid_size, Z, eps, wave_dt) — conservative params that MUST PASS
    (64, 1.0, 0.1, 0.005),
    (64, 2.0, 0.1, 0.005),
]


def run_hydrogen_sweep(grid_sizes, Z_vals, eps_vals, wave_dt=0.01):
    """
    Runs the ground state validation logic for the Hydrogen atom proxy.
    Used by both Pytest (CI) and the Svelte Validation Dashboard (Lab).
    
    Args:
        wave_dt: Time step for unitary wave propagation (lower = more conservative).
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
        cfg_itp = CoreConfig(dt=0.1, physics_mode_psi="diffusion", use_mode_coupling=False)
        N_initial = None
        for step_i in range(150):
            state = step_core(state, cfg_itp)
            N_curr = np.sum(np.abs(state["psi"])**2) * dV
            if step_i == 0:
                N_initial = N_curr
            state["psi"] = state["psi"] / np.sqrt(N_curr)
            
        psi_gs = state["psi"].copy()
        e_dens_gs = np.abs(psi_gs)**2
        
        # Energy Expectation (Exact Lebesgue integral formulation utilizing explicit dx tracking)
        grad_x, grad_y = np.gradient(psi_gs, dx, dx)
        kin_dens = np.abs(grad_x)**2 + np.abs(grad_y)**2
        pot_dens = V * e_dens_gs
        
        E_0 = np.sum(kin_dens) * dV + np.sum(pot_dens) * dV
        
        # 2. Unitary Wave Propagation (Sanity Check)
        cfg_wave = CoreConfig(dt=wave_dt, physics_mode_psi="wave_baseline", use_mode_coupling=False)
        N_before_wave = np.sum(np.abs(state["psi"])**2) * dV
        for _ in range(30):
            state = step_core(state, cfg_wave)
            
        e_dens_final = np.abs(state["psi"])**2
        norm_final = np.sum(e_dens_final) * dV # should be 1.0 continuously
        
        norm_drift_pct = abs(norm_final - N_before_wave) / (N_before_wave + 1e-9) * 100.0
        
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
            "norm_final": float(norm_final), "norm_drift_pct": float(norm_drift_pct),
            "r": float(r_exp), "r2": float(r2_exp),
            "edge_mass_cells": edge_mass_cells, "max_edge": max_edge
        })
        
        final_dens = e_dens_final
        final_V = V

    # ── Evaluate Expectations (using LAST sweep result as representative) ──
    last = results[-1]
    measured = {
        "edge_mass_cells": last["edge_mass_cells"],
        "drift_dE": last["drift_dE"],
        "norm_final": last["norm_final"],
        "norm_drift_pct": last["norm_drift_pct"],
    }
    expectation_results, overall_pass = evaluate_expectations(HYDRO_EXPECTATIONS, measured)

    manifest = {
        "run_id": f"hydro_{int(time.time())}",
        "git": get_git_info(),
        "timestamp": time.time(),
        "scenario": "hydro",
        "config": {
            "physics_mode_psi": "wave_baseline",
            "dt": 0.1,
            "seed": 42,
            "itp_steps": 150,
            "wave_steps": 30,
            "LPF_enabled": False,
            "kappa_blur_iters": 0,
            "mu_params": {"use_mu": False},
            "sweeps": [{"grid": s, "Z": z, "eps": e} for s, z, e in sweeps],
        },
        "overall_pass": overall_pass,
    }
    
    return {
        "manifest": manifest,
        "results": results,
        "expectations": HYDRO_EXPECTATIONS,
        "expectation_results": expectation_results,
        "overall_pass": overall_pass,
        "final_dens": final_dens,
        "final_V": final_V,
        "explain_pack": get_explain_pack("hydro", overall_pass)
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
        cfg = CoreConfig(**kwargs)
        
        for _ in range(500):
            state["psi"][30:35, 30:35] += (0.1 + 0.1j) * cfg.dt
            state["psi"][90:95, 90:95] += (0.1 - 0.1j) * cfg.dt
            state = step_core(state, cfg)
            
        return state["psi"], state["mu"]

    diff_args = {"dt": 0.1, "physics_mode_psi": "diffusion", "use_mode_coupling": True, "use_mu": True}
    wave_args = {"dt": 0.1, "physics_mode_psi": "wave_projected_soft", "wave_lpf_enabled": True, "use_mode_coupling": True, "use_mu": True}
    
    psi_diff, mu_diff = run_reg(diff_args)
    psi_wave, mu_wave = run_reg(wave_args)

    # ── Evaluate Expectations ──
    measured = {
        "mu_wave_max": float(np.max(mu_wave)),
        "mu_diff_max": float(np.max(mu_diff)),
        "psi_wave_has_no_nan": 0.0 if np.isnan(np.sum(psi_wave)) else 1.0,
        "psi_diff_has_no_nan": 0.0 if np.isnan(np.sum(psi_diff)) else 1.0,
    }
    expectation_results, overall_pass = evaluate_expectations(MU_REGRESSION_EXPECTATIONS, measured)
    
    manifest = {
        "run_id": f"mureg_{int(time.time())}",
        "git": get_git_info(),
        "timestamp": time.time(),
        "scenario": "mu",
        "config": {
            "diffusion": diff_args,
            "wave": wave_args
        },
        "overall_pass": overall_pass,
    }
    
    return {
        "manifest": manifest,
        "expectations": MU_REGRESSION_EXPECTATIONS,
        "expectation_results": expectation_results,
        "overall_pass": overall_pass,
        "psi_diff": psi_diff, "mu_diff": mu_diff,
        "psi_wave": psi_wave, "mu_wave": mu_wave,
        "explain_pack": get_explain_pack("mu", overall_pass)
    }

def run_particle_playground(config_overrides: dict):
    """
    Runs the advanced Particle/State Playground with time-series telemetry and excited state orthogonalization.
    Used exclusively by the Lab UI to guarantee 1:1 mathematical fidelity with Validation Core.
    """
    size = config_overrides.get("grid_size", 64)
    Z = config_overrides.get("Z", 2.0)
    eps = config_overrides.get("eps", 0.1)
    potential_type = config_overrides.get("potential_type", "coulomb")
    excited_state = config_overrides.get("excited_state", 0)
    
    x = np.linspace(-1, 1, size)
    y = np.linspace(-1, 1, size)
    dx = 2.0 / size
    dV = dx * dx
    X, Y = np.meshgrid(x, y)
    R = np.sqrt(X**2 + Y**2)
    
    # Generate Physics Potential V(r)
    if potential_type == "harmonic":
        V = 0.5 * Z * R**2
    elif potential_type == "double_well":
        V = Z * ((X**2 - 0.25)**2 + Y**2)
    elif potential_type == "ring":
        V = Z * (R - 0.5)**2
    else: # Soft Coulomb
        V = -Z / np.sqrt(R**2 + eps**2)
        
    phi_pot = np.clip(-V * 100, 0, 1000)
    kappa = np.ones((size, size), dtype=np.float64)
    
    # Configure Time-Series Data Recording Arrays
    ts_metrics = {"time": [], "N": [], "E": [], "r": [], "r2": [], "edge_mass": [], "max_edge": [], "ortho_dot": []}
    
    border_cells = 8
    edge_mask = np.ones((size, size), dtype=bool)
    edge_mask[border_cells:-border_cells, border_cells:-border_cells] = False

    def record_state(psi_arr, V_arr, step_idx):
        dens = np.abs(psi_arr)**2
        N_curr = np.sum(dens) * dV
        
        # Energy Expectation
        grad_x, grad_y = np.gradient(psi_arr, dx, dx)
        kin_dens = np.abs(grad_x)**2 + np.abs(grad_y)**2
        E_curr = np.sum(kin_dens) * dV + np.sum(V_arr * dens) * dV
        
        edge_mass = np.sum(dens[edge_mask]) * dV / (N_curr + 1e-9)
        max_edge = np.max(dens[edge_mask]) if np.any(edge_mask) else 0.0
        r_exp = np.sum(R * dens) * dV / (N_curr + 1e-9)
        r2_exp = np.sum(R**2 * dens) * dV / (N_curr + 1e-9)
        
        ts_metrics["time"].append(step_idx)
        ts_metrics["N"].append(float(N_curr))
        ts_metrics["E"].append(float(E_curr))
        ts_metrics["r"].append(float(r_exp))
        ts_metrics["r2"].append(float(r2_exp))
        ts_metrics["edge_mass"].append(float(edge_mass))
        ts_metrics["max_edge"].append(float(max_edge))

    # ---- 1) Ground State Computation (Always Needed) ----
    psi_0 = np.exp(-R**2 / 0.5).astype(np.complex128)
    state = {"psi": psi_0, "phi": phi_pot, "kappa": kappa}
    cfg_itp = CoreConfig(dt=0.1, physics_mode_psi="diffusion", use_mode_coupling=False)
    
    for _ in range(100):
        state = step_core(state, cfg_itp)
        state["psi"] /= np.sqrt(np.sum(np.abs(state["psi"])**2) * dV)
        
    ground_state_psi = state["psi"].copy()

    # ---- 2) Excitations (Gram-Schmidt Orthogonalization) ----
    if excited_state > 0:
        # Start with an asymmetric ansatz for excited P-state (e.g. x-oriented lobe)
        if excited_state == 1:
            psi_curr = (X * np.exp(-R**2 / 0.5)).astype(np.complex128)
        else: # D-state
            psi_curr = (X * Y * np.exp(-R**2 / 0.5)).astype(np.complex128)
            
        state["psi"] = psi_curr
        
        for _ in range(100):
            state = step_core(state, cfg_itp)
            
            # Gram-Schmidt Projection: |psi> = |psi> - <psi_0|psi>|psi_0>
            overlap = np.sum(np.conj(ground_state_psi) * state["psi"]) * dV
            state["psi"] -= overlap * ground_state_psi
            state["psi"] /= np.sqrt(np.sum(np.abs(state["psi"])**2) * dV)
    
    # ---- 3) User Target Run (Unitary or Continue Diff) ----
    user_dt = config_overrides.get("dt", 0.1)
    user_mode = config_overrides.get("physics_mode_psi", "wave_baseline")
    
    cfg_user = CoreConfig(
        dt=user_dt,
        physics_mode_psi=user_mode,
        use_mode_coupling=False,
        wave_lpf_enabled=config_overrides.get("wave_lpf_enabled", False)
    )
    
    for step in range(50):
        state = step_core(state, cfg_user)
        
        if excited_state > 0:
            # Re-enforce orthogonality continually if requested (though Unitary should preserve it)
            overlap = np.sum(np.conj(ground_state_psi) * state["psi"]) * dV
            ts_metrics["ortho_dot"].append(abs(float(overlap)))
        else:
            ts_metrics["ortho_dot"].append(0.0)
            
        if step % 2 == 0:
            record_state(state["psi"], V, step)
            
    # Final Visual Snapshot Extraction
    final_dens = np.abs(state["psi"])**2
    final_phase = np.angle(state["psi"])

    # ── Evaluate Expectations ──
    edge_mass_max = max(ts_metrics["edge_mass"]) if ts_metrics["edge_mass"] else 0.0
    energy_vals = ts_metrics["E"]
    energy_bounded = 1.0 if (energy_vals and all(np.isfinite(e) for e in energy_vals)) else 0.0
    
    measured = {
        "edge_mass_max": edge_mass_max,
        "energy_bounded": energy_bounded,
    }
    expectation_results, overall_pass = evaluate_expectations(PLAYGROUND_EXPECTATIONS, measured)

    manifest = {
        "run_id": f"play_{int(time.time())}",
        "git": get_git_info(),
        "timestamp": time.time(),
        "scenario": "play",
        "config": config_overrides,
        "overall_pass": overall_pass,
    }
    
    return {
        "manifest": manifest,
        "expectations": PLAYGROUND_EXPECTATIONS,
        "expectation_results": expectation_results,
        "overall_pass": overall_pass,
        "ts_metrics": ts_metrics,
        "final_dens": final_dens,
        "final_phase": final_phase,
        "final_V": V,
        "explain_pack": get_explain_pack("play", overall_pass)
    }


# ══════════════════════════════════════════════════════════════
# Reality Alignment — Expectations
# ══════════════════════════════════════════════════════════════

RA1_EXPECTATIONS = [
    {"metric": "unitarity_error", "op": "<", "value": 0.05,
     "label": "Unitarity error < 5% over 50 wave steps",
     "human_label": "The wave conserves its total 'mass' — nothing appears or disappears."},
    {"metric": "has_no_nan", "op": "==", "value": 1.0,
     "label": "ψ contains no NaN after wave propagation",
     "human_label": "The calculation completed without crashing."},
]

RA2_EXPECTATIONS = [
    {"metric": "edge_mass_cells", "op": "<", "value": 0.10,
     "label": "Edge mass (8-cell border) below 10%",
     "human_label": "The cloud stays in the center, not leaking to edges."},
    {"metric": "drift_dE", "op": "<", "value": 0.15,
     "label": "Energy drift ΔE/E < 15% after wave hold",
     "human_label": "Energy stays stable — no runaway behavior."},
    {"metric": "norm_final", "op": ">", "value": 0.80,
     "label": "Norm N(t) stays above 80% of initial",
     "human_label": "The particle doesn't 'evaporate' — most of it survives."},
]

RA3_EXPECTATIONS = [
    {"metric": "ortho_dot", "op": "<", "value": 0.05,
     "label": "Orthogonality |⟨ψ₀|ψ₁⟩| < 0.05",
     "human_label": "The excited shape is genuinely different from the ground state."},
    {"metric": "anisotropy", "op": ">", "value": 0.03,
     "label": "Density anisotropy (λ₁−λ₂)/(λ₁+λ₂) > 0.03",
     "human_label": "The excited state is clearly elongated — not just a round blob."},
    {"metric": "center_dip", "op": "<", "value": 0.50,
     "label": "Center density ratio < 50% of peak",
     "human_label": "The center is nearly empty — the 'two-lobe butterfly' pattern is visible."},
    {"metric": "ground_no_nan", "op": "==", "value": 1.0,
     "label": "Ground state ψ contains no NaN",
     "human_label": "Ground state computed without crashing."},
]

RA4_EXPECTATIONS = [
    {"metric": "mu_max_bounded", "op": "==", "value": 1.0,
     "label": "μ_max remains below mu_cap (no runaway)",
     "human_label": "Memory doesn't explode — it stays bounded."},
    {"metric": "mu_grows", "op": "==", "value": 1.0,
     "label": "μ deposits non-zero structural memory",
     "human_label": "The system actually remembers where the particle was."},
    {"metric": "mu_has_no_nan", "op": "==", "value": 1.0,
     "label": "μ field contains no NaN",
     "human_label": "Memory calculation completed without crashing."},
]

RA5_EXPECTATIONS = [
    {"metric": "driven_energy_positive", "op": "==", "value": 1.0,
     "label": "Driven mode shows net energy injection (ΔN > 0)",
     "human_label": "With forcing ON, the system gains energy — it's being 'driven'."},
    {"metric": "undriven_stable", "op": "==", "value": 1.0,
     "label": "Undriven mode energy does not grow (|ΔN| stable)",
     "human_label": "Without forcing, the system stays quiet — no spontaneous growth."},
]

RA6_EXPECTATIONS = [
    {"metric": "lpf_changes_dynamics", "op": "==", "value": 1.0,
     "label": "LPF ON vs OFF produces measurably different dynamics",
     "human_label": "The low-pass filter changes the result (expected — it's a numerical tool)."},
    {"metric": "both_runs_stable", "op": "==", "value": 1.0,
     "label": "Both LPF ON and OFF runs remain numerically stable",
     "human_label": "Both runs completed without crashing or diverging."},
]


# ══════════════════════════════════════════════════════════════
# Reality Alignment — Run Functions
# ══════════════════════════════════════════════════════════════

def run_ra1_unitarity():
    """RA-1: Wave Unitarity — check N(t) conservation during wave propagation."""
    size = 64
    x = np.linspace(-1, 1, size)
    dx = 2.0 / size
    dV = dx * dx
    X, Y = np.meshgrid(x, x)
    R = np.sqrt(X**2 + Y**2)

    psi = np.exp(-R**2 / 0.3).astype(np.complex128)
    psi /= np.sqrt(np.sum(np.abs(psi)**2) * dV)
    kappa = np.ones((size, size), dtype=np.float64)
    phi = np.zeros((size, size), dtype=np.float64)

    state = {"psi": psi.copy(), "phi": phi, "kappa": kappa}
    cfg = CoreConfig(dt=0.005, physics_mode_psi="wave_baseline", use_mode_coupling=False)

    N_series = []
    N0 = np.sum(np.abs(state["psi"])**2) * dV
    for step in range(50):
        state = step_core(state, cfg)
        N_curr = np.sum(np.abs(state["psi"])**2) * dV
        N_series.append(float(N_curr))

    unitarity_error = max(abs(n - N0) / N0 for n in N_series) if N_series else 1.0
    has_no_nan = 1.0 if not np.isnan(np.sum(state["psi"])) else 0.0

    measured = {"unitarity_error": unitarity_error, "has_no_nan": has_no_nan}
    exp_results, overall_pass = evaluate_expectations(RA1_EXPECTATIONS, measured)

    final_dens = np.abs(state["psi"])**2
    final_phase = np.angle(state["psi"])

    manifest = {
        "run_id": f"ra1_{int(time.time())}",
        "git": get_git_info(),
        "timestamp": time.time(),
        "scenario": "ra1",
        "config": {"grid": size, "dt": 0.005, "steps": 50, "physics_mode": "wave_baseline"},
        "overall_pass": overall_pass,
    }
    return {
        "manifest": manifest,
        "expectations": RA1_EXPECTATIONS,
        "expectation_results": exp_results,
        "overall_pass": overall_pass,
        "N_series": N_series,
        "final_dens": final_dens,
        "final_phase": final_phase,
        "explain_pack": get_explain_pack("ra1", overall_pass)
    }


def run_ra2_bound_state():
    """RA-2: Bound State — ITP ground state + wave hold, single golden config."""
    size, Z, eps, wave_dt = 64, 1.0, 0.1, 0.005
    x = np.linspace(-1, 1, size)
    dx = 2.0 / size
    dV = dx * dx
    X, Y = np.meshgrid(x, x)
    R = np.sqrt(X**2 + Y**2)
    V = -Z / np.sqrt(R**2 + eps**2)
    phi_pot = np.clip(-V * 100, 0, 1000)
    kappa = np.ones((size, size), dtype=np.float64)

    psi = np.exp(-R**2 / 0.5).astype(np.complex128)
    state = {"psi": psi, "phi": phi_pot, "kappa": kappa}

    # ITP
    cfg_itp = CoreConfig(dt=0.1, physics_mode_psi="diffusion", use_mode_coupling=False)
    for _ in range(150):
        state = step_core(state, cfg_itp)
        N = np.sum(np.abs(state["psi"])**2) * dV
        state["psi"] /= np.sqrt(N)

    before_dens = np.abs(state["psi"])**2
    psi_gs = state["psi"].copy()

    # Energy before wave
    grad_x, grad_y = np.gradient(psi_gs, dx, dx)
    E_0 = np.sum(np.abs(grad_x)**2 + np.abs(grad_y)**2) * dV + np.sum(V * before_dens) * dV

    # Wave hold
    cfg_wave = CoreConfig(dt=wave_dt, physics_mode_psi="wave_baseline", use_mode_coupling=False)
    N_before = np.sum(np.abs(state["psi"])**2) * dV

    ts = {"time": [], "E": [], "r": [], "edge_mass": []}
    border_cells = 8
    edge_mask = np.ones((size, size), dtype=bool)
    edge_mask[border_cells:-border_cells, border_cells:-border_cells] = False

    for step in range(30):
        state = step_core(state, cfg_wave)
        dens = np.abs(state["psi"])**2
        N_curr = np.sum(dens) * dV
        gx, gy = np.gradient(state["psi"], dx, dx)
        E_curr = np.sum(np.abs(gx)**2 + np.abs(gy)**2) * dV + np.sum(V * dens) * dV
        r_curr = np.sum(R * dens) * dV / (N_curr + 1e-9)
        em = np.sum(dens[edge_mask]) * dV / (N_curr + 1e-9)
        ts["time"].append(step)
        ts["E"].append(float(E_curr))
        ts["r"].append(float(r_curr))
        ts["edge_mass"].append(float(em))

    after_dens = np.abs(state["psi"])**2
    norm_final = np.sum(after_dens) * dV
    drift_dE = abs(ts["E"][-1] - E_0) / (abs(E_0) + 1e-9) if ts["E"] else 1.0
    edge_mass_cells = ts["edge_mass"][-1] if ts["edge_mass"] else 1.0

    measured = {"edge_mass_cells": edge_mass_cells, "drift_dE": drift_dE, "norm_final": norm_final}
    exp_results, overall_pass = evaluate_expectations(RA2_EXPECTATIONS, measured)

    manifest = {
        "run_id": f"ra2_{int(time.time())}",
        "git": get_git_info(),
        "timestamp": time.time(),
        "scenario": "ra2",
        "config": {"grid": size, "Z": Z, "eps": eps, "wave_dt": wave_dt, "itp_steps": 150, "wave_steps": 30},
        "overall_pass": overall_pass,
    }
    return {
        "manifest": manifest,
        "expectations": RA2_EXPECTATIONS,
        "expectation_results": exp_results,
        "overall_pass": overall_pass,
        "before_dens": before_dens,
        "after_dens": after_dens,
        "ts_metrics": ts,
        "final_V": V,
        "explain_pack": get_explain_pack("ra2", overall_pass)
    }


def run_ra3_excited_state():
    """RA-3: Excited state + orthogonality with robust PCA lobe detection."""
    size = 64
    x = np.linspace(-1, 1, size)
    dx = 2.0 / size
    dV = dx * dx
    X, Y = np.meshgrid(x, x)
    R = np.sqrt(X**2 + Y**2)
    Z, eps = 1.0, 0.1
    V = -Z / np.sqrt(R**2 + eps**2)
    phi_pot = np.clip(-V * 100, 0, 1000)
    kappa = np.ones((size, size), dtype=np.float64)

    # Ground state
    psi_0 = np.exp(-R**2 / 0.5).astype(np.complex128)
    state = {"psi": psi_0, "phi": phi_pot, "kappa": kappa}
    cfg_itp = CoreConfig(dt=0.1, physics_mode_psi="diffusion", use_mode_coupling=False)
    for _ in range(100):
        state = step_core(state, cfg_itp)
        state["psi"] /= np.sqrt(np.sum(np.abs(state["psi"])**2) * dV)
    ground_psi = state["psi"].copy()
    ground_dens = np.abs(ground_psi)**2

    # Excited state (P-state ansatz: x * gaussian)
    psi_exc = (X * np.exp(-R**2 / 0.3)).astype(np.complex128)
    state["psi"] = psi_exc
    for _ in range(100):
        state = step_core(state, cfg_itp)
        # Gram-Schmidt: project out ground
        overlap = np.sum(np.conj(ground_psi) * state["psi"]) * dV
        state["psi"] -= overlap * ground_psi
        state["psi"] /= np.sqrt(np.sum(np.abs(state["psi"])**2) * dV)
    excited_psi = state["psi"].copy()
    excited_dens = np.abs(excited_psi)**2

    # Orthogonality metric
    ortho_dot = abs(float(np.sum(np.conj(ground_psi) * excited_psi) * dV))

    # (A) Axis-agnostic anisotropy via covariance
    rho = excited_dens / (np.sum(excited_dens) * dV + 1e-12)
    cx = np.sum(X * rho) * dV
    cy = np.sum(Y * rho) * dV
    Mxx = np.sum((X - cx)**2 * rho) * dV
    Myy = np.sum((Y - cy)**2 * rho) * dV
    Mxy = np.sum((X - cx) * (Y - cy) * rho) * dV
    trace = Mxx + Myy
    det = Mxx * Myy - Mxy**2
    disc = max(trace**2 / 4 - det, 0)
    lam1 = trace / 2 + np.sqrt(disc)
    lam2 = trace / 2 - np.sqrt(disc)
    anisotropy = float((lam1 - lam2) / (lam1 + lam2 + 1e-12))

    # (B) Center-dip check
    c_idx = size // 2
    center_val = excited_dens[c_idx, c_idx]
    peak_val = np.max(excited_dens)
    center_dip = float(center_val / (peak_val + 1e-12))

    ground_no_nan = 1.0 if not np.isnan(np.sum(ground_psi)) else 0.0

    measured = {
        "ortho_dot": ortho_dot,
        "anisotropy": anisotropy,
        "center_dip": center_dip,
        "ground_no_nan": ground_no_nan,
    }
    exp_results, overall_pass = evaluate_expectations(RA3_EXPECTATIONS, measured)

    manifest = {
        "run_id": f"ra3_{int(time.time())}",
        "git": get_git_info(),
        "timestamp": time.time(),
        "scenario": "ra3",
        "config": {"grid": size, "Z": Z, "eps": eps, "itp_steps": 100},
        "overall_pass": overall_pass,
        "ortho_dot": ortho_dot,
        "anisotropy": anisotropy,
        "center_dip": center_dip,
    }
    return {
        "manifest": manifest,
        "expectations": RA3_EXPECTATIONS,
        "expectation_results": exp_results,
        "overall_pass": overall_pass,
        "ground_dens": ground_dens,
        "excited_dens": excited_dens,
        "final_V": V,
        "explain_pack": get_explain_pack("ra3", overall_pass)
    }


def run_ra4_mu_memory():
    """RA-4: μ Memory Imprint — verify μ grows but stays bounded (Lineum-only)."""
    size = 64
    x = np.linspace(-1, 1, size)
    dx = 2.0 / size
    dV = dx * dx
    X, Y = np.meshgrid(x, x)
    R = np.sqrt(X**2 + Y**2)
    Z, eps = 1.0, 0.1
    V = -Z / np.sqrt(R**2 + eps**2)
    phi_pot = np.clip(-V * 100, 0, 1000)
    kappa = np.ones((size, size), dtype=np.float64)

    psi = np.exp(-R**2 / 0.5).astype(np.complex128)
    psi /= np.sqrt(np.sum(np.abs(psi)**2) * dV)
    mu = np.zeros((size, size), dtype=np.float64)
    state = {"psi": psi, "phi": phi_pot, "kappa": kappa, "mu": mu}

    mu_cap = 10.0
    cfg = CoreConfig(dt=0.1, physics_mode_psi="diffusion", use_mode_coupling=False,
                    use_mu=True, mu_eta=0.005, mu_rho=0.0001, mu_cap=mu_cap)

    mu_max_series = []
    # Diffusion phase
    for _ in range(100):
        state = step_core(state, cfg)
        state["psi"] /= np.sqrt(np.sum(np.abs(state["psi"])**2) * dV)
        mu_max_series.append(float(np.max(state["mu"])))

    # Wave phase
    cfg_wave = CoreConfig(dt=0.005, physics_mode_psi="wave_baseline", use_mode_coupling=False,
                         use_mu=True, mu_eta=0.005, mu_rho=0.0001, mu_cap=mu_cap)
    for _ in range(50):
        state = step_core(state, cfg_wave)
        mu_max_series.append(float(np.max(state["mu"])))

    mu_final = state["mu"]
    mu_max_final = float(np.max(mu_final))
    psi_dens = np.abs(state["psi"])**2

    # Verdict
    mu_max_bounded = 1.0 if mu_max_final < mu_cap * 0.99 else 0.0
    mu_grows = 1.0 if mu_max_final > 0.01 else 0.0
    mu_has_no_nan = 1.0 if not np.isnan(np.sum(mu_final)) else 0.0

    # Determine verdict string
    if mu_max_final >= mu_cap * 0.99:
        verdict = "runaway"
    elif mu_max_series[-1] > mu_max_series[-10] * 1.05:
        verdict = "saturating"
    else:
        verdict = "stable"

    measured = {"mu_max_bounded": mu_max_bounded, "mu_grows": mu_grows, "mu_has_no_nan": mu_has_no_nan}
    exp_results, overall_pass = evaluate_expectations(RA4_EXPECTATIONS, measured)

    manifest = {
        "run_id": f"ra4_{int(time.time())}",
        "git": get_git_info(),
        "timestamp": time.time(),
        "scenario": "ra4",
        "config": {"grid": size, "Z": Z, "eps": eps, "mu_eta": 0.005, "mu_cap": mu_cap,
                   "diff_steps": 100, "wave_steps": 50},
        "overall_pass": overall_pass,
        "verdict": verdict,
    }
    return {
        "manifest": manifest,
        "expectations": RA4_EXPECTATIONS,
        "expectation_results": exp_results,
        "overall_pass": overall_pass,
        "mu_field": mu_final,
        "psi_dens": psi_dens,
        "mu_max_series": mu_max_series,
        "verdict": verdict,
        "explain_pack": get_explain_pack("ra4", overall_pass)
    }


def run_ra5_driving():
    """RA-5: Driving vs Dephasing — compare Linon forcing ON vs OFF (Lineum-only)."""
    size = 64
    x = np.linspace(-1, 1, size)
    dx = 2.0 / size
    dV = dx * dx
    X, Y = np.meshgrid(x, x)
    R = np.sqrt(X**2 + Y**2)

    psi_init = np.exp(-R**2 / 0.3).astype(np.complex128)
    psi_init /= np.sqrt(np.sum(np.abs(psi_init)**2) * dV)
    kappa = np.ones((size, size), dtype=np.float64)
    phi = np.zeros((size, size), dtype=np.float64)

    n_steps = 50

    # Run A: Driving ON (standard Lineum)
    state_a = {"psi": psi_init.copy(), "phi": phi.copy(), "kappa": kappa.copy()}
    cfg_driven = CoreConfig(dt=0.005, physics_mode_psi="wave_baseline", use_mode_coupling=False,
                           noise_strength=0.005, reaction_strength=0.0007)
    N_driven = []
    for _ in range(n_steps):
        state_a = step_core(state_a, cfg_driven)
        N_driven.append(float(np.sum(np.abs(state_a["psi"])**2) * dV))

    # Run B: Driving OFF (no noise, no reaction)
    state_b = {"psi": psi_init.copy(), "phi": phi.copy(), "kappa": kappa.copy()}
    cfg_undriven = CoreConfig(dt=0.005, physics_mode_psi="wave_baseline", use_mode_coupling=False,
                             noise_strength=0.0, reaction_strength=0.0)
    N_undriven = []
    for _ in range(n_steps):
        state_b = step_core(state_b, cfg_undriven)
        N_undriven.append(float(np.sum(np.abs(state_b["psi"])**2) * dV))

    N0 = float(np.sum(np.abs(psi_init)**2) * dV)
    delta_N_driven = N_driven[-1] - N0 if N_driven else 0
    delta_N_undriven = abs(N_undriven[-1] - N0) if N_undriven else 1

    driven_energy_positive = 1.0 if delta_N_driven > 0.001 else 0.0
    undriven_stable = 1.0 if delta_N_undriven < 0.05 else 0.0

    measured = {"driven_energy_positive": driven_energy_positive, "undriven_stable": undriven_stable}
    exp_results, overall_pass = evaluate_expectations(RA5_EXPECTATIONS, measured)

    manifest = {
        "run_id": f"ra5_{int(time.time())}",
        "git": get_git_info(),
        "timestamp": time.time(),
        "scenario": "ra5",
        "config": {"grid": size, "steps": n_steps, "dt": 0.005},
        "overall_pass": overall_pass,
        "delta_N_driven": delta_N_driven,
        "delta_N_undriven": delta_N_undriven,
    }
    return {
        "manifest": manifest,
        "expectations": RA5_EXPECTATIONS,
        "expectation_results": exp_results,
        "overall_pass": overall_pass,
        "N_driven": N_driven,
        "N_undriven": N_undriven,
        "explain_pack": get_explain_pack("ra5", overall_pass)
    }


def run_ra6_lpf_impact():
    """RA-6: LPF Impact — compare wave_projected_soft with LPF ON vs OFF (Lineum-only)."""
    size = 64
    x = np.linspace(-1, 1, size)
    dx = 2.0 / size
    dV = dx * dx
    X, Y = np.meshgrid(x, x)
    R = np.sqrt(X**2 + Y**2)
    Z, eps = 1.0, 0.1
    V = -Z / np.sqrt(R**2 + eps**2)
    phi_pot = np.clip(-V * 100, 0, 1000)
    kappa = np.ones((size, size), dtype=np.float64)

    # Prepare ground state first
    psi_init = np.exp(-R**2 / 0.5).astype(np.complex128)
    state_init = {"psi": psi_init, "phi": phi_pot.copy(), "kappa": kappa.copy()}
    cfg_itp = CoreConfig(dt=0.1, physics_mode_psi="diffusion", use_mode_coupling=False)
    for _ in range(100):
        state_init = step_core(state_init, cfg_itp)
        state_init["psi"] /= np.sqrt(np.sum(np.abs(state_init["psi"])**2) * dV)

    n_steps = 50

    def run_variant(lpf_on):
        state = {"psi": state_init["psi"].copy(), "phi": phi_pot.copy(), "kappa": kappa.copy()}
        cfg = CoreConfig(dt=0.005, physics_mode_psi="wave_projected_soft", use_mode_coupling=False,
                        wave_lpf_enabled=lpf_on, wave_lpf_cutoff=0.35)
        E_series = []
        N_series = []
        for step in range(n_steps):
            state = step_core(state, cfg)
            dens = np.abs(state["psi"])**2
            N_curr = np.sum(dens) * dV
            gx, gy = np.gradient(state["psi"], dx, dx)
            E_curr = np.sum(np.abs(gx)**2 + np.abs(gy)**2) * dV + np.sum(V * dens) * dV
            E_series.append(float(E_curr))
            N_series.append(float(N_curr))
        is_stable = not np.isnan(np.sum(state["psi"])) and np.max(np.abs(state["psi"])) < 1e5
        return E_series, N_series, is_stable

    E_off, N_off, stable_off = run_variant(False)
    E_on, N_on, stable_on = run_variant(True)

    # LPF changes dynamics = significant difference in final energy
    e_diff = abs(E_on[-1] - E_off[-1]) / (abs(E_off[-1]) + 1e-9) if E_off and E_on else 0
    lpf_changes = 1.0 if e_diff > 0.005 else 0.0
    both_stable = 1.0 if (stable_off and stable_on) else 0.0

    measured = {"lpf_changes_dynamics": lpf_changes, "both_runs_stable": both_stable}
    exp_results, overall_pass = evaluate_expectations(RA6_EXPECTATIONS, measured)

    manifest = {
        "run_id": f"ra6_{int(time.time())}",
        "git": get_git_info(),
        "timestamp": time.time(),
        "scenario": "ra6",
        "config": {"grid": size, "Z": Z, "eps": eps, "steps": n_steps, "dt": 0.005},
        "overall_pass": overall_pass,
        "energy_diff_pct": float(e_diff * 100),
    }
    return {
        "manifest": manifest,
        "expectations": RA6_EXPECTATIONS,
        "expectation_results": exp_results,
        "overall_pass": overall_pass,
        "E_off": E_off,
        "E_on": E_on,
        "N_off": N_off,
        "N_on": N_on,
        "explain_pack": get_explain_pack("ra6", overall_pass)
    }
