import numpy as np
import os
from scipy.ndimage import gaussian_filter

# --- Hardware Configuration ---
# Automatická detekce: Pokud je instalován PyTorch a má dostupnou grafickou kartu CUDA,
# automaticky se zrychlí na GPU. Jinak potichu zůstává na CPU/NumPy.
try:
    import torch
    USE_PYTORCH = torch.cuda.is_available() or os.environ.get("LINEUM_USE_PYTORCH", "0") == "1"
except ImportError:
    USE_PYTORCH = False

# --- Safety Caps ---
PSI_AMP_CAP = 1e6
GRAD_CAP = 1e6
PHI_CAP = 1e6

TEST_EXHALE_MODE = False
NOISE_STRENGTH = 0.005
PHI_INTERACTION_CAP = 10.0
DRIFT_STRENGTH = -0.004
DISSIPATION_RATE = 0.005
PSI_DIFFUSION = 0.05
REACTION_STRENGTH = 0.00070
PHI_DIFFUSION = 0.05

EXPERIMENTAL_TERM = 0 # Default OFF (0). Toggle to 1 to test fail-fast theoretical loops.


def sigmoid(x, k=5):
    return 1 / (1 + np.exp(-k * (x - 0.0)))

def diffuse_complex(field, kappa, rate=0.05):
    k_up = np.roll(kappa, 1, axis=0)
    k_dn = np.roll(kappa, -1, axis=0)
    k_lf = np.roll(kappa, 1, axis=1)
    k_rt = np.roll(kappa, -1, axis=1)
    
    sum_neighbors = (
        np.roll(field, 1, axis=0) * k_up +
        np.roll(field, -1, axis=0) * k_dn +
        np.roll(field, 1, axis=1) * k_lf +
        np.roll(field, -1, axis=1) * k_rt
    )
    active_neighbors = k_up + k_dn + k_lf + k_rt
    return rate * (sum_neighbors - active_neighbors * field)

def diffuse_real(field: np.ndarray, kappa: np.ndarray, rate=0.05) -> np.ndarray:
    return diffuse_complex(field, kappa, rate)

def _finite_clip(a, lo=None, hi=None, nan=0.0, posinf=None, neginf=None, dtype=None):
    x = np.asarray(a)
    if dtype is not None:
        x = x.astype(dtype, copy=False)
    if posinf is None:
        posinf = hi if hi is not None else 0.0
    if neginf is None:
        neginf = lo if lo is not None else 0.0
    x = np.nan_to_num(x, nan=nan, posinf=posinf, neginf=neginf)
    if lo is not None or hi is not None:
        x = np.clip(x, lo if lo is not None else -np.inf,
                    hi if hi is not None else np.inf)
    return x

def _cap_complex_magnitude(z: np.ndarray, cap: float) -> np.ndarray:
    z = np.asarray(z, dtype=np.complex128)
    mag = np.abs(z).astype(np.float64, copy=False)
    scale = np.ones_like(mag, dtype=np.float64)
    mask = mag > cap
    if np.any(mask):
        scale[mask] = cap / (mag[mask] + 1e-30)
        z = z * scale
    return z

def _finite_complex(z: np.ndarray, nan: float = 0.0) -> np.ndarray:
    z = np.asarray(z, dtype=np.complex128)
    re = np.nan_to_num(z.real, nan=nan, posinf=0.0, neginf=0.0)
    im = np.nan_to_num(z.imag, nan=nan, posinf=0.0, neginf=0.0)
    return re + 1j * im


# ======================================================================
# GPU PYTORCH IMPLEMENTATION (HARDWARE ACCELERATION)
# ======================================================================
def _diffuse_complex_torch(field, kappa, rate=0.05):
    import torch
    k_up = torch.roll(kappa, 1, dims=0)
    k_dn = torch.roll(kappa, -1, dims=0)
    k_lf = torch.roll(kappa, 1, dims=1)
    k_rt = torch.roll(kappa, -1, dims=1)
    
    sum_neighbors = (
        torch.roll(field, 1, dims=0) * k_up +
        torch.roll(field, -1, dims=0) * k_dn +
        torch.roll(field, 1, dims=1) * k_lf +
        torch.roll(field, -1, dims=1) * k_rt
    )
    active_neighbors = k_up + k_dn + k_lf + k_rt
    return rate * (sum_neighbors - active_neighbors * field)

