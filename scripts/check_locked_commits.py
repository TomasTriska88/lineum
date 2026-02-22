#!/usr/bin/env python3
import sys
import subprocess
import os

def check_staged_locked_runs():
    try:
        # Get list of staged files
        staged_files = subprocess.check_output(['git', 'diff', '--cached', '--name-only'], text=True).splitlines()
    except Exception:
        return 0
        
    for f in staged_files:
        if f.startswith('output_wp/runs/'):
            # Find the run id directory
            parts = f.replace('\\', '/').split('/')
            if len(parts) >= 3:
                run_dir = os.path.join(parts[0], parts[1], parts[2])
                lock_file = os.path.join(run_dir, "_LOCK.json")
                if os.path.exists(lock_file):
                    print(f"ERROR: Cannot commit changes to a locked audit run. Tampered file: {f}")
                    print("Create a new run; never modify locked evidence.")
                    sys.exit(1)
    
    return 0

if __name__ == "__main__":
    sys.exit(check_staged_locked_runs())
