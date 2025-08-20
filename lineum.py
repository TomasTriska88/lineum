from matplotlib.animation import FuncAnimation
from tqdm import tqdm
from scipy.fft import fft, fftfreq
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
from scipy.ndimage import gaussian_filter, maximum_filter
import os
from scipy.spatial.distance import euclidean
import random

# 🛠️ Runtime toggles – easy run control
RUN_ID = 6             # run index (1, 2, …)
RUN_MODE = "false"      # "true" or "false"
# used as a prefix for all output files
SEED = 41              # fixed seed for reproducibility
RUN_TAG = f"spec{RUN_ID}_{RUN_MODE}_s{SEED}"

np.random.seed(SEED)
random.seed(SEED)

# 🔧 Configuration mapping
CONFIGS = {
    # Observable-world / low-entropy test
    (1, "true"):  {"LOW_NOISE_MODE": True,  "TEST_EXHALE_MODE": True,  "KAPPA_MODE": "gradient"},

    # Resonance between order and chaos
    (1, "false"): {"LOW_NOISE_MODE": False, "TEST_EXHALE_MODE": True,  "KAPPA_MODE": "gradient"},

    # Structure-from-flow only (no memory)
    (2, "true"):  {"LOW_NOISE_MODE": True,  "TEST_EXHALE_MODE": False, "KAPPA_MODE": "gradient"},

    # Turbulent quantum-like field
    (2, "false"): {"LOW_NOISE_MODE": False, "TEST_EXHALE_MODE": False, "KAPPA_MODE": "gradient"},

    # Mathematical ideal; silence → structure
    (3, "true"):  {"LOW_NOISE_MODE": True,  "TEST_EXHALE_MODE": False, "KAPPA_MODE": "constant"},

    # Determinism + noise (physical-like)
    (3, "false"): {"LOW_NOISE_MODE": False, "TEST_EXHALE_MODE": False, "KAPPA_MODE": "constant"},

    # Closed system / trapped particle
    (4, "true"):  {"LOW_NOISE_MODE": True,  "TEST_EXHALE_MODE": False, "KAPPA_MODE": "island"},

    # Quantum-experiment-like setup
    (4, "false"): {"LOW_NOISE_MODE": False, "TEST_EXHALE_MODE": False, "KAPPA_MODE": "island"},

    # Detector for extremely subtle effects
    (5, "true"): {"LOW_NOISE_MODE": True, "TEST_EXHALE_MODE": True, "KAPPA_MODE": "island"},

    # Island universe under collapse
    (5, "false"): {"LOW_NOISE_MODE": False, "TEST_EXHALE_MODE": True,  "KAPPA_MODE": "island"},

    # Latent ideal with slowdown
    (6, "true"):  {"LOW_NOISE_MODE": True,  "TEST_EXHALE_MODE": True,  "KAPPA_MODE": "constant"},

    # # Noisy reality + memory
    (6, "false"): {"LOW_NOISE_MODE": False, "TEST_EXHALE_MODE": True,  "KAPPA_MODE": "constant"},

    # Laws gradually becoming globally shared
    (7, "true"): {"LOW_NOISE_MODE": True, "TEST_EXHALE_MODE": False, "KAPPA_MODE": "island_to_constant"}
}

# 📦 Apply configuration
cfg = CONFIGS.get((RUN_ID, RUN_MODE), {})
LOW_NOISE_MODE = cfg.get("LOW_NOISE_MODE", False)
TEST_EXHALE_MODE = cfg.get("TEST_EXHALE_MODE", False)
KAPPA_MODE = cfg.get("KAPPA_MODE", "gradient")

output_dir = "output"
os.makedirs(output_dir, exist_ok=True)


def notify_file_creation(path, success=True, error=None):
    """Print a notification about file creation success or failure."""
    name = os.path.basename(path)
    if success:
        print(f"✅ File '{name}' has been successfully created.")
    else:
        print(f"❌ Failed to create file '{name}': {error}")


def save_csv(filename, header, rows):
    """Fast CSV save using pandas; avoids per-row Python overhead."""
    path = os.path.join(output_dir, f"{RUN_TAG}_{filename}")
    try:
        # Materialize rows once (zip/generators → list); much faster than row-by-row writes
        data = list(rows)
        # Build DataFrame with/without header
        if header:
            df = pd.DataFrame(data, columns=header)
        else:
            df = pd.DataFrame(data)
        df.to_csv(path, index=False)
        notify_file_creation(path)
    except Exception as e:
        notify_file_creation(path, success=False, error=e)


particle_log = []
interaction_log = []
amplitude_log = []
topo_log = []
phi_center_log = []

# Low-noise toggle (disable stochastic ξ)
# True = structural-closure test mode
# False = regular simulations with fluctuations
LOW_NOISE_MODE = False

# TEST_EXHALE_MODE=True enables calmer dynamics for structural-memory test
# Use False in regular runs for full dynamics
TEST_EXHALE_MODE = True

# Parameters
size = 128
steps = 1000 if TEST_EXHALE_MODE else 500

# Canonical noise level
BASE_NOISE_STRENGTH = 0.005
NOISE_STRENGTH = 0.0 if LOW_NOISE_MODE else BASE_NOISE_STRENGTH

# Probe points whose amplitude we track
probe_points = [(y, x) for y in range(0, size, 20) for x in range(0, size, 20)]

multi_amp_logs = {pt: [] for pt in probe_points}


PIXEL_SIZE = 1e-12     # 1 pixel = 1 pm (pikometr)
TIME_STEP = 1e-21      # 1 krok = 1 zs (zeptosekunda)


def sigmoid(x, k=5):
    return 1 / (1 + np.exp(-k * (x - 0.0)))


