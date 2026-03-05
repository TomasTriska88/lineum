import numpy as np
import os
from dataclasses import dataclass
from typing import Dict, Any

try:
    import torch
    USE_PYTORCH = torch.cuda.is_available() or os.environ.get("LINEUM_USE_PYTORCH", "0") == "1"
except ImportError:
    USE_PYTORCH = False

@dataclass(frozen=True)
class Eq4Config:
    # --- Physic Constants ---
    dt: float = 1.0
    psi_diffusion: float = 0.05
    phi_diffusion: float = 0.05
    dissipation_rate: float = 0.005
    reaction_strength: float = 0.0007
    noise_strength: float = 0.005
    drift_strength: float = -0.004
    
    # --- Integration Specifics ---
    stencil_type: str = "LAP4"  # "LAP4" or "LAP8"
    physics_mode_psi: str = "diffusion"  # "diffusion" | "wave_baseline" | "wave_projected" | "wave_projected_soft"
    wave_damping_edge: float = 0.05
    wave_lpf_enabled: bool = False
    wave_lpf_cutoff: float = 0.35
    kappa_soft_blur_iters: int = 2
    
    # --- Mode Coupling (Energy Transfer) ---
    use_mode_coupling: bool = True
    mode_coupling_strength: float = 0.001
    
    # --- HDD Track (Mu) ---
    use_mu: bool = False
    mu_eta: float = 0.005
    mu_rho: float = 0.0001
    mu_cap: float = 10.0
    mu_peak_cutoff_ratio: float = 0.1
    
    # --- Safe Numerical CFL Guards (NOT Physics) ---
    psi_amp_cap: float = 1e6
    grad_cap: float = 1e6
    phi_cap: float = 1e6

def _diffuse_complex_numpy(field, kappa, rate, stencil_type):
    k_up = np.roll(kappa, 1, axis=0)
    k_dn = np.roll(kappa, -1, axis=0)
    k_lf = np.roll(kappa, 1, axis=1)
    k_rt = np.roll(kappa, -1, axis=1)
    
    f_up = np.roll(field, 1, axis=0)
    f_dn = np.roll(field, -1, axis=0)
    f_lf = np.roll(field, 1, axis=1)
    f_rt = np.roll(field, -1, axis=1)
    
    if stencil_type == "LAP8":
        w_ortho = 1.0
        w_diag = 0.25
        k_ul = np.roll(k_up, 1, axis=1)
        k_ur = np.roll(k_up, -1, axis=1)
        k_dl = np.roll(k_dn, 1, axis=1)
        k_dr = np.roll(k_dn, -1, axis=1)
        
        f_ul = np.roll(f_up, 1, axis=1)
        f_ur = np.roll(f_up, -1, axis=1)
        f_dl = np.roll(f_dn, 1, axis=1)
        f_dr = np.roll(f_dn, -1, axis=1)
        
        sum_neighbors = (w_ortho * (f_up*k_up + f_dn*k_dn + f_lf*k_lf + f_rt*k_rt) + 
                        w_diag * (f_ul*k_ul + f_ur*k_ur + f_dl*k_dl + f_dr*k_dr))
        active_neighbors = (w_ortho * (k_up + k_dn + k_lf + k_rt) + 
                           w_diag * (k_ul + k_ur + k_dl + k_dr))
    else:
        # Default LAP4
        sum_neighbors = f_up*k_up + f_dn*k_dn + f_lf*k_lf + f_rt*k_rt
        active_neighbors = k_up + k_dn + k_lf + k_rt

    return rate * (sum_neighbors - active_neighbors * field)

def _diffuse_complex_torch(field, kappa, rate, stencil_type):
    import torch
    k_up = torch.roll(kappa, 1, dims=0)
    k_dn = torch.roll(kappa, -1, dims=0)
    k_lf = torch.roll(kappa, 1, dims=1)
    k_rt = torch.roll(kappa, -1, dims=1)
    
    f_up = torch.roll(field, 1, dims=0)
    f_dn = torch.roll(field, -1, dims=0)
    f_lf = torch.roll(field, 1, dims=1)
    f_rt = torch.roll(field, -1, dims=1)
    
    if stencil_type == "LAP8":
        w_ortho = 1.0
        w_diag = 0.25
        k_ul = torch.roll(k_up, 1, dims=1)
        k_ur = torch.roll(k_up, -1, dims=1)
        k_dl = torch.roll(k_dn, 1, dims=1)
        k_dr = torch.roll(k_dn, -1, dims=1)
        
        f_ul = torch.roll(f_up, 1, dims=1)
        f_ur = torch.roll(f_up, -1, dims=1)
        f_dl = torch.roll(f_dn, 1, dims=1)
        f_dr = torch.roll(f_dn, -1, dims=1)
        
        sum_neighbors = (w_ortho * (f_up*k_up + f_dn*k_dn + f_lf*k_lf + f_rt*k_rt) + 
                        w_diag * (f_ul*k_ul + f_ur*k_ur + f_dl*k_dl + f_dr*k_dr))
        active_neighbors = (w_ortho * (k_up + k_dn + k_lf + k_rt) + 
                           w_diag * (k_ul + k_ur + k_dl + k_dr))
    else:
        # Default LAP4
        sum_neighbors = f_up*k_up + f_dn*k_dn + f_lf*k_lf + f_rt*k_rt
        active_neighbors = k_up + k_dn + k_lf + k_rt

    return rate * (sum_neighbors - active_neighbors * field)


