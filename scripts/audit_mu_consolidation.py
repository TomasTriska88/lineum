import numpy as np
import time
import os
import zlib
import json
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter

# Import the core engine logic to copy/paste exactly from math.py, 
# ensuring we use the exact current Eq-4' numerics.
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from lineum_core.math import (
    USE_PYTORCH, evolve, PSI_AMP_CAP, GRAD_CAP, PHI_CAP, 
    _cap_complex_magnitude, _finite_clip, _finite_complex,
    diffuse_complex, diffuse_real, sigmoid,
    NOISE_STRENGTH, PHI_INTERACTION_CAP, DRIFT_STRENGTH, DISSIPATION_RATE,
    PSI_DIFFUSION, REACTION_STRENGTH, PHI_DIFFUSION, DT,
    ENABLE_INTERACTION, ENABLE_PHI_FLOW, ENABLE_NOISE, TEST_EXHALE_MODE
)

print(f"Using PyTorch: {USE_PYTORCH}")

# --- STRICT AUDIT PARAMS ---
GRID_SIZE = 128
TICKS_PER_CHUNK = 200
CHUNKS = 15
SEED = 42

# Ensure reproducibility
np.random.seed(SEED)
if USE_PYTORCH:
    import torch
    torch.manual_seed(SEED)

def generate_packet():
    """Generates a fixed deterministic text/semantic perturbation packet."""
    packet = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.complex128)
    for _ in range(30):
        x = np.random.randint(20, GRID_SIZE - 20)
        y = np.random.randint(20, GRID_SIZE - 20)
        amp = np.random.uniform(5.0, 15.0)
        phase = np.random.uniform(-np.pi, np.pi)
        packet[x, y] = amp * np.exp(1j * phase)
    # Smooth it slightly so it's a structural impulse, not just dirac pixels
    packet = gaussian_filter(packet.real, sigma=2.0) + 1j * gaussian_filter(packet.imag, sigma=2.0)
    return packet

FIXED_PACKET = generate_packet()

def generate_kappa():
    kappa = np.ones((GRID_SIZE, GRID_SIZE), dtype=np.float64)
    for _ in range(5):
        cx, cy = np.random.randint(20, 108, 2)
        radius = np.random.randint(5, 15)
        y, x = np.ogrid[-cx:GRID_SIZE-cx, -cy:GRID_SIZE-cy]
        mask = x*x + y*y <= radius*radius
        kappa[mask] = 0.05
    return kappa

FIXED_KAPPA = generate_kappa()

def calc_novelty(phi_curr, phi_prev):
    """
    Geometrical jitter (L1 diff normalized).
    novelty_vs_prev = sum(|phi_t - phi_t-1|) / sum(phi_t)
    """
    diff_sum = np.sum(np.abs(phi_curr - phi_prev))
    total_mass = np.sum(phi_curr) + 1e-8
    return float(diff_sum / total_mass)

def calc_compression(phi_curr):
    """
    GZIP array size serving as a proxy for topographical scale complexity.
    """
    # Round to avoid float noise dominating the gzip
    rounded = np.round(phi_curr, decimals=2)
    csv_bytes = ",".join(map(str, rounded.flatten())).encode('utf-8')
    return len(zlib.compress(csv_bytes))

def create_initial_state():
    psi = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.complex128)
    phi = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.float64)
    delta = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.float64)
    mu = np.full((GRID_SIZE, GRID_SIZE), 0.1, dtype=np.float64) # mu_0 = 0.1
    return psi, phi, delta, mu

# ======================================================================
# EXACT EQ-4' CORE (No modifications, extracted for isolated tracking)
# ======================================================================
def evolve_baseline(psi, delta, phi, kappa):
    """Passthrough to the exact canonical math.py equation."""
    return evolve(psi, delta, phi, kappa)

