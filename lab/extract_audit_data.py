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
    phi_abs = phi_log['phi_center_abs'].values
    phi_norm = (phi_abs / phi_abs.max() * 40).tolist()[::step_per_frame]
    
    zeta_zeros = [14.134725, 21.022040, 25.010858, 30.424876, 32.935062, 37.586178, 40.918719, 43.327073, 48.005151, 49.773832, 52.970321, 56.446248, 59.347044, 60.831779, 62.839]
    with open(os.path.join(target_dir, "resonance.json"), "w") as f:
        json.dump({"zeta_zeros": zeta_zeros[:5], "phi_evolution": phi_norm}, f)

    # --- 6. ADVANCED ANALYSIS (Riemann & Fourier) ---
    # a) Fourier Spectrum Analysis (Image 1)
    # Perform FFT on the full phi_center_abs signal
    fft_vals = np.abs(np.fft.rfft(phi_abs))
    fft_norm = (fft_vals / fft_vals.max() * 10).tolist()[:50] # Normalize and take first 50 components
    
    # b) Riemann Correlation (Image 2/3)
    # Identify "DejaVu Points" (Significant events: Top intensity indices)
    # This ensures points are distributed over time and have variance for correlation
    top_indices = np.argsort(phi_abs)[-50:]
    dejavu_raw = sorted(top_indices.tolist())
    dejavu_points = dejavu_raw
    
    def normalize_list(l):
        if not l: return []
        if len(l) < 2: return [1.0]
        mi, mx = min(l), max(l)
        if mx == mi: return [1.0] * len(l)
        return [(x - mi) / (mx - mi) for x in l]

    zeta_zeros_full = [14.134725, 21.022040, 25.010858, 30.424876, 32.935062, 37.586178, 40.918719, 43.327073, 48.005151, 49.773832, 52.970321, 56.446248, 59.347044, 60.831779, 62.839, 65.112, 67.079, 69.115, 72.067, 75.704, 77.144, 79.337, 82.910, 84.735, 87.425, 88.809, 92.491, 94.651, 95.883, 98.831, 101.317, 103.725, 105.446, 107.168, 111.029, 111.874, 114.320, 116.226, 118.790, 121.370, 122.946, 124.256, 127.516, 129.578, 131.087, 133.497, 134.756, 138.116, 139.736, 141.123]
    
    norm_dejavu = normalize_list(dejavu_points)
    norm_riemann = normalize_list(zeta_zeros_full[:len(norm_dejavu)])
    
    # Metrics
    pearson_r = 0.0
    euclidean_dist = 0.0
    if len(norm_dejavu) > 1:
        pearson_r = float(np.corrcoef(norm_dejavu, norm_riemann)[0, 1])
        euclidean_dist = float(np.linalg.norm(np.array(norm_dejavu) - np.array(norm_riemann)))

    discovery_data = {
        "fourier_spectrum": [float(x) for x in fft_norm],
        "dejavu_points": [int(x) for x in dejavu_points],
        "norm_dejavu": [float(x) for x in norm_dejavu],
        "norm_riemann": [float(x) for x in norm_riemann],
        "pearson_r": float(pearson_r),
        "euclidean_dist": float(euclidean_dist),
        "zeta_zeros_ref": [float(x) for x in zeta_zeros_full[:len(norm_dejavu)]]
    }
    
    with open(os.path.join(target_dir, "discovery.json"), "w") as f:
        json.dump(discovery_data, f)

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
        c_score = max(0, 1.0 - (min([abs(phi_norm[i] - z) for z in zeta_zeros[:5]]) / 5.0))
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

    # Update meta with discovery stats
    meta["pearson_r"] = pearson_r
    meta["euclidean_dist"] = euclidean_dist
    
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
