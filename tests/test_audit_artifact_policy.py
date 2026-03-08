import subprocess
import os
import sys

def run_cmd(args):
    result = subprocess.run(args, capture_output=True, text=True)
    return result.stdout.strip().split('\n') if result.stdout else []

def test_no_heavy_artifacts_tracked():
    # List all tracked files inside output_wp/runs/
    files = run_cmd(['git', 'ls-files', 'output_wp/runs/'])
    
    heavy_extensions = ['.npy', '.npz', '.png', '.gif', '.html']
    heavy_logs = ['_log.csv', 'trajectories.csv', '_low_mass.csv', '_grid_dejavu.csv', '_grid_summary.csv']
    
    violations = []
    
    for f in files:
        if any(f.endswith(ext) for ext in heavy_extensions):
            violations.append(f)
        if any(log in f for log in heavy_logs):
            violations.append(f)
        if '/checkpoints/' in f:
            violations.append(f)
            
    if violations:
        print(f"FAIL: Heavy artifacts are still tracked in git: {violations}")
        sys.exit(1)
    
    print("PASS: No heavy artifacts are tracked in output_wp/runs/")
    
if __name__ == '__main__':
    test_no_heavy_artifacts_tracked()