# ======================================================================
# V2 EXTENSION: Eq-4' + \mu
# ======================================================================
def evolve_v2_mu(psi, delta, phi, kappa, mu, eta, rho, mu_0):
    """
    The strictly bounded Eq-4' + \mu V2 implementation.
    Rule 1: \mu does NOT touch \kappa.
    Rule 2: \mu does NOT touch diffuse(\psi).
    Rule 3: \mu only enters drift and reaction coupling on \phi.
    """
    size = psi.shape[0]

    # --- 1) Step the Core Eq-4' fields ---
    # We must implement the NumPy loop manually here so we can inject \mu.
    # (Extracting exactly from math.py's _evolve_numpy logic)
    
    psi = _finite_complex(psi, nan=0.0)
    phi = _finite_clip(phi, lo=0.0, hi=PHI_CAP, nan=0.0, posinf=PHI_CAP, neginf=0.0, dtype=np.float64)
    mu = _finite_clip(mu, lo=0.0, hi=1.0, nan=0.0, posinf=1.0, neginf=0.0, dtype=np.float64)

    amp = np.abs(psi).astype(np.float64, copy=False)
    amp = _finite_clip(amp, lo=0.0, hi=PSI_AMP_CAP, nan=0.0, posinf=PSI_AMP_CAP, neginf=0.0)

    grad_x, grad_y = np.gradient((amp + delta).astype(np.float64, copy=False))
    grad_x = _finite_clip(grad_x, lo=-GRAD_CAP, hi=GRAD_CAP, nan=0.0, posinf=GRAD_CAP, neginf=-GRAD_CAP)
    grad_y = _finite_clip(grad_y, lo=-GRAD_CAP, hi=GRAD_CAP, nan=0.0, posinf=GRAD_CAP, neginf=-GRAD_CAP)
    grad_mag = np.sqrt(np.clip(grad_x*grad_x + grad_y*grad_y, 0.0, 1e12))
    
    probability = sigmoid(amp + grad_mag) * kappa
    random_field = np.random.rand(size, size)
    linons = (random_field < probability).astype(float)
    linon_base = 0.01 if TEST_EXHALE_MODE else 0.03
    linon_scaling = 0.01 if TEST_EXHALE_MODE else 0.02
    linon_effect = np.clip((linon_base + linon_scaling * amp.clip(min=0)) * linons, 0.0, 10.0)
    linon_complex = linon_effect * np.exp(1j * np.angle(psi))

    fluctuation = np.clip(np.random.normal(0.0, NOISE_STRENGTH, (size, size)), -1.0, 1.0) * np.exp(1j * np.angle(psi))
    fluctuation = fluctuation if ENABLE_NOISE else np.zeros_like(psi)

    phi_int = _finite_clip(phi, lo=0.0, hi=float(PHI_INTERACTION_CAP), nan=0.0, posinf=float(PHI_INTERACTION_CAP), neginf=0.0, dtype=np.float64)
    
    # -------------------------------------------------------------
    # V2 MODULATION 1: INTERACTION TETHERING
    # The \mu field acts as an anchor for the interaction probability,
    # gently coaxing established phase locks.
    # We modulate the interaction factor by (1.0 + \mu). 
    # Bounded so it never causes runaway feedback.
    # -------------------------------------------------------------
    mu_bias = 1.0 + mu  # Ranges 1.0 -> 2.0 safely
    interaction_factor = 0.1 * np.tanh((0.04 * phi_int * kappa * mu_bias) / 0.1)
    
    interaction_term = interaction_factor * psi
    int_mag = np.abs(interaction_term)
    interaction_term = interaction_term / (1.0 + int_mag / 10.0)
    interaction_term = interaction_term if ENABLE_INTERACTION else np.zeros_like(psi)

    # -------------------------------------------------------------
    # V2 MODULATION 2: DRIFT TRENCHING (\mu explicitly shapes the current)
    # The gradient is taken over (\phi + c * \mu), carving a physical 
    # slipstream that pulls \psi into the historical scar.
    # -------------------------------------------------------------
    grad_phi_x, grad_phi_y = np.gradient(phi + 0.5 * mu) 
    
    phi_flow_term = DRIFT_STRENGTH * (grad_phi_x + 1j * grad_phi_y) * kappa
    flow_mag = np.abs(phi_flow_term)
    phi_flow_term = phi_flow_term / (1.0 + flow_mag / 10.0)
    phi_flow_term = phi_flow_term if ENABLE_PHI_FLOW else np.zeros_like(psi)
    
    psi += phi_flow_term * DT
    psi = _cap_complex_magnitude(psi, PSI_AMP_CAP)
    psi += ((linon_complex + fluctuation) * kappa + interaction_term) * DT
    psi -= DISSIPATION_RATE * psi * DT
    psi += diffuse_complex(psi, kappa, rate=PSI_DIFFUSION) * kappa * DT

    # Eq-4' safe soft bounding
    amp2 = np.clip(np.abs(psi).astype(np.float64, copy=False), 0.0, 100.0)
    local_input = np.clip(amp2 * amp2, 0.0, 1e4)
    scale_ratio = (128.0 / size) ** 2
    dynamic_reaction = REACTION_STRENGTH * scale_ratio

    phi += kappa * dynamic_reaction * (local_input - phi)
    phi += kappa * PHI_DIFFUSION * diffuse_real(phi, kappa, rate=0.05)

    psi = _finite_complex(psi, nan=0.0)
    phi = _finite_clip(phi, lo=0.0, hi=PHI_CAP, nan=0.0, posinf=PHI_CAP, neginf=0.0, dtype=np.float64)
    psi = _cap_complex_magnitude(psi, PSI_AMP_CAP)

    # -------------------------------------------------------------
    # V2 HDD UPDATE: \mu KINEMATICS
    # \partial \mu / \partial t = \eta \cdot |\Psi|^2 - \rho \cdot (\mu - \mu_0)
    # -------------------------------------------------------------
    traffic = local_input # |\Psi|^2 (capped at 1e4)
    d_mu = (eta * traffic) - (rho * (mu - mu_0))
    mu += d_mu * DT
    mu = np.clip(mu, 0.0, 1.0) # Absolute hard bound on \mu memory

    # FailSafe
    if np.isnan(np.sum(psi)) or np.max(np.abs(psi)) >= PSI_AMP_CAP * 0.99:
        print("!!! LINEUM FAIL-SAFE: Numeric divergence detected. !!!")
        psi = np.zeros_like(psi)

    return psi, phi, mu


