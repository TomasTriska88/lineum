# Verification Checklist for Lineum Core (spec6_false_s41)

This document serves for independent verification (reproduction) of the canonical Lineum simulation run in the `spec6_false_s41` configuration.

## 1. Prerequisites

- **OS:** Windows / Linux / macOS
- **Python:** Version 3.10+
- **Dependencies:** Installed libraries from `requirements.txt` (e.g., `numpy`, `scipy`, `pandas`, `matplotlib`).

### Installation (if not already installed):
```bash
pip install -r requirements.txt
```

## 2. Run Reproduction (Pipeline)

To launch the simulation, use one of the following commands. The scripts automatically set the required environment variables (including `PYTHONUTF8=1` for Windows).

### A) Quick Test (Validation Mode)
Runs only 200 simulation steps without generating expensive visual artifacts (GIFs). Useful for verifying that the installation works and the physics calculation is running.

```bash
python scripts/repro_spec6_false_s41.py --quick
```

**Expected Output:**
- The script completes without errors (exit code 0).
- It prints the path to the created `run_summary.csv`.

### B) Full Run (Full Reproduction)
Runs the complete simulation (default 2000 steps) including checkpoint saving and visualizations.

```bash
python scripts/repro_spec6_false_s41.py
```
*(Note: This run may take tens of minutes to hours depending on hardware.)*

## 3. Results Verification

After completing the reproduction (A or B), run the verification script. This tool checks the integrity of the outputs and the presence of key metrics.

```bash
python scripts/verify_repro_run.py --latest
```

**Success Criteria (PASS):**
1. The script finds `run_summary.csv` from the latest run.
2. The file contains key physics metrics (`noise_strength`, `drift_strength`).
3. Expected output directories are present (`checkpoints`, and optionally `plots`/`frames` for full runs).
4. **Reference Verification:** The script auto-verifies canonical snapshots against `docs/reference_manifest_spec6_false_s41.json`.
5. The script outputs: `VERIFIKACE: PASS`.

## Troubleshooting

- **Encoding Error (Windows):** If you encounter encoding errors, ensure you are running via the provided scripts, which enforce `PYTHONUTF8=1`.
- **Missing Libraries:** Check `pip freeze` against `requirements.txt`.

## 4. Reference Artifacts Verification (Audit-Grade)

- **Source of Truth:** `docs/reference_manifest_spec6_false_s41.json`
- **Location:** `output/repro/runs/spec6_false_s41_*/reference/`
- **Files:** `step_200.npz`, `step_1000.npz`, `final.npz`.
- **Validation Logic:**
    - **Step 1:** Check if files exist.
    - **Step 2:** Compute strict hash: `sha256( dtype|shape| + raw_bytes_little_endian_c_order )`.
    - **Step 3:** Compare against manifest.
- **Command:** `python scripts/verify_repro_run.py --latest` (Fail if mismatch).

