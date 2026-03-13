import os
import sys
import subprocess
import argparse
import pathlib
import glob

def main():
    parser = argparse.ArgumentParser(description="Run canonical execution spec6_false_s41 (Lineum).")
    parser.add_argument("--steps", type=str, default="2000", help="Number of simulation steps")
    parser.add_argument("--quick", action="store_true", help="Quick mode: 200 steps, artifacts saving disabled.")
    args = parser.parse_args()

    # Translated comment (original removed due to English-only policy)
    # Translated comment (original removed due to English-only policy)
    script_dir = pathlib.Path(__file__).parent.resolve()
    root_dir = script_dir.parent
    lineum_py = root_dir / "lineum.py"
    
    # Translated comment (original removed due to English-only policy)
    repro_output_dir = root_dir / "output" / "repro"
    repro_output_dir.mkdir(parents=True, exist_ok=True)

    # Translated comment (original removed due to English-only policy)
    env = os.environ.copy()
    
    # 1. Hardcoded parametry pro spec6_false_s41
    env["LINEUM_RUN_ID"] = "6"
    env["LINEUM_RUN_MODE"] = "false"
    env["LINEUM_SEED"] = "41"
    env["LINEUM_RUN_TAG"] = "spec6_false_s41"
    
    # 2. Windows encoding fix
    env["PYTHONUTF8"] = "1"
    
    # 3. Output dir
    env["LINEUM_BASE_OUTPUT_DIR"] = str(repro_output_dir)

    # 4. Logika pro steps a quick mode
    if args.quick:
        print("[INFO] Enabling --quick mode: steps=200, artifacts DISABLED.")
        env["LINEUM_STEPS"] = "200"
        # Translated comment (original removed due to English-only policy)
        env["LINEUM_SAVE_STATE"] = "0"
        env["LINEUM_SAVE_GIFS"] = "0"
        env["LINEUM_SAVE_POV"] = "0"
        env["LINEUM_SAVE_PNGS"] = "0" # Pro jistotu vypneme i PNG, pokud to lineum podporuje (env override)
        env["LINEUM_STORE_EVERY"] = "50" # Translated comment (original removed due to English-only policy)
    else:
        env["LINEUM_STEPS"] = args.steps
        # Translated comment (original removed due to English-only policy)
        # Translated comment (original removed due to English-only policy)
        # Translated comment (original removed due to English-only policy)
        # Translated comment (original removed due to English-only policy)
        env["LINEUM_SAVE_STATE"] = "1"
        env["LINEUM_CHECKPOINT_EVERY"] = "200" # Optimize output specifically for manifest requirements

    # Translated comment (original removed due to English-only policy)
    cmd = [sys.executable, str(lineum_py)]

    print(f"[INFO] Running lineum.py: {' '.join(cmd)}")
    print(f"[INFO] CWD: {root_dir}")
    print(f"[INFO] ENV overrides: RUN_ID={env['LINEUM_RUN_ID']}, STEPS={env['LINEUM_STEPS']}")

    # Translated comment (original removed due to English-only policy)
    try:
        subprocess.run(cmd, cwd=str(root_dir), env=env, check=True)
    except subprocess.CalledProcessError as e:
        print(f"[CHYBA] Simulace selhala s kódem {e.returncode}.")
        sys.exit(e.returncode)

    # Translated comment (original removed due to English-only policy)
    # Translated comment (original removed due to English-only policy)
    # Translated comment (original removed due to English-only policy)
    # Translated comment (original removed due to English-only policy)
    
    # Translated comment (original removed due to English-only policy)
    # Pokud je BASE_OUTPUT_DIR="output/repro", pak runs budou v "output/repro/runs".
    runs_dir = repro_output_dir / "runs"
    
    if not runs_dir.exists():
         # Translated comment (original removed due to English-only policy)
         runs_dir = repro_output_dir 

    print("[INFO] Looking for the latest run_summary.csv...")
    
    # Translated comment (original removed due to English-only policy)
    # Pattern: runs/spec6_false_s41_*/run_summary.csv
    # Translated comment (original removed due to English-only policy)
    found_summaries = []
    
    # Translated comment (original removed due to English-only policy)
    candidate_dirs = sorted(runs_dir.glob("spec6_false_s41_*"))
    
    for d in candidate_dirs:
        summary_file = d / "run_summary.csv"
        if summary_file.exists():
            found_summaries.append(summary_file)
            
    if not found_summaries:
        print("[INFO] Translated text (original removed due to English-only policy)")
        sys.exit(0)

    # Translated comment (original removed due to English-only policy)
    found_summaries.sort(key=lambda p: p.stat().st_mtime)
    
    latest_summary = found_summaries[-1]
    latest_run_dir = latest_summary.parent
    
    # Translated comment (original removed due to English-only policy)
    # Translated comment (original removed due to English-only policy)
    # Translated comment (original removed due to English-only policy)
    # Translated comment (original removed due to English-only policy)
    # Translated comment (original removed due to English-only policy)
    # Translated comment (original removed due to English-only policy)
    if len(found_summaries) > 1:
        print("[INFO] Translated text (original removed due to English-only policy)")
        print("[INFO] Translated text (original removed due to English-only policy)")
        for s in found_summaries:
            print(f" - {s}")
        print("[INFO] Translated text (original removed due to English-only policy)")

    print("-" * 40)
    print("[INFO] Translated text (original removed due to English-only policy)")
    print(f"Run Directory: {latest_run_dir}")
    print(f"Summary File:  {latest_summary}")
    print("-" * 40)

    if not args.quick:
        print("[INFO] Exporting strict reference snapshots according to manifest...")
        export_cmd = [sys.executable, str(script_dir / "export_reference_from_checkpoints.py"), str(latest_run_dir), str(root_dir / "portal" / "src" / "lib" / "data" / "docs" / "reference_manifest_spec6_false_s41.json")]
        try:
            subprocess.run(export_cmd, check=True)
        except subprocess.CalledProcessError as e:
            print("[FAIL] Reference export failed! Cannot produce canonical output.")
            sys.exit(e.returncode)

if __name__ == "__main__":
    main()
