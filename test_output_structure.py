
import os
import sys
import shutil
import tempfile
import unittest
import numpy as np
import time
import subprocess
import glob

# Ensure we can import lineum for unit tests
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class TestOutputStructure(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.base_output_dir = os.path.join(self.test_dir, "test_output")
        os.makedirs(self.base_output_dir, exist_ok=True)
        
        # Path to lineum.py
        self.lineum_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "lineum.py")
        
        # Default env for subprocess
        self.env = os.environ.copy()
        self.env["LINEUM_BASE_OUTPUT_DIR"] = self.base_output_dir
        self.env["LINEUM_RUN_MODE"] = "false" # don't run simulation
        self.env["PYTHONUTF8"] = "1"
        
        # Patch os.environ for current process too (for unit tests using import)
        self.original_env = os.environ.copy()
        os.environ["LINEUM_BASE_OUTPUT_DIR"] = self.base_output_dir

    def tearDown(self):
        try:
            shutil.rmtree(self.test_dir)
        except OSError:
            pass
        # Restore env
        os.environ.clear()
        os.environ.update(self.original_env)

    def run_sciprt(self, run_id="test", steps=0):
        """Helper to run lineum.py as a script."""
        env = self.env.copy()
        env["LINEUM_RUN_ID"] = "6" # Keep valid numeric ID
        env["LINEUM_RUN_TAG"] = str(run_id) # Override tag directly
        env["LINEUM_STEPS"] = str(steps)
        # We just want to trigger init, so run very few steps or 0 if possible
        # Since logic runs at import/init, even 0 steps is fine, but verify 1 step runs.
        
        cmd = [sys.executable, self.lineum_script]
        # We need to capture stdout to verify output directory print
        result = subprocess.run(cmd, env=env, capture_output=True, text=True)
        return result

    def create_dummy_checkpoint(self, path, step=10):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        np.savez(path, 
                 psi=np.zeros((10,10)), 
                 phi=np.zeros((10,10)), 
                 kappa=np.zeros((10,10)),
                 step_index=step,
                 next_id=100,
                 track_ids=np.array([1]),
                 track_pos_xy=np.array([[0,0]]),
                 rng_algo="MT19937",
                 rng_keys=np.zeros(1),
                 rng_pos=0,
                 rng_has_gauss=0,
                 rng_cached_gauss=0.0
                 )
    
    def test_run_dir_creation(self):
        """Test that a new run creates a timestamped subdirectory in the mocked base output."""
        result = self.run_sciprt(run_id="run_creation_test", steps=1)
        
        # Check that a directory was created in base_output_dir/runs/
        runs_dir = os.path.join(self.base_output_dir, "runs")
        self.assertTrue(os.path.isdir(runs_dir), f"runs/ directory not created in {self.base_output_dir}")
        self.assertTrue(os.path.exists(runs_dir))
        
        subdirs = glob.glob(os.path.join(runs_dir, "run_creation_test_*"))
        self.assertEqual(len(subdirs), 1, f"Expected 1 run dir, found {len(subdirs)}: {subdirs}. Stdout: {result.stdout}")
        
        # Check latest_run.txt
        latest_run_path = os.path.join(self.base_output_dir, "latest_run.txt")
        self.assertTrue(os.path.exists(latest_run_path), "latest_run.txt not created")
        
        with open(latest_run_path, 'r') as f:
            content = f.read().strip()
        
        # Content should point to the run dir (relative)
        expected_rel = os.path.relpath(subdirs[0], self.base_output_dir)
        # Normalizing separators for Windows
        content_norm = content.replace("/", os.sep).replace("\\", os.sep)
        expected_norm = expected_rel.replace("/", os.sep).replace("\\", os.sep)
        
        self.assertEqual(content_norm, expected_norm)

    def test_two_runs_separate_dirs(self):
        """Test that two consecutive runs create different directories."""
        self.run_sciprt(run_id="run_seq", steps=1)
        time.sleep(1.2) # Ensure timestamp tick (Windows resolution ~15ms, but safer >1s for %S change)
        
        # Disable resume for the second run to FORCE new directory creation
        self.env["LINEUM_RESUME"] = "0"
        
        self.run_sciprt(run_id="run_seq", steps=1)
        
        runs_dir = os.path.join(self.base_output_dir, "runs")
        subdirs = glob.glob(os.path.join(runs_dir, "run_seq_*"))
        self.assertEqual(len(subdirs), 2, "Expected 2 separate run directories")

    def test_find_latest_checkpoint_logic(self):
        """Unit test for priority logic using direct import (mocking env is tricky here, so we test logic function)."""
        import importlib
        try:
            import lineum
            importlib.reload(lineum) # Ensure it picks up the new env var
        except ImportError:
            # Maybe path issue?
            sys.path.append(os.path.dirname(os.path.abspath(__file__)))
            import lineum
            importlib.reload(lineum)
        
        # Use our test base dir for validation
        run_dir_1 = os.path.join(self.base_output_dir, "runs", "run1")
        run_dir_2 = os.path.join(self.base_output_dir, "runs", "run2")
        legacy_dir = os.path.join(self.base_output_dir, "checkpoints") # Legacy pattern
        
        # Create checkpoints
        ckpt_1 = os.path.join(run_dir_1, "checkpoints", "ckpt_1.npz") # Prio 2 (if active)
        ckpt_2 = os.path.join(run_dir_2, "checkpoints", "ckpt_2.npz") # Prio 2 (if active)
        ckpt_legacy = os.path.join(legacy_dir, "legacy.npz") # Prio 3
        
        self.create_dummy_checkpoint(ckpt_1, step=10)
        self.create_dummy_checkpoint(ckpt_legacy, step=20)
        self.create_dummy_checkpoint(ckpt_2, step=30)
        
        # 1. Explicit
        found = lineum._find_latest_checkpoint(explicit_path=ckpt_1, base_output_dir=self.base_output_dir)
        self.assertEqual(os.path.abspath(found), os.path.abspath(ckpt_1))
        
        # 2. Latest Run (Prio 2)
        # Point latest_run.txt to run2
        with open(os.path.join(self.base_output_dir, "latest_run.txt"), "w") as f:
            f.write(os.path.relpath(run_dir_2, self.base_output_dir))
            
        found = lineum._find_latest_checkpoint(base_output_dir=self.base_output_dir)
        # Check if run2 is found. Note: run2/checkpoints/ckpt_2.npz exists.
        # But wait, lineum._find_latest_checkpoint implementation assumes normalized path?
        # Let's trace it: 
        # reads latest_run.txt -> run_dir_2 (relative)
        # join(base, run_dir_2) -> absolute path to run2
        # joins "checkpoints" -> scans it.
        # Should work.
        self.assertEqual(os.path.abspath(found), os.path.abspath(ckpt_2))
        
        # 3. Legacy Fallback
        # Remove pointer
        os.remove(os.path.join(self.base_output_dir, "latest_run.txt"))
        
        found = lineum._find_latest_checkpoint(base_output_dir=self.base_output_dir)
        # Should populate candidates from:
        # - legacy (output/checkpoints)
        # So it should find legacy.npz
        self.assertEqual(os.path.abspath(found), os.path.abspath(ckpt_legacy))

    def test_resume_in_place(self):
        """Test that resuming reuses the existing run directory."""
        # 1. Run initial simulation (steps=1)
        self.run_sciprt(run_id="run_orig", steps=1)
        
        # Identify the run dir
        runs_dir = os.path.join(self.base_output_dir, "runs")
        run_dirs = [d for d in os.listdir(runs_dir) if os.path.isdir(os.path.join(runs_dir, d))]
        self.assertEqual(len(run_dirs), 1, "Should have exactly 1 run dir initially")
        original_run_dir = os.path.join(runs_dir, run_dirs[0])
        original_run_name = run_dirs[0]

        # Ensure checkpoint exists
        ckpt_dir = os.path.join(original_run_dir, "checkpoints")
        self.assertTrue(os.path.exists(ckpt_dir))
        ckpts = glob.glob(os.path.join(ckpt_dir, "*.npz"))
        self.assertTrue(len(ckpts) > 0, "Initial run should create a checkpoint")

        # 2. Resume (implicitly via latest_run.txt which points to original_run_dir)
        env = self.env.copy()
        env["LINEUM_RESUME"] = "1"
        env["LINEUM_RUN_TAG"] = "run_new_tag_ignored" 
        env["LINEUM_STEPS"] = "1"
        # Important: Don't set explicit checkpoint, let it find latest_run.txt

        # Run script
        result = subprocess.run(
            [sys.executable, "lineum.py"],
            cwd=os.getcwd(),
            env=env,
            capture_output=True,
            text=True
        )

        # Check stdout for "RESUME-IN-PLACE"
        # print("STDOUT:", result.stdout)
        # print("STDERR:", result.stderr)

        self.assertIn("RESUME-IN-PLACE", result.stdout)
        self.assertIn(original_run_name, result.stdout)

        # 3. Verify NO new directory was created
        run_dirs_after = [d for d in os.listdir(runs_dir) if os.path.isdir(os.path.join(runs_dir, d))]
        self.assertEqual(len(run_dirs_after), 1, "Should still have exactly 1 run dir (reused)")
        self.assertEqual(run_dirs_after[0], original_run_name)

if __name__ == "__main__":
    unittest.main()