def _evolve_pytorch(psi_np, delta_np, phi_np, kappa_np):
    """
    GPU-optimized step of Eq-4.
    Runs on CUDA if available. Transposes the results back to NumPy.
    """
    import torch
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    
    # Send variables to VRAM
    psi = torch.tensor(psi_np, dtype=torch.complex128, device=device)
    delta = torch.tensor(delta_np, dtype=torch.float64, device=device)
    phi = torch.tensor(phi_np, dtype=torch.float64, device=device)
    kappa = torch.tensor(kappa_np, dtype=torch.float64, device=device)

    size = psi.shape[0]

    amp = torch.abs(psi)
    amp = torch.clamp(amp, 0.0, PSI_AMP_CAP)

    grads = torch.gradient(amp + delta)
    grad_x = torch.clamp(grads[0], -GRAD_CAP, GRAD_CAP)
    grad_y = torch.clamp(grads[1], -GRAD_CAP, GRAD_CAP)
    
    grad_mag = torch.sqrt(torch.clamp(grad_x*grad_x + grad_y*grad_y, 0.0, 1e12))
    
    probability = torch.sigmoid(5.0 * (amp + grad_mag)) * kappa
    
    random_field = torch.rand(size, size, device=device, dtype=torch.float64)
    linons = (random_field < probability).to(torch.float64)
    
    linon_base = 0.01 if TEST_EXHALE_MODE else 0.03
    linon_scaling = 0.01 if TEST_EXHALE_MODE else 0.02
    linon_effect = (linon_base + linon_scaling * torch.clamp(amp, min=0.0)) * linons

    linon_complex = linon_effect * torch.exp(1j * torch.angle(psi))

    fluctuation = torch.normal(0.0, NOISE_STRENGTH, (size, size), device=device, dtype=torch.float64) * torch.exp(1j * torch.angle(psi))

    phi_int = torch.clamp(phi, 0.0, float(PHI_INTERACTION_CAP))
    interaction_term = 0.04 * phi_int * psi * kappa

    # --- EXPERIMENTAL NEW TERM FAIL-FAST HOOK ---
    if EXPERIMENTAL_TERM:
        experimental_factor = 0.0 * psi * kappa # Placeholder logic
        psi += experimental_factor

    grads_phi = torch.gradient(phi)
    
    phi_flow_term = DRIFT_STRENGTH * (grads_phi[0] + 1j * grads_phi[1]) * kappa
    psi += phi_flow_term

    psi += (linon_complex + fluctuation) * kappa + interaction_term

    psi -= DISSIPATION_RATE * psi
    psi += _diffuse_complex_torch(psi, kappa, rate=PSI_DIFFUSION) * kappa

    amp2 = torch.clamp(torch.abs(psi), 0.0, PSI_AMP_CAP)
    local_input = torch.clamp(amp2 * amp2, 0.0, 1e4)

    # Scale geometric absorption based on grid AREA (128x128 baseline)
    scale_ratio = (128.0 / size) ** 2
    dynamic_reaction = REACTION_STRENGTH * scale_ratio

    phi += kappa * dynamic_reaction * (local_input - phi)
    phi += kappa * PHI_DIFFUSION * _diffuse_complex_torch(phi, kappa, rate=0.05)

    phi = torch.clamp(phi, 0.0, PHI_CAP)
    
    # Cap magnitude
    mag = torch.abs(psi)
    scale = torch.ones_like(mag)
    mask = mag > PSI_AMP_CAP
    scale[mask] = PSI_AMP_CAP / (mag[mask] + 1e-30)
    psi = psi * scale

    # Download variables from VRAM back to numpy float
    return psi.cpu().numpy(), phi.cpu().numpy()


