import os
import json
import pytest
from pathlib import Path
from scripts.verify_whitepaper_lock import verify_locks
from scripts.lock_whitepaper import main as lock_main
import sys
from unittest.mock import patch

def test_whitepaper_lock_integrity(tmp_path, capsys):
    # 1. Create a mock whitepaper folder
    wp_dir = tmp_path / "whitepapers"
    wp_dir.mkdir()
    
    mock_wp = wp_dir / "lineum-mock.md"
    mock_wp.write_text("# Title\n> **Document Status:** Draft\n\nContent details.", encoding="utf-8")
    
    # Verify no locks pass
    assert verify_locks(str(wp_dir)) is True
    
    # 2. Lock the whitepaper
    with patch.object(sys, 'argv', ['lock_whitepaper.py', str(mock_wp)]):
        lock_main()
        
    # Check that status was updated to Frozen
    assert "Frozen" in mock_wp.read_text(encoding="utf-8")
    
    # Check that lock file exists
    lock_file = wp_dir / "lineum-mock.md.lock.json"
    assert lock_file.exists()
    
    # Verify lock passes
    assert verify_locks(str(wp_dir)) is True
    
    # 3. Modify the whitepaper (Tampering)
    mock_wp.write_text("# Title\n> **Document Status:** Frozen\n\nTampered Content details.", encoding="utf-8")
    assert verify_locks(str(wp_dir)) is False
    
    captured = capsys.readouterr()
    assert "FAIL" in captured.out
    assert "tampered" in captured.out

    # Restore content
    # Relock directly to get a clean baseline again
    with patch.object(sys, 'argv', ['lock_whitepaper.py', str(mock_wp)]):
        lock_main()
    assert verify_locks(str(wp_dir)) is True
    
    # 4. Whitepaper missing
    mock_wp.unlink()
    assert verify_locks(str(wp_dir)) is False
    captured = capsys.readouterr()
    assert "missing" in captured.out

