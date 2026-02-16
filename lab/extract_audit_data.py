import numpy as np
import pandas as pd
import json
import os
import shutil

# --- Paths ---
OUTPUT_WP = r"c:\Users\Tomáš\Documents\GitHub\lineum-core\output_wp"
RUNS_BASE = os.path.join(OUTPUT_WP, "runs")
LAB_DATA_DIR = r"c:\Users\Tomáš\Documents\GitHub\lineum-core\lab\public\data"
RUNS_DATA_DIR = os.path.join(LAB_DATA_DIR, "runs")

os.makedirs(RUNS_DATA_DIR, exist_ok=True)

def process_run(run_dir):
    run_id = os.path.basename(run_dir)
    # Extract tag (part before timestamp)
    run_tag = run_id.split('_2026')[0] 
    
    target_dir = os.path.join(RUNS_DATA_DIR, run_id)
    os.makedirs(target_dir, exist_ok=True)
    
    print(f"\n>>> Processing Run: {run_id}")

    # 1. Extract Φ-Field Frames
    phi_path = os.path.join(run_dir, f"{run_tag}_frames_phi.npy")
    if not os.path.exists(phi_path):
        print(f"    [SKIP] Missing Φ-field at {phi_path}")
        return None

    phi_frames = np.load(phi_path)
    frame_count = len(phi_frames)
    step_per_frame = 2000 // frame_count

    phi_lowres = [frame[::2, ::2].tolist() for frame in phi_frames]
    phi_payload = {
        "metadata": {"source": run_id, "frame_count": frame_count, "grid_size": 64},
        "frames": phi_lowres
    }
    with open(os.path.join(target_dir, "phi_frames.json"), "w") as f:
        json.dump(phi_payload, f)

    # 2. Extract Trajectories
    traj_path = os.path.join(run_dir, f"{run_tag}_trajectories.csv")
    df = pd.read_csv(traj_path)
    traj_info = df.groupby('id')['step'].agg(['min', 'max'])
    traj_info['duration'] = traj_info['max'] - traj_info['min']
    top_ids = traj_info.sort_values('duration', ascending=False).head(20).index.tolist()

    trajectories_data = []
    for tid in top_ids:
        t_df = df[df['id'] == tid].sort_values('step')
        path = []
        min_s, max_s = t_df['step'].min(), t_df['step'].max()
        for i in range(frame_count):
            target_step = i * step_per_frame
            if target_step < min_s or target_step > max_s:
                path.append(None)
            else:
                row = t_df[t_df['step'] <= target_step].tail(1)
                path.append(row[['x', 'y', 'amplitude', 'step']].values.tolist()[0] if not row.empty else None)
        trajectories_data.append({"id": int(tid), "path": path})

    with open(os.path.join(target_dir, "trajectories.json"), "w") as f:
        json.dump(trajectories_data, f)

    # 3. Metadata
    median_birth_step = int(np.median([t_df['step'].min() for tid in top_ids for t_df in [df[df['id'] == tid]]]))
    meta = {
        "run_id": run_id,
        "run_tag": run_tag,
        "timestamp": run_id.split('_')[-2] + "_" + run_id.split('_')[-1],
        "birth_frame": median_birth_step // step_per_frame,
        "frame_count": frame_count
    }
    with open(os.path.join(target_dir, "metadata.json"), "w") as f:
        json.dump(meta, f)

    # 4. Resonance & Harmonics
    phi_center_path = os.path.join(run_dir, f"{run_tag}_phi_center_log.csv")
    phi_log = pd.read_csv(phi_center_path)
    phi_norm = (phi_log['phi_center_abs'] / phi_log['phi_center_abs'].max() * 40).tolist()[::step_per_frame]
    
    zeta_zeros = [14.134725, 21.022040, 25.010858, 30.424876, 32.935062]
    with open(os.path.join(target_dir, "resonance.json"), "w") as f:
        json.dump({"zeta_zeros": zeta_zeros, "phi_evolution": phi_norm}, f)

    # Simplified harmonics (reusing logic)
    phi_const = (1 + 5**0.5) / 2
    golden_b = np.log(phi_const) / (np.pi / 2)
    frame_harmonics = []
    frame_correlation = []
    for i in range(frame_count):
        active = [p for traj in trajectories_data if (p := traj['path'][i])]
        h_score = 0.5
        if len(active) >= 3:
            rs = [np.sqrt((l[0]-64)**2 + (l[1]-64)**2) for l in active]
            thetas = [np.arctan2(l[1]-64, l[0]-64) for l in active]
            try:
                b = np.polyfit(np.unwrap(thetas), np.log(np.array(rs) + 1e-6), 1)[0]
                h_score = 1 - min(1, abs(b - golden_b) / golden_b)
            except: pass
        frame_harmonics.append(float(h_score))
        c_score = max(0, 1.0 - (min([abs(phi_norm[i] - z) for z in zeta_zeros]) / 5.0))
        frame_correlation.append(float(c_score))

    with open(os.path.join(target_dir, "harmonics.json"), "w") as f:
        json.dump({"frame_harmonics": frame_harmonics, "frame_correlation": frame_correlation}, f)

    # 5. Tidal Stretching
    all_vars, all_dists = [], []
    for i in range(frame_count):
        active_pos = [ [p[0], p[1]] for traj in trajectories_data if (p := traj['path'][i])]
        if len(active_pos) >= 2:
            pts = np.array(active_pos)
            all_vars.append(float(np.var(pts[:, 0]) + np.var(pts[:, 1])))
            all_dists.append(float(np.sqrt(np.sum((np.mean(pts, axis=0) - [64, 64])**2))))
        else:
            all_vars.append(0.0); all_dists.append(128.0)
    
    with open(os.path.join(target_dir, "stretching_data.json"), "w") as f:
        json.dump({"times": [i*step_per_frame for i in range(frame_count)], "variances": all_vars, "distances": all_dists}, f)

    return meta

# Main Execution
runs = [os.path.join(RUNS_BASE, d) for d in os.listdir(RUNS_BASE) if os.path.isdir(os.path.join(RUNS_BASE, d)) and not d.startswith('_')]
manifest = []

for r in runs:
    meta = process_run(r)
    if meta:
        manifest.append(meta)

with open(os.path.join(LAB_DATA_DIR, "manifest.json"), "w") as f:
    json.dump(manifest, f, indent=4)

print(f"\n--- Multi-Run Pipeline Complete: {len(manifest)} runs synced ---")