# ======================================================================
# CPU NUMPY IMPLEMENTATION (NATIVE CLOUD)
# ======================================================================
def _evolve_numpy(psi, delta, phi, kappa):
    size = psi.shape[0]

    psi = _finite_complex(psi, nan=0.0)
    phi = _finite_clip(phi, lo=0.0, hi=PHI_CAP, nan=0.0,
                       posinf=PHI_CAP, neginf=0.0, dtype=np.float64)

    amp = np.abs(psi).astype(np.float64, copy=False)
    amp = _finite_clip(amp, lo=0.0, hi=PSI_AMP_CAP, nan=0.0,
                       posinf=PSI_AMP_CAP, neginf=0.0)

    grad_x, grad_y = np.gradient((amp + delta).astype(np.float64, copy=False))
    grad_x = _finite_clip(grad_x, lo=-GRAD_CAP, hi=GRAD_CAP,
                          nan=0.0, posinf=GRAD_CAP, neginf=-GRAD_CAP)
    grad_y = _finite_clip(grad_y, lo=-GRAD_CAP, hi=GRAD_CAP,
                          nan=0.0, posinf=GRAD_CAP, neginf=-GRAD_CAP)
    grad_mag = np.sqrt(np.clip(grad_x*grad_x + grad_y*grad_y, 0.0, 1e12))
    
    probability = sigmoid(amp + grad_mag) * kappa
    
    random_field = np.random.rand(size, size)
    linons = (random_field < probability).astype(float)
    linon_base = 0.01 if TEST_EXHALE_MODE else 0.03
    linon_scaling = 0.01 if TEST_EXHALE_MODE else 0.02
    linon_effect = (linon_base + linon_scaling * amp.clip(min=0)) * linons

    linon_complex = linon_effect * np.exp(1j * np.angle(psi))

    fluctuation = np.random.normal(
        0.0, NOISE_STRENGTH, (size, size)) * np.exp(1j * np.angle(psi))

    phi_int = _finite_clip(phi, lo=0.0, hi=float(PHI_INTERACTION_CAP), nan=0.0,
                           posinf=float(PHI_INTERACTION_CAP), neginf=0.0, dtype=np.float64)
    
    interaction_term = 0.04 * phi_int * psi * kappa

    # --- EXPERIMENTAL NEW TERM FAIL-FAST HOOK ---
    if EXPERIMENTAL_TERM:
        experimental_factor = 0.0 * psi * kappa # Placeholder logic
        psi += experimental_factor
        
    grad_phi_x, grad_phi_y = np.gradient(phi)
    phi_flow_term = DRIFT_STRENGTH * (grad_phi_x + 1j * grad_phi_y) * kappa
    psi += phi_flow_term

    psi += (linon_complex + fluctuation) * kappa + interaction_term

    psi -= DISSIPATION_RATE * psi
    psi += diffuse_complex(psi, kappa, rate=PSI_DIFFUSION) * kappa

    amp2 = _finite_clip(np.abs(psi).astype(np.float64, copy=False),
                        lo=0.0, hi=PSI_AMP_CAP, nan=0.0, posinf=PSI_AMP_CAP, neginf=0.0)
    local_input = np.clip(amp2 * amp2, 0.0, 1e4)

    # Scale geometric absorption based on grid AREA (128x128 baseline)
    scale_ratio = (128.0 / size) ** 2
    dynamic_reaction = REACTION_STRENGTH * scale_ratio

    phi += kappa * dynamic_reaction * (local_input - phi)
    phi += kappa * PHI_DIFFUSION * diffuse_real(phi, kappa, rate=0.05)

    psi = _finite_complex(psi, nan=0.0)
    phi = _finite_clip(phi, lo=0.0, hi=PHI_CAP, nan=0.0,
                       posinf=PHI_CAP, neginf=0.0, dtype=np.float64)

    psi = _cap_complex_magnitude(psi, PSI_AMP_CAP)

    return psi, phi


def evolve(psi, delta, phi, kappa):
    """
    Krok rovnice Eq-4.
    Dynamicky zpracovává na GPU (PyTorch) nebo CPU (NumPy) na základě 
    továrního nastavení `USE_PYTORCH`.
    """
    if USE_PYTORCH:
        return _evolve_pytorch(psi, delta, phi, kappa)
            
    return _evolve_numpy(psi, delta, phi, kappa)
