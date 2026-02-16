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
    # Fallback to hardcoded if ptr missing
    RUN_DIR = os.path.join(OUTPUT_WP, "runs", "spec6_false_s41_20260215_023130")

RUN_TAG = os.path.basename(RUN_DIR).split('_2026')[0] # Extract specX_mode_sY
print(f"Targeting Run: {RUN_TAG} at {RUN_DIR}")

os.makedirs(LAB_DATA_DIR, exist_ok=True)

# 1. Extract Φ-Field Frames
PHI_PATH = os.path.join(RUN_DIR, f"{RUN_TAG}_frames_phi.npy")
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
    
    for i in range(400):
        target_step = i * 5
        
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

with open(os.path.join(LAB_DATA_DIR, "trajectories_audit.json"), "w") as f:
    json.dump(trajectories_data, f)
print("Saved trajectories_audit.json")

# ⚖️ Calculate Global Birth Frame (when most linons have appeared)
# For simplicity: use the median of birth steps among the top 20
birth_steps = [t_df['step'].min() for tid in top_ids for t_df in [df[df['id'] == tid]]]
median_birth_step = int(np.median(birth_steps))
birth_frame = median_birth_step // 5

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
print(f"Saved metadata.json: {metadata_payload}")

# 4. Extract Resonance Data (f0 evolution vs Zeta Zeros)
# Non-trivial zeros of Riemann Zeta function (imaginary parts)
ZETA_ZEROS = [14.134725, 21.022040, 25.010858, 30.424876, 32.935062]

PHI_LOG_PATH = os.path.join(RUN_DIR, f"{RUN_TAG}_phi_center_log.csv")
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

# 5. Harmonic Analysis (Fibonacci & Golden Spiral)
# Check for geometric ideals in the simulation data
print("Performing harmonic analysis...")

# Fibonacci Ratios (from peak intervals in average distance)
df['dist'] = np.sqrt((df['x'] - 64)**2 + (df['y'] - 64)**2)
avg_dist = df.groupby('step')['dist'].mean()

# Find peaks in average distance
peaks = []
for i in range(1, len(avg_dist)-1):
    if avg_dist.iloc[i] > avg_dist.iloc[i-1] and avg_dist.iloc[i] > avg_dist.iloc[i+1]:
        peaks.append(avg_dist.index[i])
        
fib_ratios = []
if len(peaks) > 2:
    intervals = np.diff(peaks)
    for i in range(1, len(intervals)):
        ratio = intervals[i] / intervals[i-1]
        fib_ratios.append(float(ratio))

# Golden Spiral Scoring (top trajectories)
phi = (1 + 5**0.5) / 2
golden_b = np.log(phi) / (np.pi / 2)
spiral_scores = []
for tid in top_ids[:3]:
    t_df = df[df['id'] == tid].sort_values('step')
    x, y = t_df['x'] - 64, t_df['y'] - 64
    r = np.sqrt(x**2 + y**2)
    theta = np.unwrap(np.arctan2(y, x))
    
    if len(r) > 15:
        coeffs = np.polyfit(theta, np.log(r + 1e-6), 1)
        b = coeffs[0]
        score = 1 - abs(b - golden_b) / golden_b
        spiral_scores.append(max(0, float(score)))

harmonic_payload = {
    "fibonacci_ratios": fib_ratios,
    "golden_spiral_scores": spiral_scores,
    "golden_ratio": phi,
    "harmonic_index": float(np.mean(spiral_scores)) if spiral_scores else 0.5
}

with open(os.path.join(LAB_DATA_DIR, "harmonics_audit.json"), "w") as f:
    json.dump(harmonic_payload, f)
print(f"Saved harmonics_audit.json: {harmonic_payload}")
