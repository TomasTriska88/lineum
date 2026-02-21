import numpy as np
from scipy.ndimage import gaussian_filter

# --- Safety Caps ---
PSI_AMP_CAP = 1e6
GRAD_CAP = 1e6
PHI_CAP = 1e6

# --- Default Tunable Constants ---
# (Callers like lineum.py can override these at runtime before calling evolve)
TEST_EXHALE_MODE = False
NOISE_STRENGTH = 0.005
PHI_INTERACTION_CAP = 10.0
DRIFT_STRENGTH = -0.004
DISSIPATION_RATE = 0.005
PSI_DIFFUSION = 0.05
REACTION_STRENGTH = 0.00070
PHI_DIFFUSION = 0.05


def sigmoid(x, k=5):
    return 1 / (1 + np.exp(-k * (x - 0.0)))

def diffuse_complex(field, kappa, rate=0.05):
    # Neighbors can only contribute if they are permeable
    k_up = np.roll(kappa, 1, axis=0)
    k_dn = np.roll(kappa, -1, axis=0)
    k_lf = np.roll(kappa, 1, axis=1)
    k_rt = np.roll(kappa, -1, axis=1)
    
    # Weight neighbors by their permeability
    sum_neighbors = (
        np.roll(field, 1, axis=0) * k_up +
        np.roll(field, -1, axis=0) * k_dn +
        np.roll(field, 1, axis=1) * k_lf +
        np.roll(field, -1, axis=1) * k_rt
    )
    
    # Field only loses energy to neighbors that are permeable
    active_neighbors = k_up + k_dn + k_lf + k_rt
    
    return rate * (sum_neighbors - active_neighbors * field)

def diffuse_real(field: np.ndarray, kappa: np.ndarray, rate=0.05) -> np.ndarray:
    field = np.asarray(field, dtype=np.float64)
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

def evolve(psi, delta, phi, kappa):
    # Dynamic size based on input psi
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
    # CRITICAL: Linons cannot spontaneously generate inside physical walls 
    probability = sigmoid(amp + grad_mag) * kappa
    
    # RNG calls MUST happen exactly as before
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
    # Walls cannot exude interaction force
    interaction_term = 0.04 * phi_int * psi * kappa

    grad_phi_x, grad_phi_y = np.gradient(phi)
    # Drift cannot occur inside walls
    phi_flow_term = DRIFT_STRENGTH * (grad_phi_x + 1j * grad_phi_y) * kappa
    psi += phi_flow_term

    # Fluctuations and Linon creation only happen in open space
    psi += (linon_complex + fluctuation) * kappa + interaction_term

    psi -= DISSIPATION_RATE * psi
    # CRITICAL: The wave cannot diffuse into or out of walls.
    psi += diffuse_complex(psi, kappa, rate=PSI_DIFFUSION) * kappa

    amp2 = _finite_clip(np.abs(psi).astype(np.float64, copy=False),
                        lo=0.0, hi=PSI_AMP_CAP, nan=0.0, posinf=PSI_AMP_CAP, neginf=0.0)
    local_input = np.clip(amp2 * amp2, 0.0, 1e4)

    phi += kappa * REACTION_STRENGTH * (local_input - phi)
    phi += kappa * PHI_DIFFUSION * diffuse_real(phi, kappa, rate=0.05)

    psi = _finite_complex(psi, nan=0.0)
    phi = _finite_clip(phi, lo=0.0, hi=PHI_CAP, nan=0.0,
                       posinf=PHI_CAP, neginf=0.0, dtype=np.float64)

    psi = _cap_complex_magnitude(psi, PSI_AMP_CAP)

    return psi, phi
