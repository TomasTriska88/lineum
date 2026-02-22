import os
import json
import pytest
import subprocess
from pathlib import Path
from tools.whitepaper_contract import compute_sha256

def test_contract_tool_strictly_readonly_on_locked_runs(project_root):
    """
    Snapshot hashes of locked runs, run tools/whitepaper_contract.py, then re-check hashes unchanged.
    """
    runs_dir = Path(project_root) / "output_wp" / "runs"
    locked_runs = list(runs_dir.glob("**/_LOCK.json"))
    
    if not locked_runs:
        pytest.skip("No locked runs found to test immutability.")
        
    # 1. Snapshot
    snapshots = {}
    for lock_path in locked_runs:
        run_dir = lock_path.parent
        lock_data = json.loads(lock_path.read_text(encoding="utf-8"))
        registry = lock_data.get("files", {})
        
        for rel_path, info in registry.items():
            fpath = run_dir / rel_path
            snapshots[fpath] = info["sha256"]
            
    # 2. Run the tool (in strict mode or regular)
    # We just run it to let it scan and generate the suite.
    try:
        subprocess.check_call(
            ["python", "tools/whitepaper_contract.py"], 
            cwd=project_root
        )
    except subprocess.CalledProcessError as e:
        # Tool might fail if there's a validation error, but it still shouldn't mutate the run.
        pass
        
    # 3. Verify unchanged
    for fpath, original_sha in snapshots.items():
        assert fpath.exists(), f"File {fpath} was deleted by tooling!"
        current_sha = compute_sha256(str(fpath))
        assert current_sha == original_sha, f"File {fpath} was mutated by tooling!"
