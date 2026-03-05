import sys
import os

# Important: ensure we run from the correct directory so 'config' can be imported
sys.path.insert(0, r"c:\Users\Tomáš\Documents\GitHub\lineum-core")

from config import config
import lineum

config.W = 128
config.H = 128
config.T = 100
config.LOG_EVERY = 2
config.RUN_TAG = "variant_2d"
config.SEED = 42

out_dir = r"C:\Users\Tomáš\.gemini\antigravity\tmp\lineum_variant_out"
os.makedirs(out_dir, exist_ok=True)
config.BASE_STATS_DIR = out_dir

print("Starting Lineum 2D Engine Run (100 steps)...")
lineum.run_simulation()
print(f"Finished Lineum run. Check {out_dir} for animated GIFs.")
