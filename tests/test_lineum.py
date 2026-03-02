"""
Unit tests for lineum.py functions (in-process, no subprocess).

These tests import lineum directly and exercise individual helper functions
with tmp_path isolation. Each test should run in <1s.
"""
import glob
import os

import numpy as np
import pytest

import lineum


# ---------------------------------------------------------------------------
# 1) _atomic_write_bytes
# ---------------------------------------------------------------------------

def test_atomic_write_bytes_is_atomic(tmp_path):
    """_atomic_write_bytes writes exact content and leaves no .tmp leftovers."""
    target = str(tmp_path / "a.txt")
    lineum._atomic_write_bytes(target, b"hello")

    # Content is exact
    assert open(target, "rb").read() == b"hello"

    # No leftover .tmp files
    tmps = glob.glob(str(tmp_path / "*.tmp"))
    assert tmps == [], f"Leftover .tmp files: {tmps}"


# ---------------------------------------------------------------------------
# 2) _update_latest_run_pointer
# ---------------------------------------------------------------------------

def test_update_latest_run_pointer_writes_relative_path(tmp_path):
    """_update_latest_run_pointer creates latest_run.txt with the exact relative path."""
    base_dir = str(tmp_path)
    lineum._update_latest_run_pointer(base_dir, "runs/x_y")

    ptr = tmp_path / "latest_run.txt"
    assert ptr.exists(), "latest_run.txt was not created"
    assert ptr.read_text(encoding="utf-8") == "runs/x_y"


# ---------------------------------------------------------------------------
# 3) _find_latest_checkpoint priority ordering
# ---------------------------------------------------------------------------

def test_find_latest_checkpoint_priority_ordering(tmp_path, monkeypatch):
    """Priority: explicit (1) > latest_run (2) > legacy (3)."""
    base = str(tmp_path / "output")
    os.makedirs(base, exist_ok=True)

    # Ensure LINEUM_CHECKPOINT env is not set (would override prio)
    monkeypatch.delenv("LINEUM_CHECKPOINT", raising=False)

    # Create 3 checkpoints
    legacy_dir = os.path.join(base, "checkpoints")
    os.makedirs(legacy_dir, exist_ok=True)
    legacy_ckpt = os.path.join(legacy_dir, "legacy.npz")
    np.savez(legacy_ckpt, step_index=0)

    run_dir = os.path.join(base, "runs", "abc", "checkpoints")
    os.makedirs(run_dir, exist_ok=True)
    run_ckpt = os.path.join(run_dir, "run_ckpt.npz")
    np.savez(run_ckpt, step_index=0)

    explicit_ckpt = str(tmp_path / "explicit.npz")
    np.savez(explicit_ckpt, step_index=0)

    # Point latest_run.txt to runs/abc
    with open(os.path.join(base, "latest_run.txt"), "w") as f:
        f.write("runs/abc")

    # Prio 1: explicit wins
    found = lineum._find_latest_checkpoint(explicit_path=explicit_ckpt, base_output_dir=base)
    assert os.path.abspath(found) == os.path.abspath(explicit_ckpt)

    # Prio 2: latest_run wins when no explicit
    found = lineum._find_latest_checkpoint(base_output_dir=base)
    assert os.path.abspath(found) == os.path.abspath(run_ckpt)

    # Prio 3: legacy fallback when pointer removed
    os.remove(os.path.join(base, "latest_run.txt"))
    found = lineum._find_latest_checkpoint(base_output_dir=base)
    assert os.path.abspath(found) == os.path.abspath(legacy_ckpt)


# ---------------------------------------------------------------------------
# 4) save_state_checkpoint subdir enforcement
# ---------------------------------------------------------------------------

def test_save_state_checkpoint_forces_checkpoints_subdir(tmp_path):
    """save_state_checkpoint places the .npz inside run_dir/checkpoints/."""
    run_dir = str(tmp_path / "my_run")
    os.makedirs(run_dir, exist_ok=True)

    N = 10
    psi = np.zeros((N, N))
    phi = np.zeros((N, N))
    kappa = np.full((N, N), 0.5)
    delta = np.zeros((N, N))
    active_tracks = {0: (5.0, 5.0), 1: (3.0, 7.0)}
    next_id = 2

    rel = lineum.save_state_checkpoint(
        run_dir=run_dir,
        run_prefix="test",
        step_idx=42,
        psi=psi,
        phi=phi,
        kappa=kappa,
        delta=delta,
        active_tracks=active_tracks,
        next_id=next_id,
    )

    assert rel is not None, "save_state_checkpoint returned None (failure)"

    # Relative path starts with checkpoints/
    assert rel.startswith("checkpoints/"), f"Expected checkpoints/ prefix, got: {rel}"

    # File exists inside run_dir/checkpoints/
    full_path = os.path.join(run_dir, rel)
    assert os.path.isfile(full_path), f"Checkpoint file not found at {full_path}"

    # No .npz in run_dir root (only in checkpoints/)
    root_npz = glob.glob(os.path.join(run_dir, "*.npz"))
    assert root_npz == [], f"Unexpected NPZ in run_dir root: {root_npz}"

    # No leftover .tmp files
    tmp_files = glob.glob(os.path.join(run_dir, "checkpoints", "*.tmp*"))
    assert tmp_files == [], f"Leftover tmp files: {tmp_files}"

    # Verify _meta is injected
    with np.load(full_path) as data:
        assert "_meta" in data, "Failed to embed _meta in save_state_checkpoint"
        import json
        meta_data = json.loads(data["_meta"].item())
        assert meta_data["step"] == 42


# ---------------------------------------------------------------------------
# 5) save_checkpoint includes _meta
# ---------------------------------------------------------------------------

def test_save_checkpoint_includes_meta(tmp_path, monkeypatch):
    """save_checkpoint correctly embeds _meta property for verification."""
    run_dir = str(tmp_path / "my_run")
    os.makedirs(run_dir, exist_ok=True)
    monkeypatch.setattr(lineum, "RUN_TAG", "test_meta")
    monkeypatch.setattr(lineum, "output_dir", run_dir)
    
    def mock_checkpoint_paths(step_idx):
        npz = os.path.join(run_dir, f"test_meta_{step_idx}.npz")
        json_path = os.path.join(run_dir, f"test_meta_{step_idx}.json")
        return npz, json_path

    monkeypatch.setattr(lineum, "_checkpoint_paths", mock_checkpoint_paths)

    N = 10
    psi = np.zeros((N, N))
    phi = np.zeros((N, N))
    kappa = np.full((N, N), 0.5)
    delta = np.zeros((N, N))
    
    lineum.save_checkpoint(
        step_idx=200,
        psi=psi,
        phi=phi,
        delta=delta,
        kappa=kappa,
        next_id=2,
        active_tracks={},
        trajectories=[],
        logs={}
    )
    
    npz_file = os.path.join(run_dir, "test_meta_200.npz")
    assert os.path.exists(npz_file)
    
    with np.load(npz_file) as data:
        assert "_meta" in data
        import json
        meta_data = json.loads(data["_meta"].item())
        assert meta_data["step"] == 200
        assert "origin" in meta_data
