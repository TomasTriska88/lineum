import sys
import os
import subprocess
import csv
import pytest
from pathlib import Path

# NOTE: 'project_root' fixture comes from conftest.py

def run_and_parse(project_root, env_overrides, tmp_path, expect_success=True):
    """
    Runs lineum.py in a subprocess with given env_overrides.
    - Sets output dir to tmp_path.
    - Forces short run (20 steps).
    - Checks return code.
    - Parses run_summary.csv if successful.
    """
    # Setup Env
    env = os.environ.copy()

    # Force base output dir to tmp_path so we can find results easily
    env["LINEUM_BASE_OUTPUT_DIR"] = str(tmp_path)

    # Speed optimizations & Cleanup
    env["LINEUM_STEPS"] = "20"
    env["LINEUM_SAVE_STATE"] = "0"
    env["LINEUM_SAVE_GIFS"] = "0"
    env["LINEUM_SAVE_POV"] = "0"
    env["LINEUM_RUN_TAG"] = "test_knobs"  # consistent naming, though timestamp varies
    env["PYTHONUTF8"] = "1"  # Force UTF-8 for unicode paths (Tomáš)

    # Ensure no interfering knobs from system env
    keys_to_check = [
        "LINEUM_NOISE_STRENGTH",
        "LINEUM_DRIFT_STRENGTH",
        "LINEUM_DISABLE_DRIFT"
    ]
    # Remove them if they exist in the copy (so we test defaults cleanly)
    for k in keys_to_check:
        if k in env:
            del env[k]

    # Apply overrides
    if env_overrides:
        env.update(env_overrides)

    # Run
    cmd = [sys.executable, "lineum.py"]

    # We must use cwd=project_root so imports work
    result = subprocess.run(
        cmd,
        cwd=project_root,
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8"
    )

    # Check Return Code
    if expect_success:
        if result.returncode != 0:
            print(f"--- STDOUT ---\n{result.stdout}")
            print(f"--- STDERR ---\n{result.stderr}")
        assert result.returncode == 0, f"Sim failed with rc={result.returncode}"
    else:
        assert result.returncode == 1, f"Sim should fail (rc=1) but got rc={result.returncode}"
        return {}  # No outputs to parse on failure

    # Find run_summary.csv
    # It should be in tmp_path/runs/<RunDir>/run_summary.csv
    found_csvs = list(tmp_path.rglob("run_summary.csv"))
    assert len(found_csvs) == 1, f"Expected exactly 1 summary csv, found {len(found_csvs)}: {found_csvs}"

    csv_path = found_csvs[0]

    # Parse CSV into dict (metric -> value)
    data = {}
    with open(csv_path, "r", encoding="utf-8") as f:
        # lineum.py writes header "metric,value"
        # DictReader uses that header as keys
        reader = csv.DictReader(f)
        for row in reader:
            # row is {'metric': 'noise_strength', 'value': '0.005'}
            if row.get('metric') and row.get('value') is not None:
                data[row['metric']] = row['value']

    return data


def test_baseline_defaults(project_root, tmp_path):
    """(a, d) Baseline defaults check."""
    data = run_and_parse(project_root, {}, tmp_path)
    assert float(data["noise_strength"]) == 0.005
    assert float(data["drift_strength"]) == -0.004


def test_noise_override_zero(project_root, tmp_path):
    """(b) Noise override check."""
    data = run_and_parse(project_root, {"LINEUM_NOISE_STRENGTH": "0.0"}, tmp_path)
    assert float(data["noise_strength"]) == 0.0


def test_drift_disable(project_root, tmp_path):
    """(b) Drift disable check."""
    data = run_and_parse(project_root, {"LINEUM_DISABLE_DRIFT": "true"}, tmp_path)
    assert float(data["drift_strength"]) == 0.0


def test_drift_override(project_root, tmp_path):
    """(b) Drift override check."""
    data = run_and_parse(project_root, {"LINEUM_DRIFT_STRENGTH": "-0.01"}, tmp_path)
    assert float(data["drift_strength"]) == -0.01


def test_invalid_noise_exits_1(project_root, tmp_path):
    """(c) Invalid noise float -> exit 1."""
    run_and_parse(project_root, {"LINEUM_NOISE_STRENGTH": "nope"}, tmp_path, expect_success=False)


def test_invalid_drift_exits_1(project_root, tmp_path):
    """(c) Invalid drift float -> exit 1."""
    run_and_parse(project_root, {"LINEUM_DRIFT_STRENGTH": "nope"}, tmp_path, expect_success=False)
