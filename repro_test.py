import subprocess
import sys
import os

project_root = os.getcwd()
env = os.environ.copy()
env["LINEUM_BASE_OUTPUT_DIR"] = ".scratch/repro_out"
env["LINEUM_RUN_TAG"] = "repro_run"
env["LINEUM_STEPS"] = "1"
env["LINEUM_SAVE_STATE"] = "1"
env["LINEUM_CHECKPOINT_EVERY"] = "1"
env["LINEUM_RUN_MODE"] = "false"
env["PYTHONUTF8"] = "1"

print(f"Running lineum.py from {project_root}")
print(f"Executable: {sys.executable}")

result = subprocess.run(
    [sys.executable, "lineum.py"],
    cwd=project_root,
    env=env,
    capture_output=True,
    text=True,
    encoding="utf-8",
    errors="replace",
)

print("-" * 20)
print(f"Return Code: {result.returncode}")
print("STDOUT:")
print(result.stdout)
print("-" * 20)
print("STDERR:")
print(result.stderr)
print("-" * 20)