def run_audit(mode_name, eta_param=0.0, rho_param=0.0):
    print(f"\\n[{mode_name}] Starting Ablation Run...")
    psi, phi, delta, mu = create_initial_state()
    
    logs = {
        'novelty': [],
        'compression': [],
        'drift_mu': [],
        'sbr': [],
        'nan_events': 0,
        'sbr_spikes': 0
    }
    
    mu_0 = 0.1
    # Run chunks (simulating conversational turns)
    for c in range(CHUNKS):
        # 1. Stimulus Injection (Every chunk)
        psi += FIXED_PACKET
        
        chunk_phi_prev = phi.copy()
        chunk_mu_prev = mu.copy()
        
        # 2. Relax (Tick)
        for t in range(TICKS_PER_CHUNK):
            if mode_name == "BASELINE":
                psi, phi = evolve_baseline(psi, delta, phi, FIXED_KAPPA)
            else:
                psi, phi, mu = evolve_v2_mu(psi, delta, phi, FIXED_KAPPA, mu, eta=eta_param, rho=rho_param, mu_0=mu_0)
            
            # Sub-tick diagnostics check
            sbr = np.max(np.abs(psi)) / (np.mean(np.abs(psi)) + 1e-8)
            if np.isnan(sbr) or np.isnan(np.sum(phi)):
                logs['nan_events'] += 1
            if sbr > 1e5:
                logs['sbr_spikes'] += 1
                
        # 3. Post-Chunk Log (Measure consolidation and shift)
        nov = calc_novelty(phi, chunk_phi_prev)
        comp = calc_compression(phi)
        
        drift = float(np.sum(np.abs(mu - chunk_mu_prev)))
        sbr = float(np.max(np.abs(psi)) / (np.mean(np.abs(psi)) + 1e-8))
        
        logs['novelty'].append(nov)
        logs['compression'].append(comp)
        logs['drift_mu'].append(drift)
        logs['sbr'].append(sbr)
        
        print(f"  Chunk {c:02d} | Nov: {nov:.4f} | Comp: {comp} bytes | dMu: {drift:.2f} | SBR: {sbr:.1f}")

    return {
        'logs': logs,
        'final_phi': phi.copy(),
        'final_mu': mu.copy()
    }