def _cap_complex_magnitude_numpy(z, cap):
    z = np.asarray(z, dtype=np.complex128)
    mag = np.abs(z)
    mask = mag > cap
    if np.any(mask):
        z[mask] = z[mask] * (cap / (mag[mask] + 1e-30))
    return z

def _cap_complex_magnitude_torch(z, cap):
    import torch
    mag = torch.abs(z)
    mask = mag > cap
    if torch.any(mask):
        scale = torch.ones_like(mag)
        scale[mask] = cap / (mag[mask] + 1e-8)
        z = z * scale
    return z


def _step_numpy(state: Dict[str, Any], cfg: Eq4Config) -> Dict[str, Any]:
    psi = np.asarray(state.get("psi"), dtype=np.complex128)
    phi = np.asarray(state.get("phi"), dtype=np.float64)
    kappa = np.asarray(state.get("kappa"), dtype=np.float64)
    mu = np.asarray(state.get("mu", np.zeros_like(phi)), dtype=np.float64)
    # The external semantic delta if supplied
    delta = np.asarray(state.get("delta", np.zeros_like(phi)), dtype=np.float64) 
    
    size = psi.shape[0]

    amp = np.abs(psi)
    amp = np.clip(amp, 0.0, cfg.psi_amp_cap)

    grad_x, grad_y = np.gradient(amp + delta)
    grad_x = np.clip(grad_x, -cfg.grad_cap, cfg.grad_cap)
    grad_y = np.clip(grad_y, -cfg.grad_cap, cfg.grad_cap)
    grad_mag = np.sqrt(np.clip(grad_x**2 + grad_y**2, 0.0, 1e12))
    
    # Probabilistic Linon Generation
    probability = (1.0 / (1.0 + np.exp(-5.0 * (amp + grad_mag)))) * kappa
    linons = (np.random.rand(size, size) < probability).astype(np.float64)
    linon_effect = np.clip((0.03 + 0.02 * np.clip(amp, a_min=0, a_max=None)) * linons, 0.0, 10.0)
    linon_complex = linon_effect * np.exp(1j * np.angle(psi))

    fluctuation = np.clip(np.random.normal(0.0, cfg.noise_strength, (size, size)), -1.0, 1.0) * np.exp(1j * np.angle(psi))

    # Calculate mu-modulated drift multiplier (ALWAYS READ)
    drift_multiplier = 1.0 + mu

    phi_int = np.clip(phi, 0.0, 10.0)
    interaction_factor = 0.1 * np.tanh((0.04 * phi_int * kappa * drift_multiplier) / 0.1)
    interaction_term = interaction_factor * psi
    int_mag = np.abs(interaction_term)
    interaction_term = interaction_term / (1.0 + int_mag / 10.0)
        
    grad_phi_x, grad_phi_y = np.gradient(phi)
    phi_flow_term = cfg.drift_strength * (grad_phi_x + 1j * grad_phi_y) * kappa * drift_multiplier
    flow_mag = np.abs(phi_flow_term)
    phi_flow_term = phi_flow_term / (1.0 + flow_mag / 10.0)
    
    # 1. Kinematic update
    psi += phi_flow_term * cfg.dt
    psi = _cap_complex_magnitude_numpy(psi, cfg.psi_amp_cap)

    psi += ((linon_complex + fluctuation) * kappa + interaction_term) * cfg.dt

    psi -= 0.005 * psi * cfg.dt # dissipation
    psi += _diffuse_complex_numpy(psi, kappa, rate=cfg.psi_diffusion, stencil_type=cfg.stencil_type) * kappa * cfg.dt

    e_psi = np.abs(psi)**2

    # 2. Mode-Coupling or Baseline Reaction
    if cfg.use_mode_coupling:
        delta_e = cfg.mode_coupling_strength * e_psi * kappa * cfg.dt
        phi += delta_e
        
        # Energy conservation
        psi_mag_new = np.sqrt(np.maximum(e_psi - delta_e, 0.0))
        psi = (psi / (np.sqrt(e_psi) + 1e-12)) * psi_mag_new
    else:
        scale_ratio = (128.0 / size) ** 2
        dynamic_reaction = cfg.reaction_strength * scale_ratio
        # This is strictly a fallback mapping, avoiding amp^2 clipping logic (now driven purely by generic absorption)
        phi += kappa * dynamic_reaction * (e_psi - phi) * cfg.dt

    phi += kappa * cfg.phi_diffusion * _diffuse_complex_numpy(phi, kappa, rate=0.05, stencil_type=cfg.stencil_type)
    phi = np.clip(phi, 0.0, cfg.phi_cap)

    # 3. Mu update (The HDD track)
    if cfg.use_mu:
        # Dynamic relative sparsity: Isolate absolute structural peaks
        dynamic_floor = cfg.mu_peak_cutoff_ratio
        if dynamic_floor > 0 and dynamic_floor < 1.0:
            dynamic_floor = dynamic_floor * np.max(e_psi)
            
        active_e_psi = np.maximum(e_psi - dynamic_floor, 0.0)
        mu += cfg.mu_eta * active_e_psi * kappa * drift_multiplier * cfg.dt
        mu -= cfg.mu_rho * mu * cfg.dt
        mu = np.clip(mu, 0.0, cfg.mu_cap)

    # Numeric Fail-Safe
    if np.isnan(np.sum(psi)) or np.max(np.abs(psi)) >= cfg.psi_amp_cap * 0.99:
        print("!!! LINEUM FAIL-SAFE (CPU): Numeric divergence detected. Resetting Psi. !!!")
        psi = np.zeros_like(psi)

    out_state = {"psi": psi, "phi": phi, "kappa": kappa, "mu": mu}
    return out_state


