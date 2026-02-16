import numpy as np
import pandas as pd
import json
import os

# --- Paths ---
OUTPUT_WP = r"c:\Users\Tomáš\Documents\GitHub\lineum-core\output_wp"
LAB_DATA_DIR = r"c:\Users\Tomáš\Documents\GitHub\lineum-core\lab\public\data"

# Dynamic Run Discovery
LATEST_RUN_PTR = os.path.join(OUTPUT_WP, "latest_run.txt")
if os.path.exists(LATEST_RUN_PTR):
    with open(LATEST_RUN_PTR, "r") as f:
        rel_run = f.read().strip()
    RUN_DIR = os.path.join(OUTPUT_WP, rel_run)
else:
    raise FileNotFoundError(f"Could not find latest_run.txt in {OUTPUT_WP}")

RUN_TAG = os.path.basename(RUN_DIR).split('_2026')[0] # Extract specX_mode_sY
print(f"Targeting Run: {RUN_TAG} at {RUN_DIR}")

os.makedirs(LAB_DATA_DIR, exist_ok=True)

# 1. Extract Φ-Field Frames
PHI_PATH = os.path.join(RUN_DIR, f"{RUN_TAG}_frames_phi.npy")
print(f"Loading {PHI_PATH}...")
phi_frames = np.load(PHI_PATH) # shape: (200, 128, 128)
FRAME_COUNT = len(phi_frames)
STEP_PER_FRAME = 2000 // FRAME_COUNT

phi_lowres = []
for frame in phi_frames:
    # simple striding for downsampling (keeping 64x64 for performance)
    phi_lowres.append(frame[::2, ::2].tolist())

phi_payload = {
    "metadata": {
        "source": RUN_TAG,
        "frame_count": FRAME_COUNT,
        "grid_size": 64
    },
    "frames": phi_lowres
}

with open(os.path.join(LAB_DATA_DIR, "phi_frames.json"), "w") as f:
    json.dump(phi_payload, f)
print(f"Saved phi_frames.json ({FRAME_COUNT} frames)")

# 2. Extract Key Trajectories
TRAJ_PATH = os.path.join(RUN_DIR, f"{RUN_TAG}_trajectories.csv")
print(f"Loading {TRAJ_PATH}...")
df = pd.read_csv(TRAJ_PATH)

# Select top 20 trajectories by duration
traj_info = df.groupby('id')['step'].agg(['min', 'max', 'count'])
traj_info['duration'] = traj_info['max'] - traj_info['min']
top_ids = traj_info.sort_values('duration', ascending=False).head(20).index.tolist()

trajectories_data = []
for tid in top_ids:
    t_df = df[df['id'] == tid].sort_values('step')
    
    # We need to map 2000 steps to 400 frames
    # Each frame represents steps [i*5, (i+1)*5)
    path = []
    min_s = t_df['step'].min()
    max_s = t_df['step'].max()
    
    for i in range(FRAME_COUNT):
        target_step = i * STEP_PER_FRAME
        
        # 👁️ Birth/Death Gate: only include point if step is within simulation lifespan
        if target_step < min_s or target_step > max_s:
            path.append(None)
            continue
            
        # Find the closest step in this trajectory
        step_row = t_df[t_df['step'] <= target_step].tail(1)
        if step_row.empty:
            path.append(None)
        else:
            # Format: [x, y, amplitude, step]
            row_data = step_row[['x', 'y', 'amplitude', 'step']].values.tolist()[0]
            path.append(row_data)
        
    trajectories_data.append({
        "id": int(tid),
        "path": path
    })

with open(os.path.join(LAB_DATA_DIR, "trajectories.json"), "w") as f:
    json.dump(trajectories_data, f)
print("Saved trajectories.json")

# ⚖️ Calculate Global Birth Frame (when most linons have appeared)
# For simplicity: use the median of birth steps among the top 20
birth_steps = [t_df['step'].min() for tid in top_ids for t_df in [df[df['id'] == tid]]]
median_birth_step = int(np.median(birth_steps))
birth_frame = median_birth_step // STEP_PER_FRAME

