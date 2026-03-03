import numpy as np
import os
import json
import zlib
from scipy.ndimage import gaussian_filter
from scipy import stats
import matplotlib.pyplot as plt

# Import the exact Eq-4' physics
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

print(f"Using PyTorch for Canon Audit: {USE_PYTORCH}")

# --- STRICT AUDIT PARAMS ---
GRID_SIZE = 128
TICKS_PER_CHUNK = 100 # Reduced slightly for large statistical sweeps

# V2 Params
ETA_STABLE = 0.005  
RHO_STABLE = 0.0001
MU_0 = 0.1

def generate_packet(seed):
    """Generates a deterministic semantic perturbation packet based on seed."""
    np.random.seed(seed)
    packet = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.complex128)
    for _ in range(30):
        x = np.random.randint(20, GRID_SIZE - 20)
        y = np.random.randint(20, GRID_SIZE - 20)
        amp = np.random.uniform(5.0, 15.0)
        phase = np.random.uniform(-np.pi, np.pi)
        packet[x, y] = amp * np.exp(1j * phase)
    return gaussian_filter(packet.real, sigma=2.0) + 1j * gaussian_filter(packet.imag, sigma=2.0)

def generate_kappa(seed):
    np.random.seed(seed + 100)
    kappa = np.ones((GRID_SIZE, GRID_SIZE), dtype=np.float64)
    for _ in range(5):
        cx, cy = np.random.randint(20, 108, 2)
        radius = np.random.randint(5, 15)
        y, x = np.ogrid[-cx:GRID_SIZE-cx, -cy:GRID_SIZE-cy]
        mask = x*x + y*y <= radius*radius
        kappa[mask] = 0.05
    return kappa

def calc_novelty(phi_curr, phi_prev):
    diff_sum = np.sum(np.abs(phi_curr - phi_prev))
    return float(diff_sum / (np.sum(phi_curr) + 1e-8))

def calc_compression(phi_curr):
    rounded = np.round(phi_curr, decimals=2)
    return len(zlib.compress(",".join(map(str, rounded.flatten())).encode('utf-8')))

def calc_mae(phi_a, phi_b):
    return float(np.mean(np.abs(phi_a - phi_b)))

def evolve_v2_mu(psi, delta, phi, kappa, mu, eta, rho, mu_0):
    """Strictly bounded Eq-4' + \mu V2 implementation. (Exactly as spec'd)."""
    size = psi.shape[0]
    
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
    linons = (np.random.rand(size, size) < probability).astype(float)
    linon_effect = np.clip((0.03 + 0.02 * amp.clip(min=0)) * linons, 0.0, 10.0)
    linon_complex = linon_effect * np.exp(1j * np.angle(psi))
    fluctuation = np.clip(np.random.normal(0.0, NOISE_STRENGTH, (size, size)), -1.0, 1.0) * np.exp(1j * np.angle(psi))

    phi_int = _finite_clip(phi, lo=0.0, hi=float(PHI_INTERACTION_CAP), nan=0.0, posinf=float(PHI_INTERACTION_CAP), neginf=0.0, dtype=np.float64)
    
    # \mu Mod 1: Interaction
    mu_bias = 1.0 + mu
    interaction_factor = 0.1 * np.tanh((0.04 * phi_int * kappa * mu_bias) / 0.1)
    interaction_term = interaction_factor * psi
    interaction_term = interaction_term / (1.0 + np.abs(interaction_term) / 10.0)
    
    # \mu Mod 2: Drift
    grad_phi_x, grad_phi_y = np.gradient(phi + 0.5 * mu) 
    phi_flow_term = DRIFT_STRENGTH * (grad_phi_x + 1j * grad_phi_y) * kappa
    phi_flow_term = phi_flow_term / (1.0 + np.abs(phi_flow_term) / 10.0)
    
    psi += phi_flow_term * DT
    psi = _cap_complex_magnitude(psi, PSI_AMP_CAP)
    psi += ((linon_complex + fluctuation) * kappa + interaction_term) * DT
    psi -= DISSIPATION_RATE * psi * DT
    psi += diffuse_complex(psi, kappa, rate=PSI_DIFFUSION) * kappa * DT

    amp2 = np.clip(np.abs(psi).astype(np.float64, copy=False), 0.0, 100.0)
    local_input = np.clip(amp2 * amp2, 0.0, 1e4)
    dynamic_reaction = REACTION_STRENGTH * ((128.0 / size) ** 2)

    phi += kappa * dynamic_reaction * (local_input - phi)
    phi += kappa * PHI_DIFFUSION * diffuse_real(phi, kappa, rate=0.05)

    psi = _finite_complex(psi, nan=0.0)
    phi = _finite_clip(phi, lo=0.0, hi=PHI_CAP, nan=0.0, posinf=PHI_CAP, neginf=0.0, dtype=np.float64)
    psi = _cap_complex_magnitude(psi, PSI_AMP_CAP)

    # HDD Update
    d_mu = (eta * local_input) - (rho * (mu - mu_0))
    mu = np.clip(mu + d_mu * DT, 0.0, 1.0)

    # FailSafe
    if np.isnan(np.sum(psi)) or np.max(np.abs(psi)) >= PSI_AMP_CAP * 0.99:
        psi = np.zeros_like(psi)

    return psi, phi, mu

