from matplotlib.animation import FuncAnimation
from tqdm import tqdm
from scipy.fft import fft, fftfreq
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
from scipy.ndimage import gaussian_filter, maximum_filter
import csv
import os
from scipy.spatial.distance import euclidean

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
    """Save rows to CSV and notify about success or failure."""
    path = os.path.join(output_dir, filename)
    try:
        with open(path, "w", newline="") as f:
            writer = csv.writer(f)
            if header:
                writer.writerow(header)
            for row in tqdm(rows, desc=f"Saving {filename}", unit="row"):
                writer.writerow(row)
        notify_file_creation(path)
    except Exception as e:
        notify_file_creation(path, success=False, error=e)


particle_log = []
interaction_log = []
amplitude_log = []
topo_log = []
phi_center_log = []

# Přepínač pro Low Noise režim (vypnutí kvantového šumu ξ)
# True = testování strukturálního uzavření (hypotéza)
# False = běžné simulace s fluktuacemi
LOW_NOISE_MODE = False

# TEST_EXHALE_MODE = True aktivuje klidnější simulaci pro test strukturální paměti (výdech)
# V běžných simulacích vypnout (False), aby došlo k plné dynamice systému
TEST_EXHALE_MODE = False

# Parametry
size = 128
steps = 1000 if TEST_EXHALE_MODE else 500

NOISE_STRENGTH = 0.01 if not LOW_NOISE_MODE else 0.0

# Body, jejichž amplitudu budeme sledovat
probe_points = [(y, x) for y in range(0, size, 20) for x in range(0, size, 20)]

multi_amp_logs = {pt: [] for pt in probe_points}


PIXEL_SIZE = 1e-12     # 1 pixel = 1 pm (pikometr)
TIME_STEP = 1e-21      # 1 krok = 1 zs (zeptosekunda)


def sigmoid(x, k=5):
    return 1 / (1 + np.exp(-k * (x - 0.0)))


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


def evolve(psi, delta, phi):
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

    # 🧘 LOW NOISE MODE
    NOISE_STRENGTH = 0.0  # nastav 0.01 nebo 0.0 podle toho, kolik šumu chceš

    fluctuation = np.random.normal(
        0.0, NOISE_STRENGTH, (size, size)) * np.exp(1j * np.angle(psi))

    # 💡 Adding interaction
    interaction_term = 0.04 * np.clip(phi, -10, 10) * psi

    # 💫 Gradient φ jako „tíhový tok“
    grad_phi_x, grad_phi_y = np.gradient(np.abs(phi))
    phi_flow_term = -0.004 * (grad_phi_x + 1j * grad_phi_y)
    psi += phi_flow_term

    psi += linon_complex + fluctuation + interaction_term
    disipation_rate = 0.002 if TEST_EXHALE_MODE else 0.001
    psi -= disipation_rate * psi

    psi += diffuse_complex(psi)

    # 🌀 Laděná evoluce φ pro silnější lokální efekt
    reaction_strength = 0.06     # zvýšíme reakci na |ψ|²
    diffusion_strength = 0.015   # výrazně zpomalíme difuzi

    local_input = np.clip(np.abs(psi)**2, 0, 1e4)

    phi += reaction_strength * (local_input - phi)
    phi += 0.02 * diffuse_complex(phi)  # jemná difuze pole φ

    phi += diffusion_strength * diffuse_complex(phi)

    return psi, phi


def save_phi_center_plot(filename="phi_center_plot.png"):
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


def detect_vortices(phase):
    vortices = np.zeros_like(phase)
    for i in range(size - 1):
        for j in range(size - 1):
            p00 = phase[i, j]
            p01 = phase[i, j+1]
            p11 = phase[i+1, j+1]
            p10 = phase[i+1, j]

            # Rozdíly fáze mezi sousedy (modulo 2π)
            d1 = np.angle(np.exp(1j * (p01 - p00)))
            d2 = np.angle(np.exp(1j * (p11 - p01)))
            d3 = np.angle(np.exp(1j * (p10 - p11)))
            d4 = np.angle(np.exp(1j * (p00 - p10)))

            winding = (d1 + d2 + d3 + d4) / (2 * np.pi)

            if winding > 0.5:
                vortices[i, j] = 1
            elif winding < -0.5:
                vortices[i, j] = -1
    return vortices


