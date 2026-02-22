import os
import json
import pytest
from pathlib import Path
from scripts.verify_whitepaper_lock import verify_locks
from scripts.lock_whitepaper import main as lock_main
import sys
from unittest.mock import patch

def test_whitepaper_freeze_integrity(tmp_path, capsys):
    # 1. Create a mock whitepaper folder
    wp_dir = tmp_path / "whitepapers"
    wp_dir.mkdir()
    
    # Original draft file
    mock_wp = wp_dir / "lineum-mock.md"
    mock_wp.write_text("**Version:** 1.0.18-core\n# Title\n> **Document Status:** Draft\n\nContent details.", encoding="utf-8")
    
    # Verify no locks pass
    assert verify_locks(str(wp_dir)) is True
    
    # 2. Freeze the whitepaper
    with patch.object(sys, 'argv', ['lock_whitepaper.py', str(mock_wp)]):
        lock_main()
        
    # Check that original remains draft
    assert "Draft" in mock_wp.read_text(encoding="utf-8")
    
    # Check that snapshot was created in releases/
    releases_dir = wp_dir / "releases"
    assert releases_dir.exists()
    
    snapshot = releases_dir / "lineum-mock-1.0.18-core-FROZEN.md"
    assert snapshot.exists()
    assert "Frozen" in snapshot.read_text(encoding="utf-8")
    
    # Check that lock file exists
    lock_file = releases_dir / "lineum-mock-1.0.18-core-FROZEN.md._LOCK.json"
    assert lock_file.exists()
    
    # Verify lock passes
    assert verify_locks(str(wp_dir)) is True
    
    # 3. Modify the frozen snapshot (Tampering)
    snapshot.write_text("**Version:** 1.0.18-core\n# Title\n> **Document Status:** Frozen\n\nTampered Content details.", encoding="utf-8")
    assert verify_locks(str(wp_dir)) is False
    
    captured = capsys.readouterr()
    assert "FAIL" in captured.out
    assert "tampered" in captured.out

    # Restore content by deleting snapshot and re-freezing
    snapshot.unlink()
    lock_file.unlink()
    with patch.object(sys, 'argv', ['lock_whitepaper.py', str(mock_wp)]):
        lock_main()
    assert verify_locks(str(wp_dir)) is True
    
    # 4. Snapshot missing
    snapshot.unlink()
    assert verify_locks(str(wp_dir)) is False
    captured = capsys.readouterr()
    assert "missing" in captured.out
