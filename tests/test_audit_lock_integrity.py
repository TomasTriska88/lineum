import os
import json
import pytest
from pathlib import Path
from tools.whitepaper_contract import compute_sha256, verify_locked_run

def test_audit_run_locks_mutability_check(tmp_path, capsys):
    # 1. Create a mock run folder
    run_dir = tmp_path / "mock_locked_run"
    run_dir.mkdir()
    
    # 2. Add some mock output files
    file1 = run_dir / "run_summary.csv"
    file1.write_text("id,val\n1,100", encoding="utf-8")
    
    file2 = run_dir / "kappa_map.png"
    file2.write_bytes(b"\x89PNG\r\n\x1a\n")
    
    # 3. Create a valid _LOCK.json manually to bypass Windows ACL testing Nightmares
    lock_data = {
        "files": {
            "run_summary.csv": {
                "size": file1.stat().st_size,
                "sha256": compute_sha256(str(file1))
            },
            "kappa_map.png": {
                "size": file2.stat().st_size,
                "sha256": compute_sha256(str(file2))
            }
        },
        "file_count": 2
    }
    
    lock_file = run_dir / "_LOCK.json"
    lock_file.write_text(json.dumps(lock_data, indent=2), encoding="utf-8")
    
    # Verify it succeeds initially
    is_valid = verify_locked_run(str(run_dir))
    assert is_valid is True, "Fresh lock failed verification"

    # 4. Mutate a file
    file1.write_text("id,val\n1,999", encoding="utf-8")
    with pytest.raises(SystemExit):
        verify_locked_run(str(run_dir))
    captured = capsys.readouterr()
    assert "SHA256 mismatch" in captured.out or "Size mismatch" in captured.out
    
    # Restore original content
    file1.write_text("id,val\n1,100", encoding="utf-8")
    assert verify_locked_run(str(run_dir)) is True
    
    # 5. Add a file
    (run_dir / "sneaky_file.txt").write_text("sneaky", encoding="utf-8")
    with pytest.raises(SystemExit):
        verify_locked_run(str(run_dir))
    captured = capsys.readouterr()
    assert "File count mismatch" in captured.out or "Extra file" in captured.out
    
    # Remove sneaky file
    (run_dir / "sneaky_file.txt").unlink()
    assert verify_locked_run(str(run_dir)) is True
    
    # 6. Delete a file
    file2.unlink()
    with pytest.raises(SystemExit):
        verify_locked_run(str(run_dir))
    captured = capsys.readouterr()
    assert "File count mismatch" in captured.out or "Missing file" in captured.out