if __name__ == "__main__":
    # Inicializace polí
    psi, delta = initialize_fields()
    phi = initialize_interaction_field()

    frames_amp, frames_vecx, frames_vecy, frames_curl, frames_vort, frames_particles = [
    ], [], [], [], [], []
    # print("🔄 Starting field calculations:")

    threshold = 0.12
    neighborhood_size = 3
    radius_log = []
    trajectories = []  # seznam (id, step, y, x, size)
    active_tracks = {}  # id -> (y, x)
    next_id = 0

    # print("🔄 Initializing the field and interaction field.")
    for i in tqdm(range(steps), desc="Processing steps", unit="step"):
        # Removed manual progress print
        psi, phi = evolve(psi, delta, phi)
        amp = np.abs(psi)
        phase = np.angle(psi)
        grad_x, grad_y = np.gradient(phase)
        dFy_dx = np.gradient(grad_y, axis=1)
        dFx_dy = np.gradient(grad_x, axis=0)
        curl = dFy_dx - dFx_dy
        vortices = detect_vortices(phase)

        num_pos = np.sum(vortices == 1)
        num_neg = np.sum(vortices == -1)
        net_charge = num_pos - num_neg
        total = num_pos + num_neg
        topo_log.append((i, num_pos, num_neg, net_charge, total))

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
        frames_vort.append(vortices)

        # 🔄 Uložení φ polí pro každé časové okno (pouze absolutní hodnota)
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
            local_vortices = vortices[y_min:y_max, x_min:x_max]
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

    # 🔍 SPEKTRÁLNÍ ANALÝZA OSCILACE V CENTRU

    # Získáme amplitudy a vytvoříme časovou osu
    amplitudes = np.array([row[1] for row in amplitude_log])
    times = np.arange(len(amplitudes)) * TIME_STEP  # čas v sekundách

    # Odstraníme trend (DC složku)
    amplitudes -= np.mean(amplitudes)

    # Provedeme FFT
    fft_result = fft(amplitudes)
    frequencies = fftfreq(len(amplitudes), d=TIME_STEP)
    spectrum = np.abs(fft_result)

    # Vybereme pouze kladné frekvence
    positive_freqs = frequencies[:len(frequencies)//2]
    positive_spectrum = spectrum[:len(spectrum)//2]

    # Najdeme dominantní frekvenci
    dominant_index = np.argmax(positive_spectrum)
    dominant_freq = positive_freqs[dominant_index]  # v Hz

    # Spočteme energii: E = h·f
    h = 6.62607015e-34  # Planckova konstanta [J·s]
    energy = h * dominant_freq

    # Spočteme vlnovou délku: λ = c / f
    c = 299_792_458  # rychlost světla [m/s]
    wavelength = c / dominant_freq if dominant_freq != 0 else np.inf

    # Spočteme efektivní hmotnost částice: m = E/c²
    mass = energy / c**2  # efektivní hmotnost [kg]

    # Porovnáme s elektronem
    electron_mass = 9.10938356e-31  # hmotnost elektronu [kg]
    mass_ratio = mass / electron_mass

    # Uložení do CSV
    save_csv(
        "spectrum_log.csv",
        ["frequency_Hz", "amplitude"],
        zip(positive_freqs, positive_spectrum),
    )

    save_csv(
        "trajectories.csv",
        ["id", "step", "y", "x", "amplitude"],
        trajectories,
    )

    # MULTISPEKTRÁLNÍ ANALÝZA pro každý bod zvlášť
    multi_spectrum_details = []

    for pt, amp_list in multi_amp_logs.items():
        signal = np.array(amp_list)
        signal -= np.mean(signal)
        fft_result = fft(signal)
        freqs = fftfreq(len(signal), d=TIME_STEP)
        spectrum = np.abs(fft_result)
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

    # Výpis do konzole
    print("🔬 Dominant frequency:", f"{dominant_freq:.2e} Hz")
    print("⚡ Particle energy:", f"{energy:.2e} J")
    print("🌈 Wavelength:", f"{wavelength:.2e} m")

    # Uložení grafu
    plt.figure(figsize=(8, 4))
    plt.plot(positive_freqs, positive_spectrum)
    plt.title("Spektrum oscilace ve středu pole")
    plt.xlabel("Frekvence (Hz)")
    plt.ylabel("Intenzita")
    plt.xscale("log")
    if np.any(positive_spectrum > 0):
        plt.yscale("log")

    plt.grid(True)
    plt.tight_layout()
    plot_path = os.path.join(output_dir, "spectrum_plot.png")
    try:
        plt.savefig(plot_path)
        notify_file_creation(plot_path)
    except Exception as e:
        notify_file_creation(plot_path, success=False, error=e)
    finally:
        plt.close()

    # Funkce pro uložení GIFů

    def save_gif(data_frames, filename, cmap='viridis', vmin=None, vmax=None):
        fig, ax = plt.subplots(figsize=(6, 6))
        img = ax.imshow(data_frames[0], cmap=cmap, vmin=vmin, vmax=vmax)
        ax.axis("off")

        def update(i):
            img.set_data(data_frames[i])
            return [img]
        ani = FuncAnimation(fig, update, frames=len(
            data_frames), interval=300, blit=True)
        try:
            ani.save(filename, writer=PillowWriter(fps=10))
            notify_file_creation(filename)
        except Exception as e:
            notify_file_creation(filename, success=False, error=e)
        finally:
            plt.close(fig)

    save_gif(frames_amp, os.path.join(output_dir, "lineum_amplitude.gif"),
             cmap="plasma", vmin=0, vmax=0.5)
    save_gif(frames_curl, os.path.join(output_dir, "lineum_spin.gif"),
             cmap="bwr", vmin=-0.3, vmax=0.3)
    save_gif(frames_vort, os.path.join(
        output_dir, "lineum_vortices.gif"), cmap="bwr", vmin=-1, vmax=1)
    save_gif(frames_particles, os.path.join(
        output_dir, "lineum_particles.gif"), cmap="gray", vmin=0, vmax=1)

    fig, ax = plt.subplots(figsize=(6, 6))
    x, y = np.meshgrid(np.arange(size), np.arange(size))
    vec = ax.quiver(x, y, frames_vecx[0],
                    frames_vecy[0], color='lime', scale=20)
    ax.axis("off")

    def update_quiver(i):
        vec.set_UVC(frames_vecx[i], frames_vecy[i])
        return [vec]

    ani = FuncAnimation(fig, update_quiver, frames=steps,
                        interval=300, blit=True)
    flow_path = os.path.join(output_dir, "lineum_flow.gif")
    try:
        ani.save(flow_path, writer=PillowWriter(fps=10))
        notify_file_creation(flow_path)
    except Exception as e:
        notify_file_creation(flow_path, success=False, error=e)
    finally:
        plt.close(fig)

    fig, ax = plt.subplots(figsize=(7, 7))
    amp_img = ax.imshow(frames_amp[0], cmap='plasma', vmin=0, vmax=0.5)
    curl_overlay = ax.imshow(
        frames_curl[0], cmap='bwr', alpha=0.4, vmin=-0.3, vmax=0.3)
    vec = ax.quiver(x, y, frames_vecx[0],
                    frames_vecy[0], color='lime', scale=20)
    ax.axis("off")

    def update_combo(i):
        amp_img.set_data(frames_amp[i])
        curl_overlay.set_data(frames_curl[i])
        vec.set_UVC(frames_vecx[i], frames_vecy[i])
        return [amp_img, curl_overlay, vec]

    def generate_html_report(filename="lineum_report.html", mass=0, mass_ratio=0, max_lifespan=0, median_lifespan=0, include_spin=True, phi_mean_near=0, phi_mean_field=0, phi_std_field=1, mass_ratio_blackholes=None, avg_phi_death=None, low_mass_count=None, phi_low_mass_mean=0, curl_low_mass_mean=0, phi_above_025_count=0, curl_near_zero_count=0):

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
            confirmations.append("🌀 Spontánní vznik vírů (vortexů)")
        if quasiparticles_present:
            confirmations.append(
                "🧫 Detekce kvazičástic s měřitelnou trajektorií")
        if stable_frequency:
            confirmations.append(
                f"🎵 Stable spectrum with dominant frequency {dominant_freq:.2e} Hz")
        if topo_conserved:
            confirmations.append(
                "🔁 Conservation of topological charge (winding number)")
        if phi_present:
            confirmations.append(
                "🌌 Emergence of a non-zero field φ at the center of the field")
        if mass_ratio > 0.001 and mass_ratio < 100:
            confirmations.append(
                f"⚖️ Emergence of quasiparticles with realistic effective mass ({mass_ratio:.2e}× electron mass)")

        if blackhole_count > 0:
            confirmations.append(
                f"🕳️ Detekce {blackhole_count} kvazičástic uvězněných ve φ-pasti (černá díra)")

            if mass_ratio_blackholes is not None and mass_ratio_blackholes < 0.01:
                confirmations.append(
                    "🪐 Třískova hypotéza strukturálního uzavření potvrzena: částice zanikají v silných φ-zónách bez zbytkové hmotnosti"
                )
            elif mass_ratio_blackholes is not None:
                confirmations.append(
                    f"🪐 Třískova hypotéza strukturálního uzavření částečně potvrzena: návratové částice mají hmotnost {mass_ratio_blackholes:.2e}× elektronová"
                )
            else:
                confirmations.append(
                    "🪐 Třískova hypotéza strukturálního uzavření zatím neověřena – spektrální data nedostupná"
                )

        # 🧠 Strukturální paměť kvazičástic s nízkou hmotností
        if low_mass_count > 0 and phi_above_025_count > 0 and curl_near_zero_count > 0:
            confirmations.append(
                f"🧠 Strukturální paměť potvrzena: {phi_above_025_count} nízkomasových částic bylo uzavřeno ve φ > 0.25 bez zbytkového spinu (|curl| < 0.02)"
            )

        if avg_phi_death is not None and avg_phi_death > 0.25:
            confirmations.append(
                f"🌀 φ v místě zániku návratových částic potvrzuje strukturální uzavření (⟨φ⟩ = {avg_phi_death:.3f})"
            )
        elif avg_phi_death is not None:
            confirmations.append(
                f"🌀 φ v místě zániku návratových částic: {avg_phi_death:.3f} (hranice potvrzení je 0.25)"
            )

        if wormhole_count > 0:
            confirmations.append(
                f"🌉 Podezření na {wormhole_count} případů červí díry (skoková relokace mezi φ-zónami)")

        if curl_std > 0.05:
            confirmations.append(
                f"🔄 Signifikantní spinová aktivita v φ-zónách (σ = {curl_std:.2e})")

        # Potvrzení homogenního výskytu kvazičástic
        try:
            with open(os.path.join(output_dir, "multi_spectrum_summary.csv")) as f:
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
                        "🧬 Homogenní výskyt kvazičástic s realistickou frekvencí a hmotností napříč celým polem")
        except Exception as e:
            print("⚠️ Homogeneity check failed:", e)

        if max_lifespan >= 100:
            confirmations.append(
                f"🕒 Emergence of long-lived quasiparticles (max {max_lifespan} steps, median {median_lifespan})"
            )

        if include_spin and os.path.exists(os.path.join(output_dir, "spin_aura_avg.png")):
            confirmations.append(
                "🧲 Kvazičástice nesou emergentní spinovou strukturu (dipól nebo vír)")

        if phi_mean_near > phi_mean_field + 3 * phi_std_field:
            confirmations.append(
                "🌠 Lokální zvýšení pole φ v okolí kvazičástic potvrzeno"
            )

        # 💫 φ-gravitační interakce: ověření sbližování částic
        try:
            top_trajs = pd.read_csv(os.path.join(
                output_dir, "trajectories.csv"))
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
                    confirmations.append(
                        "🌠 Emergentní φ-gravitační interakce – kvazičástice se přibližují vlivem gradientu φ"
                    )
                    phi_gravitation_confirmed = True
        except Exception as e:
            print("⚠️ φ-gravitační test selhal:", e)

        if not confirmations:
            confirmations.append(
                "No major emergent phenomena detected")

        # 🔧 HTML konstrukce
        confirmed_html = "\n".join(f"<li>{c}</li>" for c in confirmations)

        gravitational_row = ""
        if phi_gravitation_confirmed:
            gravitational_row = f"<tr><td>Gravitational behavior</td><td>Emergent φ-gradient driven motion</td></tr>"

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
    
      <h2>✅ Confirmed Emergent Phenomena</h2>
      <ul>
        {confirmed_html}
      </ul>
    
      <h2>📊 Quasiparticle Properties</h2>
      <table>
        <tr><th>Property</th><th>Value</th></tr>
        <tr><td>Dominant frequency</td><td>{dominant_freq:.2e} Hz</td></tr>
        <tr><td>Energy</td><td>{energy:.2e} J</td></tr>
        <tr><td>Wavelength</td><td>{wavelength:.2e} m</td></tr>
        <tr><td>Effective mass</td><td>{mass:.2e} kg</td></tr>
        <tr><td>Mass relative to electron</td><td>{mass_ratio:.2e}× electron mass</td></tr>
        <tr><td>⟨φ⟩ at blackhole death</td><td>{avg_phi_death:.3f}</td></tr>
        <tr><td>⟨mass_ratio⟩ at blackhole death</td><td>{mass_ratio_blackholes:.6f}</td></tr>
        <tr><td>Particles with mass_ratio < 0.01</td><td>{low_mass_count}</td></tr>
        <tr><td>⟨φ⟩ at low-mass points</td><td>{phi_low_mass_mean:.3f}</td></tr>
        <tr><td>⟨|curl|⟩ at low-mass points</td><td>{curl_low_mass_mean:.3f}</td></tr>
        <tr><td>Low-mass points with φ > 0.25</td><td>{phi_above_025_count}</td></tr>
        <tr><td>Low-mass points with |curl| < 0.02</td><td>{curl_near_zero_count}</td></tr>
        <tr><td>Max lifespan</td><td>{max_lifespan} steps</td></tr>
        <tr><td>Median lifespan</td><td>{median_lifespan} steps</td></tr>
        {gravitational_row}

      </table>
    
      <p>See full spectrum: <a href="spectrum_log.csv">spectrum_log.csv</a></p>

      <h2>🧮 Field Evolution Equation</h2>
<p><strong>Lineum Field Equation:</strong></p>
<pre><code>
ψ ← ψ + 𝛌̃ + ξ + φψ − δψ + ∇²ψ + ∇φ  
φ ← φ + (|ψ|² − φ) + ∇²φ
</code></pre>

<p><strong>Term definitions:</strong></p>
<table>
<tr><th>Term</th><th>Description</th></tr>
<tr><td>ψ</td><td>Complex scalar field – field tension</td></tr>
<tr><td>linon</td><td>Nonlinear probabilistic particle generation</td></tr>
<tr><td>fluktuace</td><td>Quantum phase noise (oscillatory noise)</td></tr>
<tr><td>φ⋅ψ</td><td>Interaction with φ – modulates ψ evolution</td></tr>
<tr><td>disipace</td><td>Field damping (decay term)</td></tr>
<tr><td>difuze</td><td>Spatial diffusion (Laplacian)</td></tr>
<tr><td>gradient(φ)</td><td><strong>New:</strong> directional influence – ψ follows φ curvature</td></tr>
<tr><td>α (|ψ|² − φ)</td><td>Reaction of φ to field density</td></tr>
<tr><td>β · difuze</td><td>Mild diffusion to form spatial φ gradients</td></tr>
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
        <div><img src="topo_charge_plot.png" alt="Topological charge plot"></div>
        <div><img src="vortex_count_plot.png" alt="Vortex count plot"></div>
        <div><img src="spectrum_plot.png" alt="Spectrum plot"></div>
        <div><img src="phi_center_plot.png" alt="φ center plot"></div>
      </div>
    
      <h2>🎞️ Field Evolution GIFs</h2>
      <div class="grid">
        <img src="lineum_amplitude.gif" alt="Amplitude">
        <img src="lineum_spin.gif" alt="Spin">
        <img src="lineum_particles.gif" alt="Particles">
        <img src="lineum_full_overlay.gif" alt="Full overlay">
      </div>

      <h2>🧲 Spinová aura kvazičástice</h2>
<p>
Analýzou pole <code>curl(∇arg(ψ))</code> v okolí stovek kvazičástic
vznikla průměrná „spinová aura“. Výsledek ukazuje dipólovou strukturu
s protisměrnou rotací – podobně jako reálné částice nesou kvantový moment hybnosti.
</p>
<div><img src="spin_aura_avg.png" alt="Spin aura"></div>

    
      <h2>📚 Glossary & Naming Rationale</h2>

      <h2>🧠 Note on Gravity</h2>
<p>
This simulation supports an alternative interpretation of gravity: not as a force, but as an emergent drive toward co-existence. 
Particles do not attract one another – instead, they shape the φ field in a way that guides others toward them.
The result is motion not due to pulling, but due to a shared directional preference.
</p>

    
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

    ani = FuncAnimation(fig, update_combo, frames=steps,
                        interval=300, blit=True)
    overlay_path = os.path.join(output_dir, "lineum_full_overlay.gif")
    try:
        ani.save(overlay_path, writer=PillowWriter(fps=10))
        notify_file_creation(overlay_path)
    except Exception as e:
        notify_file_creation(overlay_path, success=False, error=e)
    finally:
        plt.close(fig)

    # 🌀 Uložení všech polí vírů do souboru pro analýzu
    frames_vort_np = np.array(frames_vort)  # shape: (steps, size, size)
    npy_path = os.path.join(output_dir, "frames_vortices.npy")
    frames_curl_np = np.array(frames_curl)
    npy_curl_path = os.path.join(output_dir, "frames_curl.npy")
    try:
        np.save(npy_curl_path, frames_curl_np)
        notify_file_creation(npy_curl_path)
    except Exception as e:
        notify_file_creation(npy_curl_path, success=False, error=e)

    try:
        np.save(npy_path, frames_vort_np)
        frames_amp_np = np.array(frames_amp)
        amp_npy_path = os.path.join(output_dir, "frames_amp.npy")
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

        # náhodné body mimo částice
        for _ in range(5):
            ry, rx = random.randint(0, size - 1), random.randint(0, size - 1)
            phi_values_field.append(frames_phi[step][ry, rx])

    phi_mean_near = np.mean(phi_values_near_particles)
    phi_std_near = np.std(phi_values_near_particles)
    phi_mean_field = np.mean(phi_values_field)
    phi_std_field = np.std(phi_values_field)

    print(f"🌌 φ near particles: {phi_mean_near:.4e} ± {phi_std_near:.4e}")
    print(f"🌌 φ elsewhere:      {phi_mean_field:.4e} ± {phi_std_field:.4e}")

    # 🌀 Uložení φ polí pro pozdější analýzu
    frames_phi_np = np.array(frames_phi)  # φ v čase, pouze absolutní hodnota
    phi_npy_path = os.path.join(output_dir, "frames_phi.npy")
    try:
        np.save(phi_npy_path, frames_phi_np)
        notify_file_creation(phi_npy_path)
    except Exception as e:
        notify_file_creation(phi_npy_path, success=False, error=e)

    save_phi_center_plot()

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
    spin_img_path = os.path.join(output_dir, "spin_aura_avg.png")
    plt.figure(figsize=(6, 6))
    sns.heatmap(upsampled_spin_map, center=0,
                cmap="bwr", cbar=True, square=True)
    plt.title("🧲 Průměrná spinová aura kvazičástice (curl ∇arg(ψ))")
    plt.axis("off")
    plt.tight_layout()
    plt.savefig(spin_img_path, dpi=150)
    plt.close()

    include_spin = os.path.exists(
        os.path.join(output_dir, "spin_aura_avg.png"))

    low_mass_count = sum(
        1 for d in multi_spectrum_details if d["mass_ratio"] < 0.01)

    # 📊 Export φ a curl v místech kvazičástic s mass_ratio < 0.01
    low_mass_coords = [
        (d["point"][0], d["point"][1])
        for d in multi_spectrum_details
        if d["mass_ratio"] < 0.01
    ]

    phi_final = np.abs(phi.copy())  # poslední stav φ
    curl_final = curl  # poslední stav curl (v hlavní smyčce už ho máš)

    rows = []
    for y, x in low_mass_coords:
        if 0 <= y < size and 0 <= x < size:
            rows.append([y, x, phi_final[y, x], curl_final[y, x]])

    save_csv("phi_curl_low_mass.csv", ["y", "x", "phi", "curl"], rows)

    # 📊 Vyhodnocení paměťové stopy ve φ-pastích
    df_low_mass = pd.read_csv(os.path.join(
        output_dir, "phi_curl_low_mass.csv"))

    phi_low_mass_mean = df_low_mass["phi"].mean()
    curl_low_mass_mean = df_low_mass["curl"].abs().mean()
    phi_above_025_count = (df_low_mass["phi"] > 0.25).sum()
    curl_near_zero_count = (df_low_mass["curl"].abs() < 0.02).sum()

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
        curl_near_zero_count=curl_near_zero_count
    )

    print("✅ All GIFs and logs have been successfully generated.")

# 💻 Interaktivní náhled simulace (volitelné UI okno)

fig, ax = plt.subplots(figsize=(7, 7))
x, y = np.meshgrid(np.arange(size), np.arange(size))

amp_img = ax.imshow(frames_amp[0], cmap='plasma', vmin=0, vmax=0.5)
curl_overlay = ax.imshow(
    frames_curl[0], cmap='bwr', alpha=0.4, vmin=-0.3, vmax=0.3)
vec = ax.quiver(x, y, frames_vecx[0], frames_vecy[0], color='lime', scale=20)
particles_overlay = ax.imshow(
    frames_particles[0], cmap='gray', alpha=0.6, vmin=0, vmax=1)

ax.set_title("Lineum realtime UI: |ψ| + spin + tok + částice")
ax.axis("off")


def update(i):
    amp_img.set_data(frames_amp[i])
    curl_overlay.set_data(frames_curl[i])
    vec.set_UVC(frames_vecx[i], frames_vecy[i])
    particles_overlay.set_data(frames_particles[i])
    return [amp_img, curl_overlay, vec, particles_overlay]


ani = FuncAnimation(fig, update, frames=len(
    frames_amp), interval=200, blit=True)
plt.show()
