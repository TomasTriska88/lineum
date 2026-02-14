
import traceback
import sys
import os

# Set env for 1-step run
os.environ["LINEUM_STEPS"] = "1"
os.environ["LINEUM_SAVE_STATE"] = "1"
os.environ["LINEUM_CHECKPOINT_EVERY"] = "1"
os.environ["LINEUM_RUN_MODE"] = "false"

try:
    # Run lineum.py as a module or via exec
    with open("lineum.py", "rb") as f:
        code = compile(f.read(), "lineum.py", 'exec')
        exec(code, {"__name__": "__main__"})
except Exception:
    traceback.print_exc()
