"""
Shared pytest fixtures for lineum-core tests.
"""
import os
import sys
import subprocess

import pytest


@pytest.fixture
def project_root():
    """Absolute path to the repository root (parent of tests/)."""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@pytest.fixture
def base_output_dir(tmp_path):
    """Temporary output directory for integration tests."""
    out = tmp_path / "test_output"
    out.mkdir()
    return str(out)


@pytest.fixture
def base_env(base_output_dir):
    """Base environment dict for running lineum.py as subprocess."""
    env = os.environ.copy()
    env["LINEUM_BASE_OUTPUT_DIR"] = base_output_dir
    env["LINEUM_RUN_TAG"] = "test_run"
    env["LINEUM_STEPS"] = "1"
    env["LINEUM_SAVE_STATE"] = "1"
    env["LINEUM_CHECKPOINT_EVERY"] = "1"
    env["LINEUM_RUN_MODE"] = "false"
    env["PYTHONUTF8"] = "1"
    return env


@pytest.fixture
def run_lineum(project_root, base_env):
    """
    Factory fixture: call run_lineum(env_overrides=None) to execute lineum.py
    as a subprocess and get the CompletedProcess result.
    Asserts returncode == 0; on failure prints stdout + stderr.
    """
    def _run(env_overrides=None):
        env = base_env.copy()
        if env_overrides:
            env.update(env_overrides)
        result = subprocess.run(
            [sys.executable, "lineum.py"],
            cwd=project_root,
            env=env,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        if result.returncode != 0:
            print(f"STDOUT:\n{result.stdout}")
            print(f"STDERR:\n{result.stderr}")
        assert result.returncode == 0, (
            f"lineum.py failed (exit {result.returncode})\n"
            f"--- STDOUT (last 30 lines) ---\n"
            + "\n".join(result.stdout.splitlines()[-30:])
            + f"\n--- STDERR (last 20 lines) ---\n"
            + "\n".join(result.stderr.splitlines()[-20:])
        )
        return result
    return _run
