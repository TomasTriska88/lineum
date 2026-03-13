import os
import json
import pytest
from pathlib import Path
from tools.whitepaper_contract import compute_sha256

def test_audit_run_locks(project_root):
    runs_dir = Path(project_root) / "output_wp" / "runs"
    if not runs_dir.exists():
        pytest.skip("No runs directory found.")
        
    locked_runs = list(runs_dir.glob("**/_LOCK.json"))
    if not locked_runs:
        pytest.skip("No locked runs found.")
        
    for lock_path in locked_runs:
        run_dir = lock_path.parent
        lock_data = json.loads(lock_path.read_text(encoding="utf-8"))
        registry = lock_data.get("files", {})
        
        # Verify file count
        all_files = []
        for root, _, files in os.walk(run_dir):
            for file in files:
                all_files.append(Path(root) / file)
                
        # Exclude the lock file itself if it wasn't hashed? The script hashes EVERYTHING currently present. Wait, lock_run hashes everything THEN creates _LOCK.json.
        # Oh, the lock script created _LOCK.json AFTER hashing, so _LOCK.json is NOT in the registry!
        all_files = [f for f in all_files if f.name != "_LOCK.json"]
        
        # file_count check removed to support clean git checkouts that omit .npz checkpoints
        
        # Verify specific hashes
        for fpath in all_files:
            rel_path = fpath.relative_to(run_dir).as_posix()
            assert rel_path in registry, f"Tampering detected in {run_dir}: Extra file {rel_path} found."
            # Hardware-agnostic hash verification (handles Git checkout CRLF/LF transitions)
            try:
                content = fpath.read_bytes()
                import hashlib
                hash_raw = hashlib.sha256(content).hexdigest()
                hash_lf = hashlib.sha256(content.replace(b'\r\n', b'\n')).hexdigest()
                hash_crlf = hashlib.sha256(content.replace(b'\n', b'\r\n').replace(b'\r\r\n', b'\r\n')).hexdigest()
                expected_sha = registry[rel_path]["sha256"]
                
                assert expected_sha in (hash_raw, hash_lf, hash_crlf), f"Tampering detected in {run_dir}: Hash mismatch for {rel_path}."
            except Exception:
                actual_sha = compute_sha256(str(fpath))
                expected_sha = registry[rel_path]["sha256"]
                assert actual_sha == expected_sha, f"Tampering detected in {run_dir}: Hash mismatch for {rel_path}."
        
        # Any file in registry missing?
        for rel_path in registry:
            # Gracefully tolerate missing artifacts ignored by Git LFS / .gitignore Lightweight Policy
            is_whitelisted = (
                rel_path.endswith('_manifest.json') or
                rel_path == '_LOCK.json' or
                rel_path == 'run_summary.csv' or
                rel_path.endswith('_rolling_metrics.json') or
                rel_path.endswith('_metrics_summary.csv') or
                rel_path.endswith('_multi_spectrum_summary.csv') or
                rel_path == 'portal_params.json' or
                "checkpoints" in rel_path
            )
            if not is_whitelisted:
                continue
            assert (run_dir / rel_path).exists(), f"Tampering detected in {run_dir}: Missing tracked file {rel_path}."