_fft_symbol_cache = {}

def _get_fft_symbol(size: int, stencil_type: str, device, dtype):
    import torch
    key = (size, stencil_type, device, dtype)
    if key in _fft_symbol_cache:
        return _fft_symbol_cache[key]
    
    kernel = torch.zeros((size, size), device=device, dtype=dtype)
    if stencil_type == "LAP8":
        kernel[0, 0] = -5.0
        kernel[1, 0] = 1.0; kernel[-1, 0] = 1.0
        kernel[0, 1] = 1.0; kernel[0, -1] = 1.0
        kernel[1, 1] = 0.25; kernel[-1, 1] = 0.25
        kernel[1, -1] = 0.25; kernel[-1, -1] = 0.25
    else:
        kernel[0, 0] = -4.0
        kernel[1, 0] = 1.0; kernel[-1, 0] = 1.0
        kernel[0, 1] = 1.0; kernel[0, -1] = 1.0
        
    symbol = torch.fft.fft2(kernel).real
    _fft_symbol_cache[key] = symbol
    return symbol

def _step_pytorch(state: Dict[str, Any], cfg: Eq4Config) -> Dict[str, Any]:
    import torch
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    
    psi = torch.tensor(state.get("psi"), dtype=torch.complex128, device=device)
    phi = torch.tensor(state.get("phi"), dtype=torch.float64, device=device)
    kappa = torch.tensor(state.get("kappa"), dtype=torch.float64, device=device)
    mu = torch.tensor(state.get("mu", np.zeros_like(state.get("phi"))), dtype=torch.float64, device=device)
    delta = torch.tensor(state.get("delta", np.zeros_like(state.get("phi"))), dtype=torch.float64, device=device)

    size = psi.shape[0]

    amp = torch.abs(psi)
    amp = torch.clamp(amp, 0.0, cfg.psi_amp_cap)

    grads = torch.gradient(amp + delta)
    grad_x = torch.clamp(grads[0], -cfg.grad_cap, cfg.grad_cap)
    grad_y = torch.clamp(grads[1], -cfg.grad_cap, cfg.grad_cap)
    grad_mag = torch.sqrt(torch.clamp(grad_x**2 + grad_y**2, 0.0, 1e12))
    
    probability = torch.sigmoid(5.0 * (amp + grad_mag)) * kappa
    linons = (torch.rand(size, size, device=device, dtype=torch.float64) < probability).to(torch.float64)

    fluct_base = torch.clamp(torch.normal(0.0, cfg.noise_strength, (size, size), device=device, dtype=torch.float64), min=-1.0, max=1.0)

    # Calculate mu-modulated drift multiplier (ALWAYS READ)
    drift_multiplier = 1.0 + mu

    phi_int = torch.clamp(phi, 0.0, 10.0)
    interaction_factor = 0.1 * torch.tanh((0.04 * phi_int * kappa * drift_multiplier) / 0.1)

    grads_phi = torch.gradient(phi)
    phi_flow_term = cfg.drift_strength * (grads_phi[0] + 1j * grads_phi[1]) * kappa * drift_multiplier
    flow_mag = torch.abs(phi_flow_term)
    phi_flow_term = phi_flow_term / (1.0 + flow_mag / 10.0)
    
    def compute_N(curr_psi):
        amp_c = torch.clamp(torch.abs(curr_psi), 0.0, cfg.psi_amp_cap)
        linon_eff = torch.clamp((0.03 + 0.02 * amp_c) * linons, max=10.0)
        linon_comp = linon_eff * torch.exp(1j * torch.angle(curr_psi))
        fluct_comp = fluct_base * torch.exp(1j * torch.angle(curr_psi))
        
        int_term = interaction_factor * curr_psi
        int_mag_c = torch.abs(int_term)
        int_term = int_term / (1.0 + int_mag_c / 10.0)
        
        return phi_flow_term + (linon_comp + fluct_comp) * kappa + int_term

    cap_trigger_count = 0
    physics_mode = getattr(cfg, "physics_mode_psi", "diffusion")
    
    n_step_1_delta = 0.0
    n_step_2_delta = 0.0

    if "wave" in physics_mode:
        if cfg.dt != 0:
            e_before = torch.mean(torch.abs(psi)**2).item()
            psi = psi + compute_N(psi) * (cfg.dt / 2.0)
            n_step_1_delta = torch.mean(torch.abs(psi)**2).item() - e_before
        
        if cfg.dt != 0:
            symbol = _get_fft_symbol(size, cfg.stencil_type, device, torch.float64)
            psi_hat = torch.fft.fft2(psi)
            psi_hat = psi_hat * torch.exp(1j * cfg.psi_diffusion * symbol * cfg.dt)
            
            if getattr(cfg, "wave_lpf_enabled", False):
                # Spectral filter (low pass) to prevent aliasing speckles
                freqs = torch.fft.fftfreq(size, device=device)
                fx, fy = torch.meshgrid(freqs, freqs, indexing='ij')
                fr = torch.sqrt(fx**2 + fy**2)
                # Cutoff high frequencies (Nyquist is 0.5)
                lpf = torch.exp(-(fr / getattr(cfg, "wave_lpf_cutoff", 0.35))**8)  # Super-Gaussian smooth rolloff
                psi_hat = psi_hat * lpf
                
            psi = torch.fft.ifft2(psi_hat)
            
        if cfg.dt != 0:
            e_before = torch.mean(torch.abs(psi)**2).item()
            psi = psi + compute_N(psi) * (cfg.dt / 2.0)
            n_step_2_delta = torch.mean(torch.abs(psi)**2).item() - e_before
            
        if "projected" in physics_mode:
            if "soft" in physics_mode:
                # Smooth the kappa obstacle boundary to avoid hard high-frequency edges
                k_sm = kappa
                for _ in range(getattr(cfg, "kappa_soft_blur_iters", 2)):
                    k_up = torch.roll(k_sm, 1, dims=0)
                    k_dn = torch.roll(k_sm, -1, dims=0)
                    k_lf = torch.roll(k_sm, 1, dims=1)
                    k_rt = torch.roll(k_sm, -1, dims=1)
                    k_sm = (k_sm + 0.25 * (k_up + k_dn + k_lf + k_rt)) / 2.0
                psi = psi * k_sm
            else:
                psi = psi * kappa
            
            gamma_obs = getattr(cfg, "wave_damping_edge", 0.0)
            if gamma_obs > 0.0:
                not_kappa = 1.0 - kappa
                k_up = torch.roll(not_kappa, 1, dims=0)
                k_dn = torch.roll(not_kappa, -1, dims=0)
                k_lf = torch.roll(not_kappa, 1, dims=1)
                k_rt = torch.roll(not_kappa, -1, dims=1)
                dilated = torch.clamp(not_kappa + k_up + k_dn + k_lf + k_rt, 0.0, 1.0)
                ring = torch.clamp(dilated - not_kappa, 0.0, 1.0)
                psi = psi * torch.exp(-gamma_obs * ring * cfg.dt)
                
        amp_post = torch.abs(psi)
        cap_mask = amp_post > cfg.psi_amp_cap
        cap_trigger_count = int(cap_mask.sum().item())
        if cap_trigger_count > 0:
            psi = _cap_complex_magnitude_torch(psi, cfg.psi_amp_cap)
    else:
        # Standard diffusion mode
        linon_effect = torch.clamp((0.03 + 0.02 * torch.clamp(amp, min=0.0)) * linons, max=10.0)
        linon_complex = linon_effect * torch.exp(1j * torch.angle(psi))
        fluctuation = fluct_base * torch.exp(1j * torch.angle(psi))
        
        interaction_term = interaction_factor * psi
        int_mag = torch.abs(interaction_term)
        interaction_term = interaction_term / (1.0 + int_mag / 10.0)

        psi += phi_flow_term * cfg.dt
        psi = _cap_complex_magnitude_torch(psi, cfg.psi_amp_cap)

        psi += ((linon_complex + fluctuation) * kappa + interaction_term) * cfg.dt

        psi -= 0.005 * psi * cfg.dt
        psi += _diffuse_complex_torch(psi, kappa, rate=cfg.psi_diffusion, stencil_type=cfg.stencil_type) * kappa * cfg.dt
        
        amp_post = torch.abs(psi)
        cap_mask = amp_post > cfg.psi_amp_cap
        cap_trigger_count = int(cap_mask.sum().item())

    e_psi = torch.abs(psi)**2

    # 2. Mode-Coupling or Baseline Reaction
    if cfg.use_mode_coupling:
        delta_e = cfg.mode_coupling_strength * e_psi * kappa * cfg.dt
        phi += delta_e
        
        psi_mag_new = torch.sqrt(torch.clamp(e_psi - delta_e, min=0.0))
        psi = (psi / (torch.sqrt(e_psi) + 1e-12)) * psi_mag_new
    else:
        scale_ratio = (128.0 / size) ** 2
        dynamic_reaction = cfg.reaction_strength * scale_ratio
        phi += kappa * dynamic_reaction * (e_psi - phi) * cfg.dt

    phi += kappa * cfg.phi_diffusion * _diffuse_complex_torch(phi, kappa, rate=0.05, stencil_type=cfg.stencil_type)
    phi = torch.clamp(phi, 0.0, cfg.phi_cap)

    # 3. Mu update (The HDD track)
    if cfg.use_mu:
        # Dynamic relative sparsity: Isolate absolute structural peaks
        dynamic_floor = cfg.mu_peak_cutoff_ratio
        if dynamic_floor > 0 and dynamic_floor < 1.0:
            dynamic_floor = dynamic_floor * torch.max(e_psi)
            
        active_e_psi = torch.clamp(e_psi - dynamic_floor, min=0.0)
        mu += cfg.mu_eta * active_e_psi * kappa * drift_multiplier * cfg.dt
        mu -= cfg.mu_rho * mu * cfg.dt
        mu = torch.clamp(mu, 0.0, cfg.mu_cap)

    is_nan = torch.isnan(torch.sum(psi))
    max_abs_psi = torch.max(torch.abs(psi))

    if is_nan or max_abs_psi >= cfg.psi_amp_cap * 0.99:
        print("!!! LINEUM FAIL-SAFE (GPU): Numeric divergence detected. Resetting Psi. !!!")
        psi = torch.zeros_like(psi)

    e_psi_mean = torch.mean(torch.abs(psi)**2).item()
    
    out_state = {
        "psi": psi.cpu().numpy(),
        "phi": phi.cpu().numpy(),
        "kappa": kappa.cpu().numpy(),
        "mu": mu.cpu().numpy(),
        "telemetry": {
            "N_t": e_psi_mean,
            "max_abs_psi": max_abs_psi.item(),
            "cap_triggers": cap_trigger_count,
            "cap_trigger_pct": (cap_trigger_count / (size*size)) * 100.0,
            "is_nan": bool(is_nan.item()),
            "n_step_1_delta": n_step_1_delta,
            "n_step_2_delta": n_step_2_delta
        }
    }
    return out_state


def step_eq4(state: Dict[str, Any], cfg: Eq4Config = Eq4Config()) -> Dict[str, Any]:
    """
    The Single Source of Truth for Lineum Canonical Eq-4' Physics.
    Evaluates the continuous topological math across the discretized ROM (\kappa) and RAM (\phi).
    Uses GPU acceleration if available.
    """
    assert "psi" in state and "phi" in state and "kappa" in state, "State must contain psi, phi, and kappa."
    
    if USE_PYTORCH:
        return _step_pytorch(state, cfg)
            
    return _step_numpy(state, cfg)
