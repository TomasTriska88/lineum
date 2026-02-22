import os
import sys
import shutil
import pytest
import subprocess
from pathlib import Path
from tools.whitepaper_contract import verify_locked_run

def test_audit_run_locks_mutability_check(tmp_path, capsys):
    # 1. Use the tiny synthetic fixture from tests/data/
    root = Path(__file__).parent.parent
    fixture_dir = root / "tests" / "data" / "mock_run"
    run_dir = tmp_path / "mock_locked_run"
    
    # Ensure it's deterministic and fast by copying to a volatile temp folder
    shutil.copytree(fixture_dir, run_dir)
    
    # 2. Lock the run via the actual tool
    lock_script = root / "scripts" / "lock_audit_run.py"
    # To bypass Windows ACL issues breaking the Python file edits later, we just generate the _LOCK.json
    # The ACL itself is a system-level defense, Python edits might fail if we don't handle it
    # We will mock the subprocess Windows call, but for verification the _LOCK.json is the real target
    # Since we want to test Python's detection, we'll patch the locking script to NOT call icacls 
    # just for the purpose of the mutability unit test, or we'll bypass subprocess
    
    # Actually, the user says test modifying a file. If icacls denies it, we can't even mutate it in the test!
    # Because we're writing the test, we can force the mutation by changing OS permissions or mocking icacls.
    # To keep it simple, we invoke Python directly, but modify the test to manually generate the _LOCK.json using the exact format.
    # WAIT! The lock_audit_run script might successfully ACL it, preventing our test from breaking the file.
    # If the user's requirement is testing the whitepaper_contract's tamper detection, we bypass the OS-level lock by removing read-only flags or recreating files. 
    res = subprocess.run([sys.executable, str(lock_script), str(run_dir), "--no-os-lock"], capture_output=True, text=True)
    assert res.returncode == 0, f"Locking failed: {res.stderr}"
    
    # Disable read-only so tests can actually mutate the file to verify the hash-check mechanism
    if sys.platform == "win32":
        subprocess.run(f'attrib -R "{run_dir}\\*" /S /D', shell=True)
        # We can't easily undo icacls deny on the current user unless we run icacls /remove
        username = os.environ.get("USERNAME")
        if username:
            subprocess.run(f'icacls "{run_dir}" /remove:d "{username}"', shell=True)
            
    # Check that _LOCK.json exists and contains "locked": true
    lock_file = run_dir / "_LOCK.json"
    assert lock_file.exists()
    assert '"locked": true' in lock_file.read_text(encoding="utf-8").lower()
    
    # Verify it succeeds initially
    is_valid = verify_locked_run(str(run_dir))
    assert is_valid is True, "Fresh lock failed verification"

    # 3. Mutate a file
    file1 = run_dir / "run_summary.csv"
    orig_content = file1.read_text(encoding="utf-8")
    
    file1.write_text("id,val\n1,999", encoding="utf-8")
    with pytest.raises(SystemExit):
        verify_locked_run(str(run_dir))
    captured = capsys.readouterr()
    assert "SHA256 mismatch" in captured.out or "Size mismatch" in captured.out
    
    # Restore original content
    file1.write_text(orig_content, encoding="utf-8")
    assert verify_locked_run(str(run_dir)) is True
    
    # 4. Add a file
    (run_dir / "sneaky_file.txt").write_text("sneaky", encoding="utf-8")
    with pytest.raises(SystemExit):
        verify_locked_run(str(run_dir))
    captured = capsys.readouterr()
    assert "File count mismatch" in captured.out or "Extra file" in captured.out
    
    # Remove sneaky file
    (run_dir / "sneaky_file.txt").unlink()
    assert verify_locked_run(str(run_dir)) is True
    
    # 5. Delete a file
    file2 = run_dir / "kappa_map.png"
    file2.unlink()
    with pytest.raises(SystemExit):
        verify_locked_run(str(run_dir))
    captured = capsys.readouterr()
    assert "File count mismatch" in captured.out or "Missing file" in captured.out