def run_single_ablation(seed, mode="V2"):
    """Runs one full trace and returns the final metrics."""
    np.random.seed(seed)
    if USE_PYTORCH:
        import torch
        torch.manual_seed(seed)
        
    packet = generate_packet(seed)
    kappa = generate_kappa(seed)
    
    psi = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.complex128)
    phi = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.float64)
    delta = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.float64)
    mu = np.full((GRID_SIZE, GRID_SIZE), MU_0, dtype=np.float64)
    
    novelties = []
    compressions = []
    
    for c in range(15):
        psi += packet
        chunk_phi_prev = phi.copy()
        
        for t in range(TICKS_PER_CHUNK):
            if mode == "BASELINE":
                psi, phi = evolve(psi, delta, phi, kappa)
            else:
                psi, phi, mu = evolve_v2_mu(psi, delta, phi, kappa, mu, ETA_STABLE, RHO_STABLE, MU_0)
                
        novelties.append(calc_novelty(phi, chunk_phi_prev))
        compressions.append(calc_compression(phi))
        
    return novelties, compressions

# ======================================================================
# TEST 1: STATISTICAL SIGNIFICANCE (MULTI-SEED)
# ======================================================================
def test_statistical_significance(N=30):
    print(f"\\n[Test 1] Running Statistical Significance Audit (N={N})...")
    base_nov = []
    base_comp = []
    v2_nov = []
    v2_comp = []
    
    for i in range(N):
        sys.stdout.write(f"\\r  Processing Seed {i+1}/{N}...")
        sys.stdout.flush()
        
        bn, bc = run_single_ablation(i, "BASELINE")
        vn, vc = run_single_ablation(i, "V2")
        
        # Take the final chunk metrics
        base_nov.append(bn[-1])
        base_comp.append(bc[-1])
        v2_nov.append(vn[-1])
        v2_comp.append(vc[-1])
        
    print()
    
    # Calculate Mean and Std
    bn_mean, bn_std = np.mean(base_nov), np.std(base_nov)
    vn_mean, vn_std = np.mean(v2_nov), np.std(v2_nov)
    
    bc_mean, bc_std = np.mean(base_comp), np.std(base_comp)
    vc_mean, vc_std = np.mean(v2_comp), np.std(v2_comp)
    
    # T-Test (Independent)
    t_nov, p_nov = stats.ttest_ind(v2_nov, base_nov, equal_var=False)
    t_comp, p_comp = stats.ttest_ind(v2_comp, base_comp, equal_var=False)
    
    res = {
        'N': N,
        'novelty': {
            'baseline': {'mean': float(bn_mean), 'std': float(bn_std)},
            'v2': {'mean': float(vn_mean), 'std': float(vn_std)},
            't_stat': float(t_nov), 'p_value': float(p_nov)
        },
        'compression': {
            'baseline': {'mean': float(bc_mean), 'std': float(bc_std)},
            'v2': {'mean': float(vc_mean), 'std': float(vc_std)},
            't_stat': float(t_comp), 'p_value': float(p_comp)
        }
    }
    
    for k, v in res.items():
        if k != 'N':
            print(f"  {k.capitalize()}: Base={v['baseline']['mean']:.4f}±{v['baseline']['std']:.4f} | V2={v['v2']['mean']:.4f}±{v['v2']['std']:.4f} | p={v['p_value']:.2e}")
            
    return res

