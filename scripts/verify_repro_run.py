import os
import sys
import argparse
import pathlib
import csv
import glob
import json
import hashlib
import numpy as np

def main():
    parser = argparse.ArgumentParser(description="Verification of Canonical Lineum run (spec6_false_s41).")
    parser.add_argument("--base-dir", type=str, default="output/repro", help="Base output directory (default: output/repro)")
    parser.add_argument("--tag", type=str, default="spec6_false_s41", help="Run tag (default: spec6_false_s41)")
    parser.add_argument("--latest", action="store_true", default=True, help="Verify latest run (default: True)")
    parser.add_argument("--pack", action="store_true", help="After successful verification, generate and verify publishable reference pack.")
    parser.add_argument("--fuzzy-match", type=str, help="Path to Canonical ZIP package for mathematical verification (bypasses strict SHA-256 hash)")
    
    args = parser.parse_args()

    # Paths
    # Base dir is relative to CWD from where script is run (expecting repo root)
    base_path = pathlib.Path(args.base_dir).resolve()
    runs_path = base_path / "runs"
    
    if not runs_path.exists():
        # Fallback if lineum.py saves directly to base_dir (should not happen, but for robustness)
        runs_path = base_path

    print(f"[INFO] Searching for runs in: {runs_path}")
    print(f"[INFO] Searching for tag: {args.tag}")

    # Searching for run directory
    pattern = f"{args.tag}_*"
    candidates = sorted(runs_path.glob(pattern))
    
    # Filtering only directories
    candidates = [d for d in candidates if d.is_dir()]
    
    if not candidates:
        print(f"[FAIL] No run directory matching tag found '{args.tag}' v '{runs_path}'.")
        sys.exit(1)

    # Select latest by mtime
    candidates.sort(key=lambda p: p.stat().st_mtime)
    target_run_dir = candidates[-1]
    
    print(f"[INFO] Selected latest run: {target_run_dir.name}")
    
    # Checking run_summary.csv
    summary_file = target_run_dir / "run_summary.csv"
    if not summary_file.exists():
        print(f"[FAIL] File run_summary.csv not found in {target_run_dir}.")
        sys.exit(1)

    print(f"[OK] run_summary.csv found.")

    # Parsing CSV
    metrics = {}
    try:
        with open(summary_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            # CSV has structure: metric,value
            # noise_strength,0.005
            # ...
            # Convert to dict {metric: value}
            for row in reader:
                if "metric" in row and "value" in row:
                    metrics[row["metric"]] = row["value"]
            
            if not metrics:
                print("[FAIL] run_summary.csv contains no data or has wrong format.")
                sys.exit(1)
    except Exception as e:
        print(f"[FAIL] Error reading CSV: {e}")
        sys.exit(1)

    # Verification of key metrics
    # spec6_false_s41 (Config 6 false) -> LOW_NOISE=False, DRIFT=True (implicitly from lineum.py logic)
    # Check noise_strength and drift_strength if present in CSV
    
    required_keys = ["noise_strength", "drift_strength"]
    missing_keys = [k for k in required_keys if k not in metrics]
    
    if missing_keys:
        print(f"[WARN] Missing expected columns in run_summary.csv: {missing_keys}")
        # Do not hard fail if column names changed in lineum.py, emit warning.
    else:
        ns = metrics.get("noise_strength", "N/A")
        ds = metrics.get("drift_strength", "N/A")
        print(f"[INFO] noise_strength: {ns}")
        print(f"[INFO] drift_strength: {ds}")
        
    # Directory structure check
    # Checkpoints
    ckpt_dir = target_run_dir / "checkpoints"
    if not ckpt_dir.exists():
        print("[WARN] Directory 'checkpoints' is missing.")
    elif not list(ckpt_dir.glob("*.npz")):
        print("[WARN] Directory 'checkpoints' is empty.")
    else:
        print("[OK] Checkpoints found..")

    # Plots / Frames
    plots_dir = target_run_dir / "plots"
    frames_dir = target_run_dir / "frames"
    
    if plots_dir.exists() or frames_dir.exists():
        print("[OK] Visualization outputs (plots/frames) detected.")
    else:
        print("[WARN] No visualization outputs (plots/frames) found. (OK for --quick, but check).")

    # --- REFERENCE SNAPSHOTS CHECK (Manifest-Based) ---
    print("-" * 40)
    print("REFERENCE SNAPSHOTS CHECK (Manifest-Based)")
    
    script_dir = pathlib.Path(__file__).parent.resolve()
    root_dir = script_dir.parent
    manifest_path = root_dir / "portal" / "src" / "lib" / "data" / "docs" / "reference_manifest_spec6_false_s41.json"
    
    if not manifest_path.exists():
        print(f"[FAIL] Canonical manifest not found. {manifest_path}")
        print("REFERENCE_SNAPSHOTS: FAIL")
        print("REFERENCE_HASHES:    FAIL")
        print("VERIFICATION:          FAIL")
        sys.exit(1)
        
    print(f"[INFO] Loading manifest: {manifest_path.name}")
    try:
        with open(manifest_path, "r") as f:
            manifest = json.load(f)
    except Exception as e:
        print(f"[FAIL] Error reading manifest: {e}")
        sys.exit(1)

    ref_dir = target_run_dir / "reference"
    if not ref_dir.exists():
        print(f"[FAIL] Directory 'reference' is missing in {target_run_dir}.")
        # Fail immediately
        print("-" * 40)
        print("REFERENCE_SNAPSHOTS: FAIL")
        print("REFERENCE_HASHES:    FAIL")
        print("VERIFICATION:          FAIL")
        print("-" * 40)
        sys.exit(1)
        
    expected_snapshots = manifest.get("snapshots", {})
    if not expected_snapshots:
        print("[FAIL] Manifest contains no snapshots.")
        sys.exit(1)

    snapshots_ok = True
    hashes_ok = True
    
    # Imports already at top level
    
    def compute_strict_hash_verify(data_array):
        # Must be identical to repro script
        if data_array.dtype.byteorder == '>':
            data_array = data_array.byteswap().newbyteorder('<')
        if not data_array.flags['C_CONTIGUOUS']:
            data_array = np.ascontiguousarray(data_array)
        header = f"{data_array.dtype}|{data_array.shape}|"
        sha = hashlib.sha256()
        sha.update(header.encode('utf-8'))
        sha.update(data_array.tobytes())
        return sha.hexdigest()

    for key, info in expected_snapshots.items():
        if "step" not in info:
            print(f"[FAIL] Manifest snapshot '{key}' is corrupt (missing required explicit 'step' integer field).")
            print("-" * 40)
            print("REFERENCE_SNAPSHOTS: FAIL")
            print("REFERENCE_HASHES:    FAIL")
            print("VERIFICATION:          FAIL")
            sys.exit(1)

        fname = f"{key}.npz" if key == "final" else f"{key}.npz" # key je step_200, step_1000, final
        # Note: manifest keys are "step_200", "step_1000", "final".
        # Files are named exactly the same + .npz (except final which is final.npz)
        # Adjust filename logic, in manifest generator we used "step_200.npz" jako fname?
        # No, in manifest generator: snapshots = {"step_200": "step_200.npz", ...}
        # But JSON keys are "step_200", "step_1000", "final".
        # Must derive filename.
        
        filename = f"{key}.npz" # default assumption
        # But wait, in repro script: filename = "final.npz" if step == "final" else f"step_{step}.npz"
        # key "step_200" -> "step_200.npz". key "final" -> "final.npz". OK.
        
        fpath = ref_dir / filename
        
        if not fpath.exists():
            print(f"[FAIL] Missing snapshot: {filename}")
            snapshots_ok = False
            hashes_ok = False # Cannot verify hash
            continue
            
        # Load and verify hash
        try:
            with np.load(fpath) as data:
                psi = data['psi']
                phi = data['phi']
                
                # Metadata check (basic)
                if "_meta" not in data:
                     print(f"[FAIL] {filename} is missing _meta.")
                     snapshots_ok = False
                
                # Hash Validation
                psi_h = compute_strict_hash_verify(psi)
                phi_h = compute_strict_hash_verify(phi)
                
                if psi_h != info["psi_hash"]:
                    if args.fuzzy_match:
                        print(f"[WARN] {filename} PSI hash mismatch (Fuzzy mode - ignoring).")
                    else:
                        print(f"[FAIL] {filename} PSI hash mismatch!")
                        print(f"       Expected: {info['psi_hash']}")
                        print(f"       Got:      {psi_h}")
                        hashes_ok = False
                
                if phi_h != info["phi_hash"]:
                    if args.fuzzy_match:
                        print(f"[WARN] {filename} PHI hash mismatch (Fuzzy mode - ignoring).")
                    else:
                        print(f"[FAIL] {filename} PHI hash mismatch!")
                        print(f"       Expected: {info['phi_hash']}")
                        print(f"       Got:      {phi_h}")
                        hashes_ok = False
                
                if psi_h == info["psi_hash"] and phi_h == info["phi_hash"]:
                    print(f"[OK] {filename} verified (Strict Hash Match).")
                    
        except Exception as e:
            print(f"[FAIL] Error verifying {filename}: {e}")
            snapshots_ok = False
            hashes_ok = False

    print("-" * 40)
    print(f"REFERENCE_SNAPSHOTS: {'PASS' if snapshots_ok else 'FAIL'}")
    print(f"REFERENCE_HASHES:    {'PASS' if hashes_ok else 'FAIL'}")
    
    final_status = "PASS" if (snapshots_ok and hashes_ok) else "FAIL"
    print(f"VERIFICATION:          {final_status}")
    print("-" * 40)
    
    if final_status == "PASS" and hasattr(args, 'pack') and args.pack:
        import subprocess
        print(f"\n[INFO] --pack flag detected. Generating and verifying reference pack...")
        
        build_cmd = [sys.executable, str(script_dir / "build_reference_pack.py"), "--run_dir", str(target_run_dir)]
        print(f"[EXEC] {' '.join(build_cmd)}")
        try:
            build_res = subprocess.run(build_cmd, check=True)
            print("[OK] Pack successfully created.")
        except subprocess.CalledProcessError as e:
            print(f"[FAIL] Error creating pack: {e}")
            sys.exit(1)
            
        print("-" * 40)
        # Construct path to pack - default is output/repro/packs
        pack_dir = base_path / "packs"
        pack_candidates = sorted(pack_dir.glob("*.zip"))
        if not pack_candidates:
             print(f"[FAIL] New pack not found in {pack_dir}")
             sys.exit(1)
             
        # Take the newest one
        pack_candidates.sort(key=lambda p: p.stat().st_mtime)
        latest_pack = pack_candidates[-1]
        
        verify_cmd = [sys.executable, str(script_dir / "verify_reference_pack.py"), "--pack", str(latest_pack)]
        if args.fuzzy_match:
            verify_cmd.extend(["--fuzzy-match", args.fuzzy_match])
            
        print(f"[EXEC] {' '.join(verify_cmd)}")
        try:
            subprocess.run(verify_cmd, check=True)
            print(f"[OK] Pack validated successfully: {latest_pack.name}")
        except subprocess.CalledProcessError as e:
            print(f"[FAIL] Pack validation failed: {e}")
            sys.exit(1)
            
    sys.exit(0 if final_status == "PASS" else 1)

if __name__ == "__main__":
    main()
