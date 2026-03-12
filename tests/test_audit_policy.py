import os
import subprocess
import pytest
import json
import uuid
import time
from pathlib import Path

# Paths to the repository root and output_wp relative to this test file
REPO_ROOT = Path(__file__).resolve().parent.parent
LINEUM_SCRIPT = REPO_ROOT / "lineum.py"
OUTPUT_WP_DIR = REPO_ROOT / "output_wp"
STATE_FILE = OUTPUT_WP_DIR / ".audit_job_state.json"


def _run_lineum_with_env(env_updates=None):
    """Helper to run lineum.py as a subprocess with modified environment."""
    env = os.environ.copy()
    if env_updates:
        env.update(env_updates)
    
    # We pass LINEUM_STEPS=1 and LINEUM_STORE_EVERY=1 to make it exit extremely fast if it bypasses the lock
    env["LINEUM_STEPS"] = "1"
    env["LINEUM_STORE_EVERY"] = "1"
    env["LINEUM_DISABLE_TRACKING"] = "true"
    
    result = subprocess.run(
        ["python", str(LINEUM_SCRIPT)],
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
        env=env
    )
    return result


def _write_mock_state(job_id, state="RUNNING", age_seconds=0):
    """Write a mock .audit_job_state.json relative to output_wp"""
    OUTPUT_WP_DIR.mkdir(parents=True, exist_ok=True)
    state_data = {
        "job_id": job_id,
        "state": state,
        "last_heartbeat": time.time() - age_seconds
    }
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state_data, f)


def test_exploratory_run_allowed():
    """Test that a basic run targeting default 'output' is allowed."""
    result = _run_lineum_with_env({
        "LINEUM_BASE_OUTPUT_DIR": "output"
    })
    
    # It should not hit the fatal error
    assert "FATAL ERROR" not in result.stdout
    assert "FATAL ERROR" not in result.stderr
    assert result.returncode == 0 or "Error" not in result.stdout # Assuming it runs fully if no structural error


def test_direct_canonical_launch_blocked():
    """Test that a direct run pointing at output_wp without a token is blocked immediately."""
    result = _run_lineum_with_env({
        "LINEUM_BASE_OUTPUT_DIR": "output_wp"
    })
    
    assert result.returncode == 1
    assert "[FATAL] ERROR: Canonical audit must be launched via Lab Orchestration layer. (Missing token)" in result.stdout


def test_canonical_intent_relative_path_spoofing_blocked():
    """Test that using an obscured relative path like 'output/../output_wp' still triggers the vault lock."""
    result = _run_lineum_with_env({
        "LINEUM_BASE_OUTPUT_DIR": "output/../output_wp"
    })
    
    assert result.returncode == 1
    assert "[FATAL] ERROR: Canonical audit must be launched via Lab Orchestration layer" in result.stdout


def test_invalid_token_rejected():
    """Test that a bad token against a valid backend state is blocked."""
    valid_job_id = str(uuid.uuid4())
    _write_mock_state(valid_job_id, state="RUNNING", age_seconds=10)
    
    result = _run_lineum_with_env({
        "LINEUM_BASE_OUTPUT_DIR": "output_wp",
        "LINEUM_ORCHESTRATION_TOKEN": "bad-token-123"
    })
    
    assert result.returncode == 1
    assert "[FATAL] ERROR: Invalid orchestration token" in result.stdout


def test_cancelled_or_completed_token_rejected():
    """Test that if the orchestrator state is CANCELLED or COMPLETED, the job is blocked."""
    job_id = str(uuid.uuid4())
    _write_mock_state(job_id, state="CANCELLED", age_seconds=10)
    
    result = _run_lineum_with_env({
        "LINEUM_BASE_OUTPUT_DIR": "output_wp",
        "LINEUM_ORCHESTRATION_TOKEN": job_id
    })
    
    assert result.returncode == 1
    assert "[FATAL] ERROR: Cannot launch. Orchestrator state is 'CANCELLED'" in result.stdout


def test_stale_token_rejected():
    """Test that an old heartbeat (>180s) triggers an anti-replay block."""
    job_id = str(uuid.uuid4())
    # 200 seconds old
    _write_mock_state(job_id, state="RUNNING", age_seconds=200)
    
    result = _run_lineum_with_env({
        "LINEUM_BASE_OUTPUT_DIR": "output_wp",
        "LINEUM_ORCHESTRATION_TOKEN": job_id
    })
    
    assert result.returncode == 1
    assert "[FATAL] ERROR: Orchestration token is stale" in result.stdout
    assert "Replay attack" in result.stdout


def test_valid_lab_managed_launch_allowed():
    """Test that a fully valid token and fresh state passes the lock."""
    job_id = str(uuid.uuid4())
    _write_mock_state(job_id, state="RUNNING", age_seconds=10)
    
    result = _run_lineum_with_env({
        "LINEUM_BASE_OUTPUT_DIR": "output_wp",
        "LINEUM_ORCHESTRATION_TOKEN": job_id
    })
    
    assert result.returncode == 0
    assert "[POLICY] Token validated" in result.stdout
    assert job_id in result.stdout


def test_late_stage_file_overwrite_protection():
    """
    Test the secondary fail-before-touch guard manually simulating an arbitrary pointer update.
    We test the nested `_update_latest_run_pointer` function bypassing the main execution pipeline.
    """
    script = f'''import sys
import os
sys.path.append(r"{str(REPO_ROOT)}")
import lineum
lineum._update_latest_run_pointer("output_wp", "fake_run_dir")
'''
    env = os.environ.copy()
    if "LINEUM_ORCHESTRATION_TOKEN" in env:
        del env["LINEUM_ORCHESTRATION_TOKEN"]
        
    result = subprocess.run(
        ["python", "-c", script],
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
        env=env
    )
    
    assert result.returncode == 1
    assert "[FATAL] ERROR: Unauthorized attempt to overwrite canonical latest_run.txt" in result.stdout