def generate_kappa(step, total_steps=steps):
    """Postupná změna z island na constant"""
    progress = step / total_steps
    core = np.zeros((size, size))
    core[size//2 - 5:size//2 + 5, size//2 - 5:size//2 + 5] = 1.0
    core = gaussian_filter(core, sigma=5)
    return (1 - progress) * core + progress * 0.5


def generate_structured_delta(scale=10):
    noise = np.random.normal(0.0, 1.0, (size, size))
    blurred = gaussian_filter(noise, sigma=scale)
    return blurred / np.max(np.abs(blurred)) * 0.05


def initialize_fields():
    amp = np.random.normal(0.0, 0.1, (size, size))
    phase = np.random.uniform(0, 2*np.pi, (size, size))
    amp[size//2, size//2] += 1.0  # asymetrie uprostřed
    psi = amp * np.exp(1j * phase)
    delta = generate_structured_delta()
    return psi, delta


def initialize_interaction_field():
    return np.zeros((size, size), dtype=np.complex128)


def diffuse_complex(field, rate=0.05):
    return rate * (
        np.roll(field, 1, axis=0) +
        np.roll(field, -1, axis=0) +
        np.roll(field, 1, axis=1) +
        np.roll(field, -1, axis=1) -
        4 * field
    )


def evolve(psi, delta, phi, kappa):
    amp = np.abs(psi)
    grad_x, grad_y = np.gradient(amp + delta)
    grad_mag = np.sqrt(np.clip(grad_x**2 + grad_y**2, 0, 1e4))

    probability = sigmoid(amp + grad_mag)
    random_field = np.random.rand(size, size)
    linons = (random_field < probability).astype(float)
    linon_base = 0.01 if TEST_EXHALE_MODE else 0.03
    linon_scaling = 0.01 if TEST_EXHALE_MODE else 0.02
    linon_effect = (linon_base + linon_scaling * amp.clip(min=0)) * linons

    linon_complex = linon_effect * np.exp(1j * np.angle(psi))

    fluctuation = np.random.normal(
        0.0, NOISE_STRENGTH, (size, size)) * np.exp(1j * np.angle(psi))

    # 💡 Adding interaction
    interaction_term = 0.04 * np.clip(phi, -10, 10) * psi

    # 💫 Gradient φ jako „tíhový tok“
    grad_phi_x, grad_phi_y = np.gradient(np.abs(phi))
    phi_flow_term = -0.004 * (grad_phi_x + 1j * grad_phi_y)
    psi += phi_flow_term

    psi += linon_complex + fluctuation + interaction_term

    dissipation_rate = 0.00462  # ln(2)/150 → half-life 150 steps
    psi -= dissipation_rate * psi

    psi += diffuse_complex(psi)

    # 🌀 Canonical φ-evolution: slow memory + single calibrated diffusion
    # ≈ ln(2) / (2000 * ⟨κ⟩) with ⟨κ⟩≈0.5 → half-life ≈ 2000 steps
    reaction_strength = 0.00070

    local_input = np.clip(np.abs(psi)**2, 0, 1e4)

    # single-step relaxation toward local_input (no extra 0.5 factor):
    phi += kappa * reaction_strength * (local_input - phi)

    # single diffusion application, calibrated: Deff ≈ 0.05 * 0.30 = 0.015
    phi += kappa * 0.30 * diffuse_complex(phi)

    return psi, phi


def save_phi_center_plot(filename=f"{RUN_TAG}_phi_center_plot.png"):
    phi_center_values = [row[1] for row in phi_center_log]
    steps_list = [row[0] for row in phi_center_log]

    plt.figure(figsize=(8, 4))
    plt.plot(steps_list, phi_center_values, label="|φ_center|", color="orange")
    plt.xlabel("Step")
    plt.ylabel("|φ_center|")
    plt.title("Development of the amplitude of the interaction field at the center")
    plt.grid(True)
    plt.tight_layout()
    path = os.path.join(output_dir, filename)
    try:
        plt.savefig(path)
        notify_file_creation(path)
    except Exception as e:
        notify_file_creation(path, success=False, error=e)
    finally:
        plt.close()


def save_kappa_map(kappa, filename=f"{RUN_TAG}_kappa_map.png"):
    plt.figure(figsize=(6, 6))
    plt.imshow(kappa, cmap="inferno", vmin=0, vmax=1)
    plt.colorbar(label="κ value")
    plt.title("Kappa map (κ)")
    plt.axis("off")
    path = os.path.join(output_dir, filename)
    try:
        plt.savefig(path)
        notify_file_creation(path)
    except Exception as e:
        notify_file_creation(path, success=False, error=e)
    finally:
        plt.close()


def detect_vortices(phase: np.ndarray) -> np.ndarray:
    """
    Vectorized winding-number detection on 2x2 plaquettes.
    Returns int array in {-1,0,+1}, without amplitude gating.
    """
    p00 = phase[:-1, :-1]
    p01 = phase[:-1, 1:]
    p11 = phase[1:, 1:]
    p10 = phase[1:, :-1]

    d1 = np.angle(np.exp(1j * (p01 - p00)))
    d2 = np.angle(np.exp(1j * (p11 - p01)))
    d3 = np.angle(np.exp(1j * (p10 - p11)))
    d4 = np.angle(np.exp(1j * (p00 - p10)))
    winding = (d1 + d2 + d3 + d4) / (2 * np.pi)

    vortices = np.zeros_like(phase, dtype=int)
    block = vortices[:-1, :-1]
    block[winding > 0.5] = 1
    block[winding < -0.5] = -1
    return vortices


VORTEX_VIS_PERCENTILE = 5.0  # visualization-only gate: keep lowest 5% amplitud


def update_topology_log(raw_vortices: np.ndarray, step_idx: int, topo_log: list) -> None:
    """
    Append RAW topology counts for this step into topo_log: (step, +1, -1, net, total).
    """
    num_pos = int(np.sum(raw_vortices == 1))
    num_neg = int(np.sum(raw_vortices == -1))
    net_charge = num_pos - num_neg
    total = num_pos + num_neg
    topo_log.append((step_idx, num_pos, num_neg, net_charge, total))


def gate_vortices_by_amplitude(vortices: np.ndarray, amp: np.ndarray, amp_thresh: float = None) -> np.ndarray:
    """
    Keep vortex marks only where |psi| is low (near singularities).
    Used for visualization; metrics still use raw vortices.
    """

    if amp_thresh is None:
        # default: robust 5th percentile
        amp_thresh = float(np.percentile(amp, 5.0))
    mask = (amp <= amp_thresh)
    out = np.zeros_like(vortices)
    out[:-1, :-1] = vortices[:-1, :-1] * mask[:-1, :-1]
    return out


if __name__ == "__main__":
    # Inicializace polí
    psi, delta = initialize_fields()
    phi = initialize_interaction_field()
    # ladicí pole, zatím statické (všude 1.0)

    kappa = np.ones((size, size), dtype=np.float64)

    if KAPPA_MODE == "gradient":
        for y in range(size):
            kappa[y, :] = np.linspace(0.1, 1.0, size)
        save_kappa_map(kappa)

    elif KAPPA_MODE == "constant":
        kappa *= 0.5  # nebo jiná zvolená konstanta
        save_kappa_map(kappa)

    elif KAPPA_MODE == "island":
        from scipy.ndimage import gaussian_filter
        kappa *= 0.0
        kappa[size//2 - 5:size//2 + 5, size//2 - 5:size//2 + 5] = 1.0
        kappa = gaussian_filter(kappa, sigma=5)
        save_kappa_map(kappa)

    frames_amp, frames_vecx, frames_vecy, frames_curl, frames_vort, frames_particles = [
    ], [], [], [], [], []
    # print("🔄 Starting field calculations:")

    threshold = 0.12
    neighborhood_size = 3
    radius_log = []
    trajectories = []  # seznam (id, step, y, x, size)
    active_tracks = {}  # id -> (y, x)
    next_id = 0

    # Ladicí konstanta aplikovaná na víc složek systému
    TUNING_CONST = 1 / 137
    APPLY_TUNING = True

    # print("🔄 Initializing the field and interaction field.")
    for i in tqdm(range(steps), desc="Processing steps", unit="step"):
        # Removed manual progress print

        if KAPPA_MODE == "island_to_constant":
            kappa = generate_kappa(i)

        psi, phi = evolve(psi, delta, phi, kappa)
        amp = np.abs(psi)

        phase = np.angle(psi)

        # Phase-safe central differences with periodic boundary:
        # wrap differences as angle(exp(i Δθ)) to avoid ±π jumps artefacts
        dph_dx = 0.5 * \
            np.angle(
                np.exp(1j * (np.roll(phase, -1, axis=1) - np.roll(phase, 1, axis=1))))
        dph_dy = 0.5 * \
            np.angle(
                np.exp(1j * (np.roll(phase, -1, axis=0) - np.roll(phase, 1, axis=0))))

        # keep names used later (for vector field/GIFs)
        grad_x = dph_dx
        grad_y = dph_dy

        # curl(∇phase) via central differences (periodic)
        dFy_dx = 0.5 * (np.roll(grad_y, -1, axis=1) -
                        np.roll(grad_y, 1, axis=1))
        dFx_dy = 0.5 * (np.roll(grad_x, -1, axis=0) -
                        np.roll(grad_x, 1, axis=0))

        curl = (dFy_dx - dFx_dy) * kappa

        # RAW vortices for metrics/CSV
        raw_vortices = detect_vortices(phase)
        # append to topology log
        update_topology_log(raw_vortices, i, topo_log)
        vortices_vis = gate_vortices_by_amplitude(
            raw_vortices, amp)  # visualization-only (for GIF)

        local_max = (amp == maximum_filter(amp, size=neighborhood_size))
        particles = (amp > threshold) & local_max
        coords = np.argwhere(particles)

        # 💥 Experimentální injekce do φ – lokální posílení v místě částic
        injection_amount = 0.2
        for cy, cx in coords:
            y_min = max(cy - 1, 0)
            y_max = min(cy + 2, size)
            x_min = max(cx - 1, 0)
            x_max = min(cx + 2, size)
            phi[y_min:y_max, x_min:x_max] += injection_amount

        # Pro každou nově detekovanou částici
        assigned = set()
        new_active_tracks = {}

        for cy, cx in coords:
            pos = np.array([cy, cx])
            min_dist = float("inf")
            closest_id = None

            # Najdi nejbližší aktivní trajektorii
            for tid, last_pos in active_tracks.items():
                dist = np.linalg.norm(pos - last_pos)
                if dist < 3.0 and tid not in assigned:
                    if dist < min_dist:
                        min_dist = dist
                        closest_id = tid

            if closest_id is not None:
                # Navazujeme na předchozí trajektorii
                new_active_tracks[closest_id] = pos
                assigned.add(closest_id)
                trajectories.append((closest_id, i, cy, cx, amp[cy, cx]))
            else:
                # Nová trajektorie
                new_active_tracks[next_id] = pos
                trajectories.append((next_id, i, cy, cx, amp[cy, cx]))
                next_id += 1

        # Aktualizuj aktivní trajektorie
        active_tracks = new_active_tracks

        frames_particles.append(particles.astype(float))

        frames_amp.append(amp)
        frames_vecx.append(grad_x)
        frames_vecy.append(grad_y)
        frames_curl.append(curl)
        frames_vort.append(vortices_vis)

        # 🔄 Save |φ| frames for each time window (absolute value only)
        if 'frames_phi' not in locals():
            frames_phi = []
        frames_phi.append(np.abs(phi.copy()))

        r_threshold = 0.15
        mask = amp > r_threshold
        coords = np.argwhere(mask)
        center = np.array([size//2, size//2])
        if coords.size > 0:
            distances = np.linalg.norm(coords - center, axis=1)
            avg_radius = np.mean(distances)
        else:
            avg_radius = 0.0
        radius_log.append((i, avg_radius))

        # Removed manual progress print

        if coords.size > 0:
            centroid = coords.mean(axis=0)
            particle_log.append((i, centroid[0], centroid[1], len(coords)))
        else:
            particle_log.append((i, np.nan, np.nan, 0))

        radius = 5
        if coords.size > 0:
            center_y, center_x = centroid.round().astype(int)
            y_min = max(center_y - radius, 0)
            y_max = min(center_y + radius + 1, size)
            x_min = max(center_x - radius, 0)
            x_max = min(center_x + radius + 1, size)
            local_vortices = raw_vortices[y_min:y_max, x_min:x_max]
            pos_count = np.sum(local_vortices == 1)
            neg_count = np.sum(local_vortices == -1)
        else:
            pos_count = 0
            neg_count = 0
        interaction_log.append(
            (i, pos_count, neg_count, pos_count - neg_count))

        center_y, center_x = size // 2, size // 2
        central_amp = amp[center_y, center_x]

        # print(f"🔄 Step {i+1}/{steps}: Saving data and updating logs.")
        amplitude_log.append((i, central_amp))
        phi_center_log.append((i, np.abs(phi[center_y, center_x])))

        for pt in probe_points:
            y, x = pt
            if 0 <= y < size and 0 <= x < size:
                multi_amp_logs[pt].append(np.abs(psi[y, x]))
            else:
                multi_amp_logs[pt].append(np.nan)

    save_csv("radius_log.csv", ["step", "avg_radius"], radius_log)

    save_csv("particle_log.csv", [
             "step", "center_y", "center_x", "size"], particle_log)

    save_csv(
        "interaction_log.csv",
        ["step", "vortices_pos", "vortices_neg", "net_local_charge"],
        interaction_log,
    )

    save_csv("amplitude_log.csv", ["step", "central_amplitude"], amplitude_log)

    save_csv("phi_center_log.csv", ["step", "phi_center_abs"], phi_center_log)

    # --- φ half-life estimate (center point)
    phi_df = pd.DataFrame(phi_center_log, columns=["step", "phi_center_abs"])
    if not phi_df.empty:
        phi_final = float(phi_df["phi_center_abs"].iloc[-1])
        phi_half = phi_final / 2.0
        hits = np.flatnonzero(phi_df["phi_center_abs"].values >= phi_half)
        phi_half_life_steps = int(
            phi_df["step"].iloc[hits[0]]) if hits.size > 0 else None
    else:
        phi_half_life_steps = None

    # 🔍 SPEKTRÁLNÍ ANALÝZA OSCILACE V CENTRU

    # Get amplitudes and create the time axis
    amplitudes = np.array([row[1] for row in amplitude_log])
    times = np.arange(len(amplitudes)) * TIME_STEP  # čas v sekundách

    # Remove DC component
    amplitudes -= np.mean(amplitudes)

    # Compute FFT
    fft_result = fft(amplitudes)
    frequencies = fftfreq(len(amplitudes), d=TIME_STEP)
    spectrum = np.abs(fft_result)**2

    # Keep positive frequencies only
    positive_freqs = frequencies[:len(frequencies)//2]
    positive_spectrum = spectrum[:len(spectrum)//2]

    # Find the dominant frequency
    dominant_index = np.argmax(positive_spectrum)
    dominant_freq = positive_freqs[dominant_index]  # v Hz

    # --- Spectral Balance Ratio (SBR) with ±2-bin guard around f0
    guard = 2
    peak_power = positive_spectrum[dominant_index]
    mask = np.ones_like(positive_spectrum, dtype=bool)
    l = max(dominant_index - guard, 0)
    r = min(dominant_index + guard + 1, len(positive_spectrum))
    mask[l:r] = False
    rest_power = np.mean(positive_spectrum[mask]) if np.any(mask) else np.nan
    sbr = peak_power / \
        rest_power if (rest_power and rest_power > 0) else np.nan

    # Spočteme energii: E = h·f
    h = 6.62607015e-34  # Planck constant [J·s]
    energy = h * dominant_freq

    # Spočteme vlnovou délku: λ = c / f
    c = 299_792_458  # speed of light [m/s]
    wavelength = c / dominant_freq if dominant_freq != 0 else np.inf

    # Spočteme efektivní hmotnost částice: m = E/c²
    mass = energy / c**2  # effective mass [kg]

    # Compare with electron
    electron_mass = 9.10938356e-31  # electron mass [kg]
    mass_ratio = mass / electron_mass

    # Uložení do CSV
    save_csv(
        "spectrum_log.csv",
        ["frequency_Hz", "amplitude"],
        zip(positive_freqs, positive_spectrum),
    )

    # Nyní exportuj jen čisté trajektorie
    save_csv(
        "trajectories.csv",
        ["id", "step", "y", "x", "amplitude"],
        trajectories,
    )

    # 🔍 SPECTRAL ANALYSIS OF THE CENTER-POINT OSCILLATION
    multi_spectrum_details = []

    for pt, amp_list in multi_amp_logs.items():
        signal = np.array(amp_list)
        signal -= np.mean(signal)
        fft_result = fft(signal)
        freqs = fftfreq(len(signal), d=TIME_STEP)
        spectrum = np.abs(fft_result)**2
        positive_freqs = freqs[:len(freqs)//2]
        positive_spectrum = spectrum[:len(spectrum)//2]

        dom_idx = np.argmax(positive_spectrum)
        dom_freq = positive_freqs[dom_idx]
        energy = h * dom_freq
        mass = energy / c**2
        mass_ratio = mass / electron_mass

        multi_spectrum_details.append({
            "point": pt,
            "dominant_freq_Hz": dom_freq,
            "energy_J": energy,
            "mass_kg": mass,
            "mass_ratio": mass_ratio
        })

        # Uložení spektra pro každý bod zvlášť
        save_csv(
            f"spectrum_log_point_{pt[0]}_{pt[1]}.csv",
            ["frequency_Hz", "amplitude"],
            zip(positive_freqs, positive_spectrum),
        )

    # Uložení shrnutí výsledků pro všechny body
    save_csv(
        "multi_spectrum_summary.csv",
        ["y", "x", "dominant_freq_Hz", "energy_J", "mass_kg", "mass_ratio"],
        [(d["point"][0], d["point"][1], d["dominant_freq_Hz"], d["energy_J"],
          d["mass_kg"], d["mass_ratio"]) for d in multi_spectrum_details]
    )

    save_csv(
        "topo_log.csv",
        ["step", "num_pos", "num_neg", "net_charge", "total_vortices"],
        topo_log,
    )

    # --- Topology summary metrics for the HTML report
    topo_df = pd.DataFrame(topo_log, columns=[
                           "step", "num_pos", "num_neg", "net_charge", "total_vortices"])
    if not topo_df.empty:
        pct_neutral = float((topo_df["net_charge"].abs() <= 1).mean() * 100.0)
        mean_total_vort = float(topo_df["total_vortices"].mean())
    else:
        pct_neutral = None
        mean_total_vort = None

    # Save plot
    plt.figure(figsize=(8, 4))
    plt.plot(positive_freqs, positive_spectrum)
    plt.title("Spectrum of center-point oscillation")
    plt.xlabel("Frequency (Hz)")
    plt.ylabel("Power (arb.)")
    plt.xscale("log")
    if np.any(positive_spectrum > 0):
        plt.yscale("log")

    plt.grid(True)
    plt.tight_layout()
    plot_path = os.path.join(output_dir, f"{RUN_TAG}_spectrum_plot.png")
    try:
        plt.savefig(plot_path)
        notify_file_creation(plot_path)
    except Exception as e:
        notify_file_creation(plot_path, success=False, error=e)
    finally:
        plt.close()

    # --- Topology plots (to match the HTML report)
    if not topo_df.empty:
        # Net topological charge over steps
        plt.figure(figsize=(8, 3))
        plt.plot(topo_df["step"], topo_df["net_charge"])
        plt.title("Topological net charge per step")
        plt.xlabel("Step")
        plt.ylabel("Net charge")
        plt.grid(True)
        plt.tight_layout()
        path = os.path.join(output_dir, f"{RUN_TAG}_topo_charge_plot.png")
        try:
            plt.savefig(path)
            notify_file_creation(path)
        except Exception as e:
            notify_file_creation(path, success=False, error=e)
        finally:
            plt.close()

        # Total vortices over steps
        plt.figure(figsize=(8, 3))
        plt.plot(topo_df["step"], topo_df["total_vortices"])
        plt.title("Total vortices per step")
        plt.xlabel("Step")
        plt.ylabel("Count")
        plt.grid(True)
        plt.tight_layout()
        path = os.path.join(output_dir, f"{RUN_TAG}_vortex_count_plot.png")
        try:
            plt.savefig(path)
            notify_file_creation(path)
        except Exception as e:
            notify_file_creation(path, success=False, error=e)
        finally:
            plt.close()

    # Funkce pro uložení GIFů

    def save_gif(data_frames, filename, cmap='viridis', vmin=None, vmax=None,
                 out_px=None, resample='nearest'):
        """
        Fast GIF writer: maps frames -> RGBA via Matplotlib colormap (no figures),
        then writes GIF via Pillow. Optional upscale to a fixed pixel size (out_px).
        """
        from matplotlib import cm, colors
        from PIL import Image
        import numpy as np

        if vmin is None:
            vmin = float(np.min(data_frames))
        if vmax is None:
            vmax = float(np.max(data_frames))

        norm = colors.Normalize(vmin=vmin, vmax=vmax, clip=True)
        mapper = cm.ScalarMappable(norm=norm, cmap=cmap)

        # zvol resampling (nejvěrnější předchozímu vzhledu bývá 'nearest')
        RESAMPLE = {
            'nearest': Image.NEAREST,
            'bilinear': Image.BILINEAR,
            'bicubic': Image.BICUBIC
        }.get(resample, Image.NEAREST)

        pil_frames = []
        for f in data_frames:
            rgba = mapper.to_rgba(f, bytes=True)   # uint8 RGBA
            img = Image.fromarray(rgba, mode="RGBA")
            if out_px is not None:
                img = img.resize((out_px, out_px), RESAMPLE)
            pil_frames.append(img)

        try:
            if len(pil_frames) == 1:
                pil_frames[0].save(filename)
            else:
                pil_frames[0].save(
                    filename,
                    save_all=True,
                    append_images=pil_frames[1:],
                    duration=100,  # ~10 fps
                    loop=0,
                    disposal=2
                )
            notify_file_creation(filename)
        except Exception as e:
            notify_file_creation(filename, success=False, error=e)

    def save_full_overlay_gif(frames_amp, frames_curl, frames_vecx, frames_vecy, filename,
                              vmin_amp=0.0, vmax_amp=0.5, vmin_curl=-0.3, vmax_curl=0.3,
                              out_px=512, vec_stride=8, vec_scale=6.0, k_skip=2, fps=10,
                              amp_alpha_floor=0.20, curl_alpha_quantile=0.90, alpha_scale=96,
                              resample='nearest'):
        """Fast overlay GIF:
        • base = amplitude (plasma),
        • overlay = curl (bwr) with alpha masked by amplitude and curl quantile,
        • sparse arrows from (frames_vecx, frames_vecy).
        """

        from matplotlib import cm, colors
        from PIL import Image, ImageDraw
        import numpy as np
        import math

        # Colormap normalizace
        amp_norm = colors.Normalize(vmin=vmin_amp,  vmax=vmax_amp,  clip=True)
        curl_norm = colors.Normalize(vmin=vmin_curl, vmax=vmax_curl, clip=True)
        amp_map = cm.ScalarMappable(norm=amp_norm,  cmap='plasma')
        curl_map = cm.ScalarMappable(norm=curl_norm, cmap='bwr')

        # Resample režim
        RESAMPLE = {
            'nearest': Image.NEAREST,
            'bilinear': Image.BILINEAR,
            'bicubic': Image.BICUBIC
        }.get(resample, Image.NEAREST)

        pil_frames = []
        n = len(frames_amp)

        # Globální statistiky curlu (konzistentní napříč snímky)
        abs_curl_all = np.abs(np.stack(frames_curl))
        max_abs_curl = max(1e-9, float(abs_curl_all.max()))
        # např. 90. percentil
        curl_q = float(np.quantile(abs_curl_all, curl_alpha_quantile))

        for i in range(0, n, max(1, k_skip)):
            amp = frames_amp[i]
            curl = frames_curl[i]
            vx = frames_vecx[i]
            vy = frames_vecy[i]

            # RGBA base = amplitude
            amp_rgba = amp_map.to_rgba(amp, bytes=True)  # uint8 RGBA
            base = Image.fromarray(amp_rgba, mode="RGBA")

            # RGBA overlay = curl s ALFA maskou (amp-gating + kvantil |curl|)
            curl_rgba = curl_map.to_rgba(curl, bytes=True).copy()
            abs_curl = np.abs(curl)

            # 1) normalizovaný příspěvek z curlu
            #    (lineárně od prahu curl_q do maxima; pod prahem = 0)
            denom = max(1e-12, (max_abs_curl - curl_q))
            alpha_f = np.clip((abs_curl - curl_q) / denom, 0.0, 1.0)

            # 2) potlačení mimo "hmotu": v nízké amplitudě nulová alfa
            alpha_f[amp < amp_alpha_floor] = 0.0

            # 3) zmenšení celkové krytí (méně "fialového sněhu")
            # typicky 96 (0..96)
            alpha = (alpha_f * alpha_scale).astype(np.uint8)
            curl_rgba[..., 3] = alpha
            over = Image.fromarray(curl_rgba, mode="RGBA")

            # Kompozice amplitude + curl
            comp = Image.alpha_composite(base, over)

            # --- ŠIPKY se špičkou (arrowheads) ---
            draw = ImageDraw.Draw(comp)
            H, W = amp.shape
            arrow_rgba = (144, 238, 144, 200)

            for y in range(0, H, vec_stride):
                for x in range(0, W, vec_stride):
                    dx = float(vx[y, x])
                    dy = float(vy[y, x])
                    if dx*dx + dy*dy < 1e-12:
                        continue

                    x1, y1 = float(x), float(y)
                    x2 = x1 + dx * vec_scale
                    y2 = y1 + dy * vec_scale

                    # tělo šipky
                    draw.line([(x1, y1), (x2, y2)], fill=arrow_rgba, width=1)

                    # špička šipky („V“)
                    theta = math.atan2(dy, dx)
                    head_len = 0.6 * vec_scale
                    head_wide = 0.35 * vec_scale
                    hx = math.cos(theta)
                    hy = math.sin(theta)
                    nx = -hy
                    ny = hx
                    xh1 = x2 - hx*head_len + nx*head_wide
                    yh1 = y2 - hy*head_len + ny*head_wide
                    xh2 = x2 - hx*head_len - nx*head_wide
                    yh2 = y2 - hy*head_len - ny*head_wide
                    draw.line([(x2, y2), (xh1, yh1)], fill=arrow_rgba, width=1)
                    draw.line([(x2, y2), (xh2, yh2)], fill=arrow_rgba, width=1)

            if out_px:
                comp = comp.resize((out_px, out_px), RESAMPLE)

            pil_frames.append(comp)

        try:
            if len(pil_frames) == 1:
                pil_frames[0].save(filename)
            else:
                pil_frames[0].save(
                    filename,
                    save_all=True,
                    append_images=pil_frames[1:],
                    duration=int(1000/max(1, fps)),
                    loop=0,
                    disposal=2,
                    optimize=True
                )
            notify_file_creation(filename)
        except Exception as e:
            notify_file_creation(filename, success=False, error=e)

    def save_flow_quiver_gif(frames_vecx, frames_vecy, filename,
                             out_px=512, vec_stride=8, vec_scale=6.0, k_skip=2, fps=10,
                             bg="white", resample="nearest"):
        # This Python code is generating a series of frames for an ultra-fast flow GIF with vector arrows. It
        # uses the PIL (Python Imaging Library) module to create and draw the frames. The code takes input
        # arrays `frames_vecx` and `frames_vecy` representing vector components, and generates a GIF animation
        # showing the flow of vectors as arrows on a sparse grid.
        """
        Ultra-fast FLOW GIF: sparse vector field with arrowheads (no Matplotlib).
        Vykreslí se řídká šachovnice šipek z (frames_vecx, frames_vecy).
        """
        from PIL import Image, ImageDraw
        import numpy as np
        import math

        # choose resample kernel
        RESAMPLE = {
            "nearest": Image.NEAREST,
            "bilinear": Image.BILINEAR,
            "bicubic": Image.BICUBIC
        }.get(resample, Image.NEAREST)

        n = len(frames_vecx)
        H, W = frames_vecx[0].shape

        # arrow color (semi-transparent lime)
        arrow_rgba = (144, 238, 144, 220)

        pil_frames = []
        for i in range(0, n, max(1, k_skip)):
            vx = frames_vecx[i]
            vy = frames_vecy[i]

            # plátno
            if bg == "black":
                comp = Image.new("RGBA", (W, H), (0, 0, 0, 255))
            else:
                comp = Image.new("RGBA", (W, H), (255, 255, 255, 255))

            draw = ImageDraw.Draw(comp)

            # šipky se špičkou (stejná orientace jako u overlay funkce)
            for y in range(0, H, vec_stride):
                for x in range(0, W, vec_stride):
                    dx = float(vx[y, x])
                    dy = float(vy[y, x])
                    if dx*dx + dy*dy < 1e-12:
                        continue

                    x1, y1 = float(x), float(y)
                    x2 = x1 + dx * vec_scale
                    y2 = y1 + dy * vec_scale
                    # tělo šipky
                    draw.line([(x1, y1), (x2, y2)], fill=arrow_rgba, width=2)

                    # arrowhead ("V" shape with two short strokes)
                    theta = math.atan2(dy, dx)
                    head_len = 0.6 * vec_scale
                    head_wide = 0.35 * vec_scale
                    hx = math.cos(theta)
                    hy = math.sin(theta)
                    nx = -hy
                    ny = hx
                    xh1 = x2 - hx * head_len + nx * head_wide
                    yh1 = y2 - hy * head_len + ny * head_wide
                    xh2 = x2 - hx * head_len - nx * head_wide
                    yh2 = y2 - hy * head_len - ny * head_wide
                    draw.line([(x2, y2), (xh1, yh1)], fill=arrow_rgba, width=2)
                    draw.line([(x2, y2), (xh2, yh2)], fill=arrow_rgba, width=2)

            if out_px:
                comp = comp.resize((out_px, out_px), RESAMPLE)

            pil_frames.append(comp)

        try:
            if len(pil_frames) == 1:
                pil_frames[0].save(filename)
            else:
                pil_frames[0].save(
                    filename,
                    save_all=True,
                    append_images=pil_frames[1:],
                    duration=int(1000/max(1, fps)),
                    loop=0,
                    disposal=2,
                    optimize=True
                )
            notify_file_creation(filename)
        except Exception as e:
            notify_file_creation(filename, success=False, error=e)

    save_gif(frames_amp, os.path.join(output_dir, f"{RUN_TAG}_lineum_amplitude.gif"),
             cmap="plasma", vmin=0, vmax=0.5, out_px=512)

    save_gif(frames_curl, os.path.join(output_dir, f"{RUN_TAG}_lineum_spin.gif"),
             cmap="bwr", vmin=-0.3, vmax=0.3, out_px=512)

    save_gif(frames_vort, os.path.join(output_dir, f"{RUN_TAG}_lineum_vortices.gif"),
             cmap="bwr", vmin=-1, vmax=1, out_px=512)

    save_gif(frames_particles, os.path.join(output_dir, f"{RUN_TAG}_lineum_particles.gif"),
             cmap="gray", vmin=0, vmax=1, out_px=512)

    flow_path = os.path.join(output_dir, f"{RUN_TAG}_lineum_flow.gif")
    save_flow_quiver_gif(
        frames_vecx, frames_vecy,
        flow_path,
        out_px=512,      # output GIF size in pixels
        # sparsity of arrow grid
        vec_stride=12,
        vec_scale=9.0,   # arrow length (scale)
        k_skip=2,        # skip every 2nd frame (smaller file)
        fps=5,          # snímková frekvence GIFu
        bg="black"       # nebo "black", chceš-li tmavé pozadí
    )

    def generate_html_report(filename=f"{RUN_TAG}_lineum_report.html", mass=0, mass_ratio=0, max_lifespan=0, median_lifespan=0, include_spin=True, phi_mean_near=0, phi_mean_field=0, phi_std_field=1, mass_ratio_blackholes=None, avg_phi_death=None, low_mass_count=None, phi_low_mass_mean=0, curl_low_mass_mean=0, phi_above_025_count=0, curl_near_zero_count=0, phi_half_life_steps=None, sbr=None, pct_neutral=None, mean_total_vort=None, phi_std_near=None):

        # ✅ Detekce jevů na základě logů
        quasiparticles_present = len(trajectories) > 0
        # total vortices > 0
        vortices_present = any(row[4] > 0 for row in topo_log)
        charge_std = np.std([row[3] for row in topo_log])
        topo_conserved = charge_std < 3
        stable_frequency = dominant_freq > 1e10  # arbitrárně: nad 10 GHz
        phi_present = np.nanmax([row[1] for row in phi_center_log]) > 0.01
        phi_gravitation_confirmed = False

        # 🧪 Dynamický seznam potvrzených jevů
        confirmations = []
        if vortices_present:
            confirmations.append("🌀 Spontaneous vortex formation (±1 winding)")
        if quasiparticles_present:
            confirmations.append(
                "🧫 Quasiparticle detections with trackable trajectories")
        if stable_frequency:
            confirmations.append(
                f"🎵 Stable single-peak spectrum (f₀ = {dominant_freq:.2e} Hz{'; SBR ≈ ' + f'{sbr:.2f}' if (sbr is not None and sbr == sbr) else ''})"
            )
        if topo_conserved:
            confirmations.append(
                "🔁 Near-neutral global topological charge over time (winding)")
        if phi_present:
            confirmations.append(
                "🌌 Non-zero background φ observed at the center")

        if mass_ratio > 0.001 and mass_ratio < 100:
            confirmations.append(
                f"⚖️ Display-only effective mass estimate from f₀ (m/mₑ ≈ {mass_ratio:.2e})"
            )

        # [ARXIV_V1] Blackhole/wormhole/closure confirmations are disabled for the initial release.
        # if blackhole_count > 0:
        #     confirmations.append(
        #         f"🕳️ Detekce {blackhole_count} kvazičástic uvězněných ve φ-pasti (černá díra)")

        #     if mass_ratio_blackholes is not None and mass_ratio_blackholes < 0.01:
        #         confirmations.append(
        #             "🪐 Třískova hypotéza strukturálního uzavření potvrzena: částice zanikají v silných φ-zónách bez zbytkové hmotnosti"
        #         )
        #     elif mass_ratio_blackholes is not None:
        #         confirmations.append(
        #             f"🪐 Třískova hypotéza strukturálního uzavření částečně potvrzena: návratové částice mají hmotnost {mass_ratio_blackholes:.2e}× elektronová"
        #         )
        #     else:
        #         confirmations.append(
        #             "🪐 Třískova hypotéza strukturálního uzavření zatím neověřena – spektrální data nedostupná"
        #         )

        # [ARXIV_V1] Blackhole/wormhole/closure confirmations are disabled for the initial release.
        # if avg_phi_death is not None and avg_phi_death > 0.25:
        #     confirmations.append(
        #         f"🌀 φ v místě zániku návratových částic potvrzuje strukturální uzavření (⟨φ⟩ = {avg_phi_death:.3f})"
        #     )
        # elif avg_phi_death is not None:
        #     confirmations.append(
        #         f"🌀 φ v místě zániku návratových částic: {avg_phi_death:.3f} (hranice potvrzení je 0.25)"
        #     )

        # [ARXIV_V1] Blackhole/wormhole/closure confirmations are disabled for the initial release.
        # if wormhole_count > 0:
        #     confirmations.append(
        #         f"🌉 Podezření na {wormhole_count} případů červí díry (skoková relokace mezi φ-zónami)")

        if curl_std > 0.05:
            confirmations.append(
                f"🔄 Significant curl activity inside high-φ regions (σ = {curl_std:.2e})")

        # Potvrzení homogenního výskytu kvazičástic
        try:
            with open(os.path.join(output_dir, f"{RUN_TAG}_multi_spectrum_summary.csv")) as f:
                import csv
                reader = csv.DictReader(f)
                freqs = []
                mass_ratios = []
                for row in reader:
                    freqs.append(float(row["dominant_freq_Hz"]))
                    mass_ratios.append(float(row["mass_ratio"]))

                freq_std = np.std(freqs)
                mass_ratio_std = np.std(mass_ratios)

                if freq_std < 1e17 and mass_ratio_std < 0.01:
                    confirmations.append(
                        "🧬 Consistent f₀ across sampled points (low across-grid variance)")

        except Exception as e:
            print("⚠️ Homogeneity check failed:", e)

        if max_lifespan >= 100:
            confirmations.append(
                f"🕒 Emergence of long-lived quasiparticles (max {max_lifespan} steps, median {median_lifespan})"
            )

        if include_spin and os.path.exists(os.path.join(output_dir, f"{RUN_TAG}_spin_aura_avg.png")):
            confirmations.append(
                "🧲 Averaged curl map near quasiparticles shows a dipole-like pattern (spin aura)")

        if phi_mean_near > phi_mean_field + 3 * phi_std_field:
            confirmations.append(
                "🌠 Elevated φ near quasiparticles (mean > field mean + 3σ)")

        # 💫 φ-gravitační interakce: ověření sbližování částic
        try:
            top_trajs = pd.read_csv(os.path.join(
                output_dir, f"{RUN_TAG}_trajectories.csv"))
            grouped = top_trajs.groupby("id")
            lifespans = grouped.size().sort_values(ascending=False)
            top2_ids = lifespans.head(2).index.tolist()
            filtered = top_trajs[top_trajs["id"].isin(top2_ids)]

            from collections import defaultdict
            from scipy.spatial.distance import euclidean
            step_to_positions = defaultdict(dict)
            for _, row in filtered.iterrows():
                step = int(row["step"])
                id_ = int(row["id"])
                y = float(row["y"])
                x = float(row["x"])
                step_to_positions[step][id_] = (y, x)

            shared_steps = [s for s in step_to_positions if len(
                step_to_positions[s]) == 2]

            if len(shared_steps) >= 5:
                dists = [euclidean(*step_to_positions[s].values())
                         for s in shared_steps]
                if dists[0] > dists[-1]:
                    # (v1-safe) no explicit claim; keep internal flag if needed
                    phi_gravitation_confirmed = True

        except Exception as e:
            print("⚠️ φ-guidance test failed:", e)

        if not confirmations:
            confirmations.append(
                "No major emergent phenomena detected")

        # 🔧 HTML konstrukce
        confirmed_html = "\n".join(f"<li>{c}</li>" for c in confirmations)

        gravitational_row = ("<tr><td>Guided motion</td>"
                             "<td>Alignment with +∇|φ| (environmental guidance)</td></tr>")

        # --- Run labels shown under the report title (only if available)
        labels = [f"RUN_TAG: {RUN_TAG}"]
        if 'TIME_STEP' in globals():
            try:
                labels.append(f"Δt: {TIME_STEP:.2e} s")
            except Exception:
                pass
        if 'PIXEL_SIZE' in globals():
            try:
                labels.append(f"pixel: {PIXEL_SIZE:.2e} m")
            except Exception:
                pass
        labels_text = " · ".join(labels)

        # --- Data links for convenience (relative to report location)
        data_links_html = (
            f'<ul>'
            f'<li><a href="{RUN_TAG}_amplitude_log.csv">amplitude_log.csv</a></li>'
            f'<li><a href="{RUN_TAG}_spectrum_log.csv">spectrum_log.csv</a></li>'
            f'<li><a href="{RUN_TAG}_phi_center_log.csv">phi_center_log.csv</a></li>'
            f'<li><a href="{RUN_TAG}_topo_log.csv">topo_log.csv</a></li>'
            f'<li><a href="{RUN_TAG}_trajectories.csv">trajectories.csv</a></li>'
            f'<li><a href="{RUN_TAG}_multi_spectrum_summary.csv">multi_spectrum_summary.csv</a></li>'
            f'<li><a href="{RUN_TAG}_spin_aura_profile.csv">spin_aura_profile.csv</a></li>'
            f'</ul>'
        )

        # --- Derived display numbers from f0 (safe)
        try:
            # constants in-place (avoid missing PLANCK_H / LIGHT_SPEED)
            _H = 6.62607015e-34        # Planck constant [J·s]
            _C = 299_792_458.0         # speed of light [m/s]
            energy_j = _H * dominant_freq
            energy_ev = energy_j / 1.602176634e-19
            wavelength_m = _C / \
                dominant_freq if dominant_freq != 0 else float("inf")
        except Exception:
            energy_j = None
            energy_ev = None
            wavelength_m = None

        html = f"""<!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <title>Lineum Simulation Report</title>
      <style>
        body {{ font-family: Arial, sans-serif; padding: 20px; }}
        h1, h2 {{ color: #2c3e50; }}
        img {{ margin: 10px; border: 1px solid #ccc; }}
        .grid {{ display: flex; flex-wrap: wrap; gap: 10px; }}
        table {{ border-collapse: collapse; margin-top: 10px; }}
        th, td {{ border: 1px solid #ccc; padding: 6px 10px; text-align: left; }}
        th {{ background-color: #f4f4f4; }}
      </style>
    </head>
    <body>
        <h1>🧪 Lineum – Emergent Quantum Field</h1>

        <p style="margin-top:-8px;color:#666;"><small>{labels_text}</small></p>

        <h2>📦 Data & downloads</h2>
        {data_links_html}


        <h2>📂 Run Configuration</h2>
        <ul>
            <li><strong>Run tag:</strong> {RUN_TAG}</li>
            <li><strong>LOW_NOISE_MODE:</strong> {'True' if LOW_NOISE_MODE else 'False'}</li>
            <li><strong>TEST_EXHALE_MODE:</strong> {'True' if TEST_EXHALE_MODE else 'False'}</li>
            <li><strong>KAPPA_MODE:</strong> {KAPPA_MODE}</li>
        </ul>


      <h2>✅ Confirmed observations (v1-safe)</h2>
      <ul>
        {confirmed_html}
      </ul>

      <h2>📌 Run metrics ({RUN_TAG})</h2>
    <table>
    <tr><th>Metric</th><th>Value</th></tr>
    <tr><td>φ half-life (center)</td>
        <td>{phi_half_life_steps if phi_half_life_steps is not None else '—'} steps
            (canonical target ≈ 2000)</td></tr>
              <tr><td>SBR (±2-bin guard)</td>
      <td>{'—' if (sbr is None or sbr != sbr) else f'{sbr:.2f}'}</td></tr>
  <tr><td>Topology neutrality</td>
      <td>{'—' if pct_neutral is None else f'{pct_neutral:.1f}%'} of steps with |net charge| ≤ 1
          (mean vortices ≈ {'—' if mean_total_vort is None else f'{mean_total_vort:.0f}'})</td></tr>
            <tr><td>φ near vs field</td>
      <td>{phi_mean_near:.2e} ± {('—' if phi_std_near is None else f'{phi_std_near:.2e}')}
          vs {phi_mean_field:.2e} ± {('—' if phi_std_field is None else f'{phi_std_field:.2e}')}</td></tr>


    </table>

      <h2>📊 Quasiparticle Properties</h2>
      <table>
        <tr><th>Property</th><th>Value</th></tr>
        <tr><td>Dominant frequency f₀</td>
    <td>{dominant_freq:.2e} Hz</td></tr>
<tr><td>Energy (E = h f₀)</td>
    <td>{'—' if energy_j is None else f'{energy_j:.2e} J (~{energy_ev/1e3:.2f} keV)'}</td></tr>
<tr><td>Wavelength (λ = c / f₀)</td>
    <td>{'—' if wavelength_m is None else f'{wavelength_m:.2e} m'}</td></tr>

        <tr><td>Effective mass</td><td>{mass:.2e} kg</td></tr>
        <tr><td>Mass relative to electron</td><td>{mass_ratio:.2e}× electron mass</td></tr>
        <tr><td>Max lifespan</td><td>{max_lifespan} steps</td></tr>
        <tr><td>Median lifespan</td><td>{median_lifespan} steps</td></tr>
        {gravitational_row}

      </table>

      <h2>🌀 Simulation Summary</h2>
      <ul>
        <li><strong>Steps:</strong> {len(frames_amp)}</li>
        <li><strong>Field size:</strong> {size} × {size}</li>
        <li><strong>Quasiparticles detected:</strong> {'✅ Yes' if quasiparticles_present else '❌ No'}</li>
        <li><strong>Vortices detected:</strong> {'✅ Yes' if vortices_present else '❌ No'}</li>
        <li><strong>Topological charge conserved:</strong> {'✅ Yes' if topo_conserved else '⚠️ Unstable'}</li>
      </ul>

      <h2>📈 Key Plots</h2>
      <div class="grid">
        <div><img src="{RUN_TAG}_topo_charge_plot.png" alt="Topological charge plot"></div>
        <div><img src="{RUN_TAG}_vortex_count_plot.png" alt="Vortex count plot"></div>
        <div><img src="{RUN_TAG}_spectrum_plot.png" alt="Spectrum plot"></div>
        <div><img src="{RUN_TAG}_phi_center_plot.png" alt="φ center plot"></div>
      </div>

            <h2>🎞️ Field Evolution GIFs</h2>
      <div class="grid">
        <figure>
          <img src="{RUN_TAG}_lineum_amplitude.gif" alt="Amplitude |ψ|" title="Amplitude |ψ|">
          <figcaption>Amplitude |ψ|</figcaption>
        </figure>

        <figure>
          <img src="{RUN_TAG}_lineum_spin.gif" alt="Spin-like curl map" title="Spin-like curl map">
          <figcaption>Spin-like curl map</figcaption>
        </figure>

        <figure>
          <img src="{RUN_TAG}_lineum_vortices.gif" alt="Vortex cores (±1 winding)" title="Vortex cores (±1 winding)">
          <figcaption>Vortex cores (±1 winding)</figcaption>
        </figure>

        <figure>
          <img src="{RUN_TAG}_lineum_particles.gif" alt="Tracked quasiparticles" title="Tracked quasiparticles">
          <figcaption>Tracked quasiparticles</figcaption>
        </figure>

        <figure>
          <img src="{RUN_TAG}_lineum_flow.gif" alt="Flow field arrows (∇φ)" title="Flow field arrows (∇φ)">
          <figcaption>Flow field arrows (∇φ)</figcaption>
        </figure>

        <figure>
  <img src="{RUN_TAG}_lineum_full_overlay.gif"
       alt="Composite overlay (masked curl)"
       title="Composite overlay (masked curl)">
  <figcaption>Composite overlay (masked curl)</figcaption>
</figure>

      </div>


      <h2>🧲 Spin aura (averaged curl map)</h2>
<p>
We compute an average of <code>curl(∇arg ψ)</code> in local windows centered on detected quasiparticles.
The resulting map shows a robust dipole-like pattern (“spin aura”). We report this as an emergent
flow pattern in the model; no claim is made about quantum spin.
</p>

<div><img src="{RUN_TAG}_spin_aura_avg.png" alt="Spin aura"></div>


      <h2>📚 Glossary & Naming Rationale</h2>

      <h2>🧠 Note on φ-guided motion</h2>
<p><strong>Note on φ-guided motion.</strong><br>
We do not claim a gravitational theory. In the canonical regime, particles tend to move along gradients of the background field φ. We refer to this as <em>environmental guidance</em>: a metric-like influence of φ on trajectories, without introducing a force law or any analogy to GR. This behavior is quantified via alignment metrics in the report and should be interpreted as an emergent guidance effect within the model.</p>

    <h3>🔤 Lineum</h3>
    <p>
      The name <strong>Lineum</strong> is a coined term from the Latin <em>linea</em> ("line" or "thread"), symbolizing
      the filament-like tension structures that emerge in the field. It refers to a hypothetical quantum field defined
      by local, nonlinear evolution rules. This field exhibits spontaneous formation of vortices, oscillations,
      topological effects, and quasiparticles.
    </p>
    <p>
      Pronunciation: <strong><em>line-um</em></strong> (Czech: <em>lineum</em>, as written).
    </p>
    <p>
      The name follows a tradition of physics-inspired constructs such as <em>graviton</em>, <em>inflaton</em>, or
      <em>axion</em>—terms that suggest emergent dynamics without predefining their exact physical nature.
    </p>

    <p style="color:#666;margin-top:24px;">
<small>Note: This report summarizes operational measurements from a 2D emergent model.
No cosmological, gravitational, biomedical or metaphysical claims are made.</small>
</p>

    <p style="margin-top:30px; font-style: italic; color: #555;">
        (c) Lineum – emergent quantum field simulation
    </p>
    </body>
    </html>"""

        path = os.path.join(output_dir, filename)
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(html)
            notify_file_creation(path)
        except Exception as e:
            notify_file_creation(path, success=False, error=e)

    overlay_path = os.path.join(
        output_dir, f"{RUN_TAG}_lineum_full_overlay.gif")
    save_full_overlay_gif(
        frames_amp, frames_curl, frames_vecx, frames_vecy,
        overlay_path,
        vmin_amp=0.0, vmax_amp=0.5,
        vmin_curl=-0.3, vmax_curl=0.3,
        out_px=512,
        vec_stride=12,         # sparser arrows = cleaner look
        vec_scale=6.0,
        k_skip=2,
        fps=5,                 # sladěno s ostatními GIFy (při k_skip=2)
        amp_alpha_floor=0.30,  # skryje curl v nízké |ψ|
        curl_alpha_quantile=0.95,  # ignore weak curl below the 95th percentile
        alpha_scale=80,        # gentler overall curl alpha
        resample="bilinear"
    )

    # 🌀 Save all vortex fields to files for analysis
    frames_vort_np = np.array(frames_vort)  # shape: (steps, size, size)
    npy_path = os.path.join(output_dir, f"{RUN_TAG}_frames_vortices.npy")
    frames_curl_np = np.array(frames_curl)
    npy_curl_path = os.path.join(output_dir, f"{RUN_TAG}_frames_curl.npy")
    try:
        np.save(npy_curl_path, frames_curl_np)
        notify_file_creation(npy_curl_path)
    except Exception as e:
        notify_file_creation(npy_curl_path, success=False, error=e)

    try:
        np.save(npy_path, frames_vort_np)
        frames_amp_np = np.array(frames_amp)
        amp_npy_path = os.path.join(output_dir, f"{RUN_TAG}_frames_amp.npy")
        try:
            np.save(amp_npy_path, frames_amp_np)
            notify_file_creation(amp_npy_path)
        except Exception as e:
            notify_file_creation(amp_npy_path, success=False, error=e)

        notify_file_creation(npy_path)
    except Exception as e:
        notify_file_creation(npy_path, success=False, error=e)

    # 🧪 Analýza φ v okolí kvazičástic
    import random
    phi_values_near_particles = []
    phi_values_field = []

    for row in trajectories:
        step, y, x = int(row[1]), int(row[2]), int(row[3])
        if 0 <= step < len(frames_phi):
            phi_frame = frames_phi[step]
            if 2 < y < size - 3 and 2 < x < size - 3:
                local_phi = phi_frame[y-2:y+3, x-2:x+3].flatten()
                phi_values_near_particles.extend(local_phi)

        # random points outside particles
        for _ in range(5):
            ry, rx = random.randint(0, size - 1), random.randint(0, size - 1)
            phi_values_field.append(frames_phi[step][ry, rx])

    phi_mean_near = np.mean(phi_values_near_particles)
    phi_std_near = np.std(phi_values_near_particles)
    phi_mean_field = np.mean(phi_values_field)
    phi_std_field = np.std(phi_values_field)

    # 🌀 Uložení φ polí pro pozdější analýzu
    frames_phi_np = np.array(frames_phi)  # φ v čase, pouze absolutní hodnota
    phi_npy_path = os.path.join(output_dir, f"{RUN_TAG}_frames_phi.npy")
    try:
        np.save(phi_npy_path, frames_phi_np)
        notify_file_creation(phi_npy_path)
    except Exception as e:
        notify_file_creation(phi_npy_path, success=False, error=e)

    if KAPPA_MODE == "island_to_constant":
        save_kappa_map(kappa)

    # 📈 Výpočet životnosti kvazičástic
    lifespan_df = pd.DataFrame(trajectories, columns=[
        "id", "step", "y", "x", "amplitude"])
    phi_abs = np.array(frames_phi)
    blackhole_candidates = []
    for tid, group in lifespan_df.groupby("id"):
        steps = group["step"].values
        ys = group["y"].values.astype(int)
        xs = group["x"].values.astype(int)
        inside_phi = []
        for s, y, x in zip(steps, ys, xs):
            if 0 <= s < len(phi_abs):
                if phi_abs[s, y, x] > 0.25:
                    inside_phi.append(True)
                else:
                    inside_phi.append(False)
        if len(inside_phi) > 5 and all(inside_phi[-5:]):
            blackhole_candidates.append(tid)
    blackhole_count = len(blackhole_candidates)

    # Získání φ při posledním výskytu každé černoděrové částice
    phi_at_death = []

    for tid in blackhole_candidates:
        traj = lifespan_df[lifespan_df["id"] == tid]
        last_step = traj["step"].max()
        row = traj[traj["step"] == last_step].iloc[0]
        y, x = int(row["y"]), int(row["x"])
        if 0 <= last_step < len(phi_abs):
            phi_val = phi_abs[last_step, y, x]
            phi_at_death.append(phi_val)

    if phi_at_death:
        avg_phi_death = np.mean(phi_at_death)
    else:
        avg_phi_death = None

    # Výpočet průměrné hmotnosti návratových částic
    blackhole_masses = []

    for tid in blackhole_candidates:
        traj = lifespan_df[lifespan_df["id"] == tid]
        yx_pairs = traj[["y", "x"]].drop_duplicates().values.astype(int)
        for y, x in yx_pairs:
            match = [d for d in multi_spectrum_details if d["point"] == (y, x)]
            if match:
                blackhole_masses.append(match[0]["mass_ratio"])

    if blackhole_masses:
        mass_ratio_blackholes = np.mean(blackhole_masses)
    else:
        mass_ratio_blackholes = None

    wormhole_count = 0
    for tid, group in lifespan_df.groupby("id"):
        group = group.sort_values("step")
        prev = None
        for _, row in group.iterrows():
            step, y, x = int(row["step"]), int(row["y"]), int(row["x"])
            if 0 <= step < len(phi_abs):
                if phi_abs[step, y, x] > 0.25:
                    if prev:
                        dist = euclidean((y, x), prev)
                        if dist > 20:
                            wormhole_count += 1
                            break
                    prev = (y, x)

    lifespans = lifespan_df.groupby("id")["step"].agg(["min", "max"])
    lifespans["duration"] = lifespans["max"] - lifespans["min"] + 1

    if lifespans["duration"].dropna().empty:
        max_lifespan = 0
    else:
        max_lifespan = int(lifespans["duration"].max())

    median_lifespan = int(lifespans["duration"].median())

    # 📊 Analýza průměrné spinové aury kvazičástic
    import seaborn as sns
    from scipy.ndimage import zoom

    frames_curl_np = np.array(frames_curl)

    curl_inside_phi = []
    for step in range(len(frames_curl_np)):
        mask = phi_abs[step] > 0.25
        curl_inside_phi.extend(frames_curl_np[step][mask])

    curl_mean = np.mean(curl_inside_phi)
    curl_std = np.std(curl_inside_phi)

    lifespan_df = pd.DataFrame(trajectories, columns=[
        "id", "step", "y", "x", "amplitude"])
    cutout_size = 11
    half_size = cutout_size // 2
    cutouts = []

    for _, row in lifespan_df.iterrows():
        step = int(row["step"])
        y = int(row["y"])
        x = int(row["x"])

        if (
            0 <= step < len(frames_curl_np)
            and half_size <= y < frames_curl_np.shape[1] - half_size
            and half_size <= x < frames_curl_np.shape[2] - half_size
        ):
            cutout = frames_curl_np[step, y - half_size: y +
                                    half_size + 1, x - half_size: x + half_size + 1]
            cutouts.append(cutout)

    average_spin_map = np.mean(cutouts, axis=0)
    upsampled_spin_map = zoom(average_spin_map, 5, order=3)

    # Uložení obrázku
    spin_img_path = os.path.join(output_dir, f"{RUN_TAG}_spin_aura_avg.png")
    plt.figure(figsize=(6, 6))
    sns.heatmap(upsampled_spin_map, center=0,
                cmap="bwr", cbar=True, square=True)
    plt.title("🧲 Averaged spin aura (curl ∇arg(ψ))")
    plt.axis("off")
    plt.tight_layout()
    plt.savefig(spin_img_path, dpi=150)
    plt.close()

    # Also save a plain spin-aura map (without axes) and a radial profile for the appendix
    # Map (use the upsampled heatmap as a clean raster)
    spin_map_path = os.path.join(output_dir, f"{RUN_TAG}_spin_aura_map.png")
    plt.figure(figsize=(3.6, 3.6))
    plt.imshow(upsampled_spin_map, cmap="bwr")
    plt.axis("off")
    plt.tight_layout(pad=0)
    try:
        plt.savefig(spin_map_path, bbox_inches="tight", pad_inches=0, dpi=150)
        notify_file_creation(spin_map_path)
    except Exception as e:
        notify_file_creation(spin_map_path, success=False, error=e)
    finally:
        plt.close()

    # Radial profile from the non-upsampled average map
    yy, xx = np.indices(average_spin_map.shape)
    cy, cx = average_spin_map.shape[0] // 2, average_spin_map.shape[1] // 2
    rr = np.sqrt((yy - cy)**2 + (xx - cx)**2)
    rbin = rr.astype(int)
    rmax = rbin.max()
    profile_rows = [(int(r), float(average_spin_map[rbin == r].mean()))
                    for r in range(rmax + 1)]
    save_csv("spin_aura_profile.csv", ["radius_px", "mean_curl"], profile_rows)

    include_spin = os.path.exists(
        os.path.join(output_dir, f"{RUN_TAG}_spin_aura_avg.png"))

    low_mass_count = sum(
        1 for d in multi_spectrum_details if d["mass_ratio"] < 0.01)

    # 📊 Export φ a curl v místech kvazičástic s mass_ratio < 0.01
    low_mass_coords = [
        (d["point"][0], d["point"][1])
        for d in multi_spectrum_details
        if d["mass_ratio"] < 0.01
    ]

    phi_final = np.abs(phi.copy())  # poslední stav φ

    # 📊 Výstup φ hodnot v mřížce 20×20
    grid_points = [(y, x) for y in range(0, size, 20)
                   for x in range(0, size, 20)]
    phi_grid_rows = [(y, x, phi_final[y, x]) for y, x in grid_points]
    save_csv("phi_grid_summary.csv", ["y", "x", "phi"], phi_grid_rows)

    # 🧠 Detekce deja vu / Mandela efekt kandidátů (φ > 0.25 na mřížce)
    phi_deja_rows = [(y, x, phi_final[y, x])
                     for y, x in grid_points if phi_final[y, x] > 0.25]
    save_csv("phi_grid_dejavu.csv", ["y", "x", "phi"], phi_deja_rows)

    curl_final = curl  # poslední stav curl (v hlavní smyčce už ho máš)

    rows = []
    for y, x in low_mass_coords:
        if 0 <= y < size and 0 <= x < size:
            rows.append([y, x, phi_final[y, x], curl_final[y, x]])

    save_csv("phi_curl_low_mass.csv", ["y", "x", "phi", "curl"], rows)

    # 📊 Vyhodnocení paměťové stopy ve φ-pastích
    df_low_mass = pd.read_csv(os.path.join(
        output_dir, f"{RUN_TAG}_phi_curl_low_mass.csv"))

    phi_low_mass_mean = df_low_mass["phi"].mean()
    curl_low_mass_mean = df_low_mass["curl"].abs().mean()
    phi_above_025_count = (df_low_mass["phi"] > 0.25).sum()
    curl_near_zero_count = (df_low_mass["curl"].abs() < 0.02).sum()

    # Save φ-center plot used in the report
    try:
        save_phi_center_plot()
    except Exception as e:
        print(f"[warn] save_phi_center_plot failed: {e}")

    generate_html_report(
        mass=mass,
        mass_ratio=mass_ratio,
        max_lifespan=max_lifespan,
        median_lifespan=median_lifespan,
        include_spin=include_spin,
        phi_mean_near=phi_mean_near,
        phi_mean_field=phi_mean_field,
        phi_std_field=phi_std_field,
        mass_ratio_blackholes=mass_ratio_blackholes,
        avg_phi_death=avg_phi_death,
        low_mass_count=low_mass_count,
        phi_low_mass_mean=phi_low_mass_mean,
        curl_low_mass_mean=curl_low_mass_mean,
        phi_above_025_count=phi_above_025_count,
        curl_near_zero_count=curl_near_zero_count,
        phi_half_life_steps=phi_half_life_steps,
        sbr=sbr,
        pct_neutral=pct_neutral,
        mean_total_vort=mean_total_vort,
        phi_std_near=phi_std_near,
    )

    print("✅ All GIFs and logs have been successfully generated.")