# ======================================================================
# TEST 2: MEMORY RETENTION TEST (HDD RESILIENCE)
# Sequences: A (Learn) -> B (Chaos) -> A (Recall)
# ======================================================================
def run_retention_test(seed=42):
    print(f"\\n[Test 2] Running Memory Retention Test (Seed={seed})...")
    np.random.seed(seed)
    
    packet_A = generate_packet(seed)      # Core Concept
    packet_B = generate_packet(seed+99)   # Disruptive Concept
    kappa = generate_kappa(seed)
    
    def simulate_sequence(mode):
        psi = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.complex128)
        phi = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.float64)
        delta = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.float64)
        mu = np.full((GRID_SIZE, GRID_SIZE), MU_0, dtype=np.float64)
        
        def run_phase(packet, iterations):
            nonlocal psi, phi, mu
            for _ in range(iterations):
                psi += packet
                for t in range(TICKS_PER_CHUNK):
                    if mode == "BASELINE":
                        psi, phi = evolve(psi, delta, phi, kappa)
                    else:
                        psi, phi, mu = evolve_v2_mu(psi, delta, phi, kappa, mu, ETA_STABLE, RHO_STABLE, MU_0)
            return phi.copy()
            
        # 1. Learn Phase (A)
        phi_learn = run_phase(packet_A, 10)
        
        # 2. Chaos/Disruption Phase (B)
        phi_chaos = run_phase(packet_B, 10)
        
        # 3. Recall Phase (A)
        phi_recall = run_phase(packet_A, 5)
        
        # Return-to-Basin MAE (How close is Recall to the originally Learned state?)
        rtb_score = calc_mae(phi_learn, phi_recall)
        
        return rtb_score, phi_learn, phi_chaos, phi_recall
        
    rtb_base, _, _, _ = simulate_sequence("BASELINE")
    rtb_v2, _, _, _ = simulate_sequence("V2")
    
    print(f"  Return-to-Basin MAE (Lower is better):")
    print(f"  Baseline Eq-4':  {rtb_base:.4f}")
    print(f"  Eq-4'+mu (V2):   {rtb_v2:.4f}")
    
    return {'baseline_mae': float(rtb_base), 'v2_mae': float(rtb_v2)}

# ======================================================================
# TEST 3: PARAMETER SWEEP MAP
# ======================================================================
def run_parameter_sweep():
    print(f"\\n[Test 3] Running Parameter Sweep (Stability Envelope)...")
    etas = [0.001, 0.005, 0.02, 0.1]
    rhos = [0.00001, 0.0001, 0.001]
    
    results = []
    
    for e in etas:
        for r in rhos:
            sys.stdout.write(f"\\r  Testing eta={e}, rho={r}... ")
            sys.stdout.flush()
            
            # Run short burst
            packet = generate_packet(1)
            kappa = generate_kappa(1)
            psi, phi, delta = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.complex128), np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.float64), np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.float64)
            mu = np.full((GRID_SIZE, GRID_SIZE), MU_0, dtype=np.float64)
            
            sbr_spike = False
            nan_inf = False
            nov = 1.0
            
            for c in range(5):
                psi += packet
                prev_phi = phi.copy()
                for t in range(TICKS_PER_CHUNK):
                    psi, phi, mu = evolve_v2_mu(psi, delta, phi, kappa, mu, e, r, MU_0)
                    
                    if np.isnan(np.sum(psi)) or np.isinf(np.sum(phi)):
                        nan_inf = True
                        break
                        
                    sbr = np.max(np.abs(psi)) / (np.mean(np.abs(psi)) + 1e-8)
                    if sbr > 1e5:
                        sbr_spike = True
                        
                if nan_inf: break
                nov = calc_novelty(phi, prev_phi)
                
            state = "STABLE"
            if nan_inf: state = "NAN_RUNAWAY"
            elif sbr_spike: state = "SBR_SPIKE"
            elif nov <= 0.0001: state = "FROZEN"
            elif nov > 0.05: state = "UNCONSOLIDATED"
            
            results.append({'eta': float(e), 'rho': float(r), 'state': state, 'final_novelty': float(nov)})
            
    print("\\nSweep complete.")
    return results

if __name__ == "__main__":
    out_dir = os.path.join(os.path.dirname(__file__), '..', 'output_audit_mu')
    os.makedirs(out_dir, exist_ok=True)
    
    # 1. Run Significance Audit
    stat_res = test_statistical_significance(N=30)
    
    # 2. Run Retention Audit
    ret_res = run_retention_test(seed=42)
    
    # 3. Run Param Sweep
    sweep_res = run_parameter_sweep()
    
    # Save output
    final_data = {
        'statistics': stat_res,
        'retention': ret_res,
        'param_sweep': sweep_res
    }
    
    with open(os.path.join(out_dir, 'canon_mu_validation.json'), 'w') as f:
        json.dump(final_data, f, indent=2)
        
    print(f"\\nAll Canon Audits saved to {out_dir}/canon_mu_validation.json")
