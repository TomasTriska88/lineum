import pytest
import os
import sys
from unittest.mock import patch, MagicMock
# Import lineum to access _find_latest_checkpoint
# Adjust path if necessary or use conftest structure
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import lineum

def test_resume_alias_support(tmp_path, capsys):
    """Verify that LINEUM_RESUME_CHECKPOINT works as an alias."""
    ckpt_path = tmp_path / "alias_ckpt.npz"
    ckpt_path.touch()
    
    with patch.dict(os.environ, {"LINEUM_RESUME_CHECKPOINT": str(ckpt_path)}, clear=True):
        found = lineum._find_latest_checkpoint()
        assert found == str(ckpt_path)
    
    captured = capsys.readouterr()
    assert "WARNING: deprecated alias LINEUM_RESUME_CHECKPOINT" in captured.out

def test_priority_conflict(tmp_path, capsys):
    """Verify LINEUM_CHECKPOINT takes precedence over alias with warning."""
    primary = tmp_path / "primary.npz"
    primary.touch()
    secondary = tmp_path / "secondary.npz"
    secondary.touch()
    
    with patch.dict(os.environ, {
        "LINEUM_CHECKPOINT": str(primary),
        "LINEUM_RESUME_CHECKPOINT": str(secondary)
    }, clear=True):
        found = lineum._find_latest_checkpoint()
        assert found == str(primary)
        
    captured = capsys.readouterr()
    assert "CONFLICT: Both" in captured.out
    assert "Using LINEUM_CHECKPOINT" in captured.out

def test_fail_fast_primary(capsys):
    """Verify SystemExit(1) if LINEUM_CHECKPOINT is set but missing."""
    with patch.dict(os.environ, {"LINEUM_CHECKPOINT": "/non/existent/path.npz"}, clear=True):
        with pytest.raises(SystemExit) as excinfo:
            lineum._find_latest_checkpoint()
        assert excinfo.value.code == 1
        
    captured = capsys.readouterr()
    assert "CRITICAL ERROR: Explicit checkpoint not found" in captured.out
    assert "Aborting to prevent split-brain" in captured.out

def test_fail_fast_alias(capsys):
    """Verify SystemExit(1) if alias is set but missing."""
    with patch.dict(os.environ, {"LINEUM_RESUME_CHECKPOINT": "/non/existent/alias.npz"}, clear=True):
        with pytest.raises(SystemExit) as excinfo:
            lineum._find_latest_checkpoint()
        assert excinfo.value.code == 1

def test_explicit_arg_priority(tmp_path):
    """Verify explicit argument beats environment variables."""
    arg_ckpt = tmp_path / "arg.npz"
    arg_ckpt.touch()
    env_ckpt = tmp_path / "env.npz"
    env_ckpt.touch()
    
    with patch.dict(os.environ, {"LINEUM_CHECKPOINT": str(env_ckpt)}, clear=True):
        found = lineum._find_latest_checkpoint(explicit_path=str(arg_ckpt))
        assert found == str(arg_ckpt)
