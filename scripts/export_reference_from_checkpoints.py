import sys
import json
import shutil
from pathlib import Path

def main():
    if len(sys.argv) < 3:
        print("Usage: python export_reference_from_checkpoints.py <run_dir> <manifest_path>")
        sys.exit(1)
        
    run_dir = Path(sys.argv[1]).resolve()
    manifest_path = Path(sys.argv[2]).resolve()
    
    if not manifest_path.exists():
        print(f"[FAIL] Manifest not found at: {manifest_path}")
        sys.exit(1)
        
    with open(manifest_path, 'r') as f:
        manifest = json.load(f)
        
    snapshots = manifest.get("snapshots", {})
    if not snapshots:
        print(f"[FAIL] 'snapshots' key missing or empty in manifest: {manifest_path}")
        sys.exit(1)
        
    ref_dir = run_dir / "reference"
    ref_dir.mkdir(parents=True, exist_ok=True)
    ckpt_dir = run_dir / "checkpoints"
    
    for key in sorted(snapshots.keys()):
        info = snapshots[key]
        if "step" not in info:
            print(f"[FAIL] Required 'step' key missing for snapshot '{key}' in manifest schema. Cannot export deterministically.")
            sys.exit(1)
            
        try:
            step_int = int(info["step"])
        except ValueError:
            print(f"[FAIL] 'step' must be an integer, got: {info['step']}")
            sys.exit(1)
            
        padded = f"{step_int:08d}"
        
        # Checkpoint pattern: *_ckpt_{padded}.npz
        matches = list(ckpt_dir.glob(f"*_ckpt_{padded}.npz"))
        if len(matches) == 0:
            # Fallback pre koncový stav, kde loop končí na indexe (step - 1) a generátor udělá state_step*
            fallback_step = step_int - 1
            matches = list(ckpt_dir.glob(f"*_state_step{fallback_step}.npz"))
            
        if len(matches) == 0:
            print(f"[FAIL] Found 0 checkpoints matching step '{padded}' for snapshot '{key}'. Run failed to produce artifact.")
            sys.exit(1)
        elif len(matches) > 1:
            print(f"[FAIL] Ambiguous matches! Found multiple ({len(matches)}) checkpoints for step '{padded}'.")
            sys.exit(1)
             
        target_name = f"{key}.npz"
        shutil.copy2(matches[0], ref_dir / target_name)
        print(f"[OK] Exported {matches[0].name} -> reference/{target_name} based on manifest step: {step_int}")

if __name__ == "__main__":
    main()