# 3. Save Metadata
metadata_payload = {
    "run_tag": RUN_TAG,
    "timestamp": os.path.basename(RUN_DIR).split('_')[-2] + "_" + os.path.basename(RUN_DIR).split('_')[-1],
    "birth_frame": birth_frame,
    "birth_step": median_birth_step,
    "phi_source": os.path.basename(PHI_PATH)
}
with open(os.path.join(LAB_DATA_DIR, "metadata.json"), "w") as f:
    json.dump(metadata_payload, f)
print(f"Saved metadata.json")

# 4. Extract Resonance Data (f0 evolution vs Zeta Zeros)
# Non-trivial zeros of Riemann Zeta function (imaginary parts)
ZETA_ZEROS = [14.134725, 21.022040, 25.010858, 30.424876, 32.935062]

PHI_LOG_PATH = os.path.join(RUN_DIR, f"{RUN_TAG}_phi_center_log.csv")
phi_log = pd.read_csv(PHI_LOG_PATH)
# Normalize phi_center to [0, 100] for visual alignment
phi_log['phi_norm'] = (phi_log['phi_center_abs'] / phi_log['phi_center_abs'].max()) * 40

phi_evolution = phi_log.iloc[::STEP_PER_FRAME]['phi_norm'].tolist() # Sync with 400 frames (2000 steps / 5)

resonance_payload = {
    "zeta_zeros": ZETA_ZEROS,
    "phi_evolution": phi_evolution,
    "f0_canonical": 1.856777545095882e+20
}

with open(os.path.join(LAB_DATA_DIR, "resonance.json"), "w") as f:
    json.dump(resonance_payload, f)
print("Saved resonance.json")

# 5. Harmonic Analysis (Dynamic Per-Frame)
print("Performing per-frame harmonic analysis...")

phi_const = (1 + 5**0.5) / 2
golden_b = np.log(phi_const) / (np.pi / 2)

frame_harmonics = []
frame_correlation = []

for i in range(FRAME_COUNT):
    # a) Harmony: Spiral fit for active linons
    active_linons = []
    for traj in trajectories_data:
        p = traj['path'][i]
        if p is not None:
            active_linons.append(p)
    
    h_score = 0.5 # Default
    if len(active_linons) >= 3:
        # Calculate deviation from spiral
        rs = []
        thetas = []
        for l in active_linons:
            dx, dy = l[0] - 64, l[1] - 64
            r = np.sqrt(dx**2 + dy**2)
            theta = np.arctan2(dy, dx)
            rs.append(r)
            thetas.append(theta)
        
        # Sort by theta to check growth
        # Simple heuristic: how well does r correlate with exp(b*theta)
        try:
            thetas_unwrapped = np.unwrap(thetas)
            coeffs = np.polyfit(thetas_unwrapped, np.log(np.array(rs) + 1e-6), 1)
            b = coeffs[0]
            h_score = 1 - min(1, abs(b - golden_b) / golden_b)
        except:
            h_score = 0.5
    
    frame_harmonics.append(float(h_score))

    # b) Correlation: Alignment with Zeta Zeros
    current_f = phi_evolution[i]
    dists = [abs(current_f - z) for z in ZETA_ZEROS]
    min_dist = min(dists)
    # Correlation is 100% if dist is 0, drops off. Max dist range is roughly 40.
    c_score = max(0, 1.0 - (min_dist / 5.0)) # 5.0 is the "proximity" threshold
    frame_correlation.append(float(c_score))

harmonic_payload = {
    "frame_harmonics": frame_harmonics,
    "frame_correlation": frame_correlation,
    "golden_ratio": phi_const
}

with open(os.path.join(LAB_DATA_DIR, "harmonics.json"), "w") as f:
    json.dump(harmonic_payload, f)
print(f"Saved harmonics.json with {len(frame_harmonics)} dynamic steps.")
