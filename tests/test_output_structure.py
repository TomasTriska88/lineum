"""
Integration tests for the output directory structure and resume-in-place logic.

These tests run lineum.py as a subprocess to verify:
- Timestamped run directories are created under output/runs/
- latest_run.txt pointer is maintained
- Two consecutive runs create separate directories
- Resuming reuses the existing run directory (resume-in-place)
"""
import os
import time
import glob
import subprocess
import sys

import numpy as np
import pytest


# ---------------------------------------------------------------------------
# Helpers (used only in this module)
# ---------------------------------------------------------------------------

def _create_dummy_checkpoint(path, step=10):
    """Create a minimal valid .npz checkpoint at *path*."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    np.savez(
        path,
        psi=np.zeros((10, 10)),
        phi=np.zeros((10, 10)),
        kappa=np.zeros((10, 10)),
        step_index=step,
        next_id=100,
        track_ids=np.array([1]),
        track_pos_xy=np.array([[0, 0]]),
        rng_algo="MT19937",
        rng_keys=np.zeros(1),
        rng_pos=0,
        rng_has_gauss=0,
        rng_cached_gauss=0.0,
    )


# ---------------------------------------------------------------------------
# Integration tests
# ---------------------------------------------------------------------------

@pytest.mark.integration
def test_run_dir_creation(run_lineum, base_output_dir):
    """A fresh run creates a timestamped subdirectory under runs/."""
    run_lineum({"LINEUM_RUN_TAG": "runA"})

    runs_dir = os.path.join(base_output_dir, "runs")
    assert os.path.isdir(runs_dir), "runs/ directory not created"

    subdirs = glob.glob(os.path.join(runs_dir, "runA_*"))
    assert len(subdirs) == 1, f"Expected 1 run dir, found {len(subdirs)}: {subdirs}"

    # latest_run.txt should exist and point to that directory
    latest = os.path.join(base_output_dir, "latest_run.txt")
    assert os.path.isfile(latest), "latest_run.txt not created"

    content = open(latest, "r", encoding="utf-8").read().strip()
    expected_rel = os.path.relpath(subdirs[0], base_output_dir)
    # Normalize separators for Windows
    assert content.replace("/", os.sep) == expected_rel.replace("/", os.sep)


@pytest.mark.integration
def test_latest_run_pointer(run_lineum, base_output_dir):
    """latest_run.txt points to an existing directory and contains the run tag."""
    run_lineum({"LINEUM_RUN_TAG": "runB"})

    ptr = os.path.join(base_output_dir, "latest_run.txt")
    assert os.path.isfile(ptr), "latest_run.txt missing"

    rel_path = open(ptr, "r", encoding="utf-8").read().strip()
    full_path = os.path.join(base_output_dir, rel_path)
    assert os.path.isdir(full_path), "latest_run.txt points to non-existent dir"
    assert "runB_" in rel_path, "Pointer does not contain run tag"


@pytest.mark.integration
def test_two_runs_separate_dirs(run_lineum, base_output_dir):
    """Two consecutive runs with the same tag create separate directories."""
    run_lineum({"LINEUM_RUN_TAG": "run_seq"})
    time.sleep(1.2)  # Ensure timestamp second changes
    run_lineum({"LINEUM_RUN_TAG": "run_seq", "LINEUM_RESUME": "0"})

    runs_dir = os.path.join(base_output_dir, "runs")
    subdirs = glob.glob(os.path.join(runs_dir, "run_seq_*"))
    assert len(subdirs) == 2, f"Expected 2 run dirs, found {len(subdirs)}"


@pytest.mark.integration
def test_resume_in_place(run_lineum, base_output_dir, project_root, base_env):
    """Resuming reuses the existing run directory (no new dir created)."""
    # 1. Initial run
    run_lineum({"LINEUM_RUN_TAG": "run_orig", "LINEUM_STEPS": "1"})

    runs_dir = os.path.join(base_output_dir, "runs")
    run_dirs = [
        d for d in os.listdir(runs_dir)
        if os.path.isdir(os.path.join(runs_dir, d))
    ]
    assert len(run_dirs) == 1, "Should have exactly 1 run dir initially"
    original_name = run_dirs[0]
    original_dir = os.path.join(runs_dir, original_name)

    # Verify checkpoint exists
    ckpt_dir = os.path.join(original_dir, "checkpoints")
    assert os.path.isdir(ckpt_dir)
    ckpts = glob.glob(os.path.join(ckpt_dir, "*.npz"))
    assert len(ckpts) > 0, "Initial run should create a checkpoint"

    # 2. Resume — different tag should be ignored
    env = base_env.copy()
    env["LINEUM_RESUME"] = "1"
    env["LINEUM_RUN_TAG"] = "run_new_tag_ignored"
    env["LINEUM_STEPS"] = "1"

    result = subprocess.run(
        [sys.executable, "lineum.py"],
        cwd=project_root,
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )

    # May exit non-zero for unrelated post-processing; check key behaviour
    assert "RESUME-IN-PLACE" in result.stdout, (
        f"RESUME-IN-PLACE not found in stdout.\n"
        f"stdout (last 10): {result.stdout.splitlines()[-10:]}"
    )
    assert original_name in result.stdout

    # 3. Still only 1 run directory
    run_dirs_after = [
        d for d in os.listdir(runs_dir)
        if os.path.isdir(os.path.join(runs_dir, d))
    ]
    assert len(run_dirs_after) == 1, "Should still have exactly 1 run dir (reused)"
    assert run_dirs_after[0] == original_name


@pytest.mark.integration
def test_find_latest_checkpoint_logic(base_output_dir):
    """Unit test for _find_latest_checkpoint priority: explicit > latest_run > legacy."""
    import importlib
    import lineum
    importlib.reload(lineum)

    # Create checkpoints in different locations
    run1_ckpt = os.path.join(base_output_dir, "runs", "run1", "checkpoints", "ckpt_1.npz")
    run2_ckpt = os.path.join(base_output_dir, "runs", "run2", "checkpoints", "ckpt_2.npz")
    legacy_ckpt = os.path.join(base_output_dir, "checkpoints", "legacy.npz")

    _create_dummy_checkpoint(run1_ckpt, step=10)
    _create_dummy_checkpoint(legacy_ckpt, step=20)
    _create_dummy_checkpoint(run2_ckpt, step=30)

    # Priority 1: Explicit path
    found = lineum._find_latest_checkpoint(explicit_path=run1_ckpt, base_output_dir=base_output_dir)
    assert os.path.abspath(found) == os.path.abspath(run1_ckpt)

    # Priority 2: Latest run via pointer
    with open(os.path.join(base_output_dir, "latest_run.txt"), "w") as f:
        f.write(os.path.relpath(
            os.path.join(base_output_dir, "runs", "run2"),
            base_output_dir
        ))
    found = lineum._find_latest_checkpoint(base_output_dir=base_output_dir)
    assert os.path.abspath(found) == os.path.abspath(run2_ckpt)

    # Priority 3: Legacy fallback
    os.remove(os.path.join(base_output_dir, "latest_run.txt"))
    found = lineum._find_latest_checkpoint(base_output_dir=base_output_dir)
    assert os.path.abspath(found) == os.path.abspath(legacy_ckpt)
