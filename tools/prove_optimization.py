
import os
import sys
import subprocess
import numpy as np
import hashlib
import shutil

# Paths
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LINEUM_SCRIPT = os.path.join(ROOT_DIR, "lineum.py")
OUTPUT_DIR = os.path.join(ROOT_DIR, "output", "proof_invariant")

# Configuration
STEPS = 200
SEED = 42

def run_simulation(name, disable_tracking):
    print(f"--- Running {name} (DISABLE_TRACKING={disable_tracking}) ---")
    run_dir = os.path.join(OUTPUT_DIR, name)
    if os.path.exists(run_dir):
        shutil.rmtree(run_dir)
    os.makedirs(run_dir, exist_ok=True)
    
    env = os.environ.copy()
    env["LINEUM_STEPS"] = str(STEPS)
    env["LINEUM_STORE_EVERY"] = "100"
    env["LINEUM_DISABLE_TRACKING"] = "true" if disable_tracking else "false"
    env["LINEUM_SAVE_STATE"] = "1"
    
    env["LINEUM_RUN_ID"] = "6"
    env["LINEUM_RUN_MODE"] = "false"
    env["LINEUM_SEED"] = str(SEED)
    env["PYTHONIOENCODING"] = "utf-8"
    env["LINEUM_LOW_NOISE_MODE"] = "1" # Match audit configuration
    env["LINEUM_RESUME"] = "false"  # Force fresh run

    
    cmd = [sys.executable, LINEUM_SCRIPT]
    try:
        res = subprocess.run(cmd, env=env, cwd=ROOT_DIR, capture_output=True, text=True, encoding="utf-8")
    except UnicodeError:
         # Fallback for some windows envs
         res = subprocess.run(cmd, env=env, cwd=ROOT_DIR, capture_output=True) 
         # Decode manually
         res.stdout = res.stdout.decode("utf-8", errors="replace") if res.stdout else ""
         res.stderr = res.stderr.decode("utf-8", errors="replace") if res.stderr else ""
    
    if res.returncode != 0:
        print(f"FAILED {name}: {res.stderr}")
        return None
    
    # Find output directory (it will be name_timestamp)
    # But wait, lineum allows us to set output dir? No, it appends timestamp.
    # Let's find the directory that starts with 'name' in OUTPUT_DIR
    candidates = [d for d in os.listdir(OUTPUT_DIR) if d.startswith(name) and os.path.isdir(os.path.join(OUTPUT_DIR, d))]
    candidates.sort() # latest last
    if not candidates:
        print(f"No output directory found for {name}")
        return None
        
    final_dir = os.path.join(OUTPUT_DIR, candidates[-1])
    # Find the checkpoint
    # It should be in checkpoints/name_state_step{STEPS-1}.npz or similar
    # Actually lineum saves "latest_state_checkpoint" in manifest or we can search.
    # Based on code: checkpoints/{tag}_state_step{i}.npz
    
    ckpt_dir = os.path.join(final_dir, "checkpoints")
    ckpts = [f for f in os.listdir(ckpt_dir) if f.endswith(".npz")]
    if not ckpts:
        print(f"No checkpoints in {ckpt_dir}")
        return None
    
    # Sort to find last
    ckpts.sort()
    return os.path.join(ckpt_dir, ckpts[-1])

def hash_array(name, arr):
    # Ensure C-contiguous and consistent type
    arr_c = np.ascontiguousarray(arr)
    data = arr_c.tobytes()
    h = hashlib.sha256(data).hexdigest()
    return h.upper()

def compare_states(ckpt_a, ckpt_b):
    print("\n--- Comparing States ---")
    print(f"A (Tracked):   {ckpt_a}")
    print(f"B (Untracked): {ckpt_b}")
    
    data_a = np.load(ckpt_a, allow_pickle=False)
    data_b = np.load(ckpt_b, allow_pickle=False)
    
    # Fields to check
    fields = ["psi", "phi", "kappa"]
    
    param_match = True
    
    print(f"{'Field':<10} | {'Hash A (Tracked)':<64} | {'Hash B (Untracked)':<64} | {'Match'}")
    print("-" * 150)
    
    for f in fields:
        arr_a = data_a[f]
        arr_b = data_b[f]
        
        h_a = hash_array(f, arr_a)
        h_b = hash_array(f, arr_b)
        
        match = (h_a == h_b)
        if not match:
            param_match = False
            
        print(f"{f:<10} | {h_a} | {h_b} | {'✅' if match else '❌'}")
        
    return param_match

def main():
    # 1. Run Tracked (Baseline)
    ckpt_a = run_simulation("run_tracked_baseline", disable_tracking=False)
    if not ckpt_a: return
    
    # 2. Run Untracked (Optimized)
    ckpt_b = run_simulation("run_untracked_opt", disable_tracking=True)
    if not ckpt_b: return
    
    # 3. Compare
    match = compare_states(ckpt_a, ckpt_b)
    
    if match:
        print("\n✅ PROOF SUCCESSFUL: Core state is invariant under DISABLE_TRACKING.")
    else:
        print("\n❌ PROOF FAILED: States diverged!")
        sys.exit(1)

if __name__ == "__main__":
    main()
