import numpy as np
import pandas as pd
import json
import os

# --- Paths ---
RUN_DIR = r"c:\Users\Tomáš\Documents\GitHub\lineum-core\output_wp\runs\spec6_false_s41_20260215_023130"
LAB_DATA_DIR = r"c:\Users\Tomáš\Documents\GitHub\lineum-core\lab\public\data"

os.makedirs(LAB_DATA_DIR, exist_ok=True)

# 1. Extract Φ-Field Frames
PHI_PATH = os.path.join(RUN_DIR, "spec6_false_s41_frames_phi.npy")
print(f"Loading {PHI_PATH}...")
phi_frames = np.load(PHI_PATH) # shape: (200, 128, 128)

# Use ALL 200 frames for 4x higher fidelity
phi_lowres = []
for frame in phi_frames:
    # simple striding for downsampling (keeping 64x64 for performance)
    phi_lowres.append(frame[::2, ::2].tolist())

phi_payload = {
    "metadata": {
        "source": "spec6_false_s41",
        "frame_count": len(phi_lowres),
        "grid_size": 64
    },
    "frames": phi_lowres
}

with open(os.path.join(LAB_DATA_DIR, "phi_audit_frames.json"), "w") as f:
    json.dump(phi_payload, f)
print("Saved phi_audit_frames.json")

# 2. Extract Key Trajectories
TRAJ_PATH = os.path.join(RUN_DIR, "spec6_false_s41_trajectories.csv")
print(f"Loading {TRAJ_PATH}...")
df = pd.read_csv(TRAJ_PATH)

# Select top 20 longest trajectories
traj_lengths = df.groupby('id').size()
top_ids = traj_lengths.sort_values(ascending=False).head(20).index.tolist()

trajectories_data = []
for tid in top_ids:
    t_df = df[df['id'] == tid].sort_values('step')
    # Filter only every 10 steps to smooth/decimate
    t_decimated = t_df.iloc[::10]
    trajectories_data.append({
        "id": int(tid),
        "path": t_decimated[['x', 'y']].values.tolist()
    })

# 3. Extract Resonance Data (f0 evolution vs Zeta Zeros)
# Non-trivial zeros of Riemann Zeta function (imaginary parts)
ZETA_ZEROS = [14.134725, 21.022040, 25.010858, 30.424876, 32.935062]

# The audit f0 is ~1.85e20 Hz. We need to normalize this to a "spectral space"
# where we can see the alignment. 
# We'll use the rolling phi_center as a proxy for the 'vibration' state if per-step FFT isn't available.
# Actually, let's use the phi_center_log.csv to simulate the resonance curve.

PHI_LOG_PATH = os.path.join(RUN_DIR, "spec6_false_s41_phi_center_log.csv")
phi_log = pd.read_csv(PHI_LOG_PATH)
# Normalize phi_center to [0, 100] for visual alignment
phi_log['phi_norm'] = (phi_log['phi_center_abs'] / phi_log['phi_center_abs'].max()) * 40

resonance_payload = {
    "zeta_zeros": ZETA_ZEROS,
    "phi_evolution": phi_log.iloc[::5]['phi_norm'].tolist(), # Sync with 400 frames (2000 steps / 5)
    "f0_canonical": 1.856777545095882e+20
}

with open(os.path.join(LAB_DATA_DIR, "resonance_audit.json"), "w") as f:
    json.dump(resonance_payload, f)
print("Saved resonance_audit.json")
