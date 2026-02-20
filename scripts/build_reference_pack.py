import os
import sys
import argparse
import pathlib
import json
import zipfile
import hashlib
import tempfile
import datetime
import shutil

def get_latest_run_dir(base_dir, tag):
    runs_path = pathlib.Path(base_dir) / "runs"
    if not runs_path.exists():
        runs_path = pathlib.Path(base_dir)
    
    candidates = sorted(runs_path.glob(f"{tag}_*"))
    candidates = [d for d in candidates if d.is_dir()]
    
    if not candidates:
        return None
        
    candidates.sort(key=lambda p: p.stat().st_mtime)
    return candidates[-1]

def deterministic_zip(zip_path, files_to_zip):
    # files_to_zip: list of tuples (source_path, arcname)
    files_to_zip.sort(key=lambda x: x[1])
    
    with zipfile.ZipFile(zip_path, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
        for source_path, arcname in files_to_zip:
            # Setting fixed date/time for deterministic behavior
            zinfo = zipfile.ZipInfo(arcname)
            zinfo.date_time = (2025, 1, 1, 0, 0, 0)
            zinfo.compress_type = zipfile.ZIP_DEFLATED
            
            with open(source_path, 'rb') as f:
                zf.writestr(zinfo, f.read())

def hash_file(filepath):
    sha = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while chunk := f.read(8192):
            sha.update(chunk)
    return sha.hexdigest()

def main():
    parser = argparse.ArgumentParser(description="Create a Publishable Reference Pack.")
    parser.add_argument("--latest", action="store_true", help="Find latest run matching tag")
    parser.add_argument("--run_dir", type=str, help="Explicit run directory path")
    parser.add_argument("--out_dir", type=str, default="output/repro/packs/", help="Output directory for the pack")
    parser.add_argument("--tag", type=str, default="spec6_false_s41", help="Tag to identify the run (used with --latest)")
    
    args = parser.parse_args()
    
    if args.latest:
        run_dir = get_latest_run_dir("output/repro", args.tag)
        if not run_dir:
            print(f"[ERROR] Nenalezen žádný běh pro tag '{args.tag}'")
            sys.exit(1)
    elif args.run_dir:
        run_dir = pathlib.Path(args.run_dir).resolve()
    else:
        print("[ERROR] Musíte specifikovat buď --latest nebo --run_dir")
        sys.exit(1)
        
    run_dir = pathlib.Path(run_dir)
    if not run_dir.exists() or not run_dir.is_dir():
        print(f"[ERROR] Run directory neexistuje: {run_dir}")
        sys.exit(1)
        
    print(f"[INFO] Budování packu z: {run_dir}")
    
    out_dir = pathlib.Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    
    # We will gather files into a temporary directory first to hash them
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = pathlib.Path(tmpdir)
        files_for_pack = []
        
        # 1. Reference snapshots
        ref_dir = run_dir / "reference"
        if not ref_dir.exists():
             print(f"[ERROR] Adresář s referenčními snapshoty neexistuje: {ref_dir}")
             sys.exit(1)
             
        for ref_file in ["step_200.npz", "step_1000.npz", "final.npz"]:
            src = ref_dir / ref_file
            if src.exists():
                dst = tmp_path / "reference" / ref_file
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)
                files_for_pack.append((dst, f"reference/{ref_file}"))
            else:
                 print(f"[WARN] Chybí snapshot: {src}")
                 
        # 2. run_summary.csv
        summary = run_dir / "run_summary.csv"
        if summary.exists():
            dst = tmp_path / "run_summary.csv"
            shutil.copy2(summary, dst)
            files_for_pack.append((dst, "run_summary.csv"))
            
        # 3. metrics_summary.csv
        metrics_files = list(run_dir.glob("*_metrics_summary.csv"))
        if metrics_files:
            dst = tmp_path / "metrics_summary.csv" # Rename for standardization
            shutil.copy2(metrics_files[0], dst)
            files_for_pack.append((dst, "metrics_summary.csv"))
            
        # 4. Manifest
        source_manifests = list(run_dir.glob("*_manifest.json"))
        manifest_data = {}
        if source_manifests:
             with open(source_manifests[0], "r") as f:
                 manifest_data = json.load(f)
                 
        manifest_data["created_at"] = datetime.datetime.utcnow().isoformat() + "Z"
        manifest_data["source_run_dir"] = run_dir.name
        
        import platform
        import numpy as np
        manifest_data["python_version"] = platform.python_version()
        manifest_data["numpy_version"] = np.__version__
        
        manifest_dst = tmp_path / "manifest.json"
        with open(manifest_dst, "w") as f:
            json.dump(manifest_data, f, indent=2)
        files_for_pack.append((manifest_dst, "manifest.json"))
        
        # We want to embed files list in manifest EXCEPT the manifest itself and SHA256SUMS.txt
        manifest_files_list = {}
        for src, arcname in files_for_pack:
            if arcname not in ["manifest.json", "SHA256SUMS.txt"]:
                manifest_files_list[arcname] = hash_file(src)
                
        manifest_data["files"] = manifest_files_list
        
        # Write final manifest
        with open(manifest_dst, "w") as f:
            json.dump(manifest_data, f, indent=2)
            
        # Now hash everything including final manifest to create SHA256SUMS.txt
        sums_dst = tmp_path / "SHA256SUMS.txt"
        files_for_pack.sort(key=lambda x: x[1])
        with open(sums_dst, "w", newline='\n') as f:
            for src, arcname in files_for_pack:
                 hash_val = hash_file(src)
                 f.write(f"{hash_val}  {arcname}\n")
                 
        files_for_pack.append((sums_dst, "SHA256SUMS.txt"))
        
        # 6. README.md
        readme_dst = tmp_path / "README.md"
        readme_content = f"""# Lineum Canonical Reference Pack
Run ID: {manifest_data.get('run_id', 'Unknown')}
Source Dir: {run_dir.name}
Created At: {manifest_data.get('created_at', '')}

Tento balíček obsahuje kanonické referenční snapshoty a metadata pro nezávislou verifikaci Lineum Core.

## Jak verifikovat
Pro ověření integrity a shody použijte validátor z repozitáře `lineum-core`:

```bash
python scripts/verify_reference_pack.py --pack <cesta_k_tomuto_zipu>
```

Tím se provede:
1. Kontrola přítomnosti všech povinných souborů.
2. Validace hashů proti `SHA256SUMS.txt`.
3. Validace schématu uvnitř `.npz` snapshotů.
"""
        with open(readme_dst, "w", encoding="utf-8") as f:
            f.write(readme_content)
        files_for_pack.append((readme_dst, "README.md"))
        
        # Create ZIP
        zip_name = f"lineum_reference_pack_{args.tag}_{run_dir.name.split('_')[-2]}_{run_dir.name.split('_')[-1]}.zip"
        if not (run_dir.name.startswith(args.tag)):
             zip_name = f"lineum_reference_pack_{run_dir.name}.zip"
             
        out_zip = out_dir / zip_name
        
        deterministic_zip(out_zip, files_for_pack)
        
        print(f"[OK] Reference pack úspěšně sestaven: {out_zip}")
        print(f"[OK] Velikost: {out_zip.stat().st_size / (1024*1024):.2f} MB")

if __name__ == "__main__":
    main()