if __name__ == "__main__":
    
    # 1. Baseline Eq-4' Run
    base_results = run_audit("BASELINE")
    
    # 2. Minimal \mu Injection V2 (Stable params hypothesis)
    eta_stable = 0.005  # Slow write
    rho_stable = 0.0001 # Micro-decay
    v2_results = run_audit("V2_Eq4_Mu", eta_param=eta_stable, rho_param=rho_stable)
    
    # 3. Aggressive/Unstable \mu (Runaway checks)
    eta_agg = 0.1
    rho_agg = 0.00001
    agg_results = run_audit("V2_AGGRESSIVE", eta_param=eta_agg, rho_param=rho_agg)
    
    # Save the data
    output_dir = os.path.join(os.path.dirname(__file__), '..', 'output_audit_mu')
    os.makedirs(output_dir, exist_ok=True)
    
    with open(os.path.join(output_dir, 'mu_audit_metrics.json'), 'w') as f:
        json.dump({
            'baseline': base_results['logs'],
            'v2_stable': v2_results['logs'],
            'v2_aggressive': agg_results['logs']
        }, f, indent=2)
        
    print(f"\\nAudit complete. Data saved to {output_dir}")
    
    # Generate Visuals
    plt.figure(figsize=(12, 10))
    
    # 1) Novelty
    plt.subplot(2, 2, 1)
    plt.plot(base_results['logs']['novelty'], label="Baseline Eq-4'", color='gray')
    plt.plot(v2_results['logs']['novelty'], label="Eq-4'+μ (V2)", color='blue')
    plt.plot(agg_results['logs']['novelty'], label="Aggressive (V2)", color='red', linestyle='--')
    plt.title("Consolidation (Novelty Jitter vs Prev)")
    plt.xlabel("Interaction Chunk")
    plt.ylabel("Jitter (Lower=Consolidated, 0=Frozen)")
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # 2) Compression
    plt.subplot(2, 2, 2)
    plt.plot(base_results['logs']['compression'], label="Baseline Eq-4'", color='gray')
    plt.plot(v2_results['logs']['compression'], label="Eq-4'+μ (V2)", color='blue')
    plt.title("Information Density (GZIP bytes)")
    plt.xlabel("Interaction Chunk")
    plt.ylabel("Bytes (Higher=Complex Routes)")
    plt.legend()
    plt.grid(True, alpha=0.3)

    # 3) SBR Stability
    plt.subplot(2, 2, 3)
    plt.plot(base_results['logs']['sbr'], label="Baseline Eq-4'", color='gray')
    plt.plot(v2_results['logs']['sbr'], label="Eq-4'+μ (V2)", color='blue')
    plt.title("Numerical Stability (SBR)")
    plt.yscale('log')
    plt.xlabel("Interaction Chunk")
    plt.axhline(1e5, color='r', linestyle=':', label='Spike Boundary')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # 4) Drift Mu
    plt.subplot(2, 2, 4)
    plt.plot(v2_results['logs']['drift_mu'], label="Eq-4'+μ (V2) $\\Delta\\mu$", color='blue')
    plt.title("Historical Writing Rate (L1 $\\Delta\\mu$)")
    plt.xlabel("Interaction Chunk")
    plt.ylabel("Macro change in memory")
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'mu_ablation_curves.png'))
    print("Graphs saved.")
    
    # Summary Check
    print("\\n----- ABLATION CONCLUSION -----")
    if base_results['logs']['nan_events'] == 0 and v2_results['logs']['nan_events'] == 0:
        print("[PASS] Numeric runaways contained. No NaNs.")
        
    fin_nov_base = base_results['logs']['novelty'][-1]
    fin_nov_v2 = v2_results['logs']['novelty'][-1]
    
    if fin_nov_v2 < fin_nov_base and fin_nov_v2 > 0.001:
        print(f"[PASS] Consolidation verified. V2 ({fin_nov_v2:.4f}) is more stable than Base ({fin_nov_base:.4f}) but not FROZEN.")
    elif fin_nov_v2 <= 0.001:
        print(f"[FAIL] Thermal Death Detected! V2 froze rigid: {fin_nov_v2:.4f}")
    else:
        print(f"[FAIL] V2 failed to consolidate better than Base.")
        
    fin_comp_base = base_results['logs']['compression'][-1]
    fin_comp_v2 = v2_results['logs']['compression'][-1]
    if fin_comp_v2 > fin_comp_base:
        print(f"[PASS] Complexity growth verified. V2 topography holds ({fin_comp_v2}b) > Base ({fin_comp_base}b).")
    else:
        print(f"[FAIL] V2 memory flattened instead of growing compared to baseline.")
