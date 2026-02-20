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
    parser = argparse.ArgumentParser(description="Verifikace kanonického běhu Lineum (spec6_false_s41).")
    parser.add_argument("--base-dir", type=str, default="output/repro", help="Základní výstupní adresář (default: output/repro)")
    parser.add_argument("--tag", type=str, default="spec6_false_s41", help="Tag běhu (default: spec6_false_s41)")
    parser.add_argument("--latest", action="store_true", default=True, help="Ověřit nejnovější běh (default: True)")
    
    args = parser.parse_args()

    # Cesty
    # Base dir je relativní ke CWD, odkud se skript spouští (očekáváme root repo)
    base_path = pathlib.Path(args.base_dir).resolve()
    runs_path = base_path / "runs"
    
    if not runs_path.exists():
        # Fallback, pokud lineum.py ukládá přímo do base_dir (což by nemělo, ale pro robustnost)
        runs_path = base_path

    print(f"[INFO] Hledám běhy v: {runs_path}")
    print(f"[INFO] Hledaný tag: {args.tag}")

    # Hledání adresáře běhu
    pattern = f"{args.tag}_*"
    candidates = sorted(runs_path.glob(pattern))
    
    # Filtrujeme jen adresáře
    candidates = [d for d in candidates if d.is_dir()]
    
    if not candidates:
        print(f"[FAIL] Nenalezen žádný adresář běhu odpovídající tagu '{args.tag}' v '{runs_path}'.")
        sys.exit(1)

    # Vybereme nejnovější (podle mtime)
    candidates.sort(key=lambda p: p.stat().st_mtime)
    target_run_dir = candidates[-1]
    
    print(f"[INFO] Vybrán nejnovější běh: {target_run_dir.name}")
    
    # Kontrola run_summary.csv
    summary_file = target_run_dir / "run_summary.csv"
    if not summary_file.exists():
        print(f"[FAIL] Soubor run_summary.csv nenalezen v {target_run_dir}.")
        sys.exit(1)

    print(f"[OK] run_summary.csv nalezen.")

    # Parsování CSV
    metrics = {}
    try:
        with open(summary_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            # CSV má strukturu: metric,value
            # noise_strength,0.005
            # ...
            # Musíme to převést na dict {metric: value}
            for row in reader:
                if "metric" in row and "value" in row:
                    metrics[row["metric"]] = row["value"]
            
            if not metrics:
                print("[FAIL] run_summary.csv neobsahuje žádná data nebo má špatný formát.")
                sys.exit(1)
    except Exception as e:
        print(f"[FAIL] Chyba při čtení CSV: {e}")
        sys.exit(1)

    # Verifikace klíčových metrik
    # spec6_false_s41 (Config 6 false) -> LOW_NOISE=False, DRIFT=True (implicitně z lineum.py logiky)
    # Zkontrolujeme noise_strength a drift_strength pokud jsou v CSV
    
    required_keys = ["noise_strength", "drift_strength"]
    missing_keys = [k for k in required_keys if k not in metrics]
    
    if missing_keys:
        print(f"[WARN] V run_summary.csv chybí očekávané sloupce: {missing_keys}")
        # Nefailujeme tvrdě, pokud se změnily názvy sloupců v lineum.py, ale varujeme.
    else:
        ns = metrics.get("noise_strength", "N/A")
        ds = metrics.get("drift_strength", "N/A")
        print(f"[INFO] noise_strength: {ns}")
        print(f"[INFO] drift_strength: {ds}")
        
    # Kontrola adresářové struktury
    # Checkpoints
    ckpt_dir = target_run_dir / "checkpoints"
    if not ckpt_dir.exists():
        print("[WARN] Adresář 'checkpoints' chybí.")
    elif not list(ckpt_dir.glob("*.npz")):
        print("[WARN] Adresář 'checkpoints' je prázdný.")
    else:
        print("[OK] Checkpoints nalezeny.")

    # Plots / Frames
    plots_dir = target_run_dir / "plots"
    frames_dir = target_run_dir / "frames"
    
    if plots_dir.exists() or frames_dir.exists():
        print("[OK] Vizualizační výstupy (plots/frames) detekovány.")
    else:
        print("[WARN] Žádné vizualizační výstupy (plots ani frames) nenalezeny. (OK pro --quick, ale zkontrolujte).")

    # --- VERIFIKACE REFERENCE SNAPSHOTŮ (Manifest-Based) ---
    print("-" * 40)
    print("REFERENCE SNAPSHOTS CHECK (Manifest-Based)")
    
    script_dir = pathlib.Path(__file__).parent.resolve()
    root_dir = script_dir.parent
    manifest_path = root_dir / "docs" / "reference_manifest_spec6_false_s41.json"
    
    if not manifest_path.exists():
        print(f"[FAIL] Kanonický manifest nenalezen: {manifest_path}")
        print("REFERENCE_SNAPSHOTS: FAIL")
        print("REFERENCE_HASHES:    FAIL")
        print("VERIFIKACE:          FAIL")
        sys.exit(1)
        
    print(f"[INFO] Načítám manifest: {manifest_path.name}")
    try:
        with open(manifest_path, "r") as f:
            manifest = json.load(f)
    except Exception as e:
        print(f"[FAIL] Chyba při čtení manifestu: {e}")
        sys.exit(1)

    ref_dir = target_run_dir / "reference"
    if not ref_dir.exists():
        print(f"[FAIL] Adresář 'reference' chybí v {target_run_dir}.")
        # Fail immediately
        print("-" * 40)
        print("REFERENCE_SNAPSHOTS: FAIL")
        print("REFERENCE_HASHES:    FAIL")
        print("VERIFIKACE:          FAIL")
        print("-" * 40)
        sys.exit(1)
        
    expected_snapshots = manifest.get("snapshots", {})
    if not expected_snapshots:
        print("[FAIL] Manifest neobsahuje žádné snapshoty.")
        sys.exit(1)

    snapshots_ok = True
    hashes_ok = True
    
    # Imports already at top level
    
    def compute_strict_hash_verify(data_array):
        # Musí být identické s repro skriptem
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
        fname = f"{key}.npz" if key == "final" else f"{key}.npz" # key je step_200, step_1000, final
        # Pozn: v manifestu jsou klíče "step_200", "step_1000", "final".
        # Soubory se jmenují stejně + .npz (kromě final, tam je to final.npz)
        # Upravíme logiku filenames v manifest generatoru jsme použili "step_200.npz" jako fname?
        # Ne, v manifest generatoru: snapshots = {"step_200": "step_200.npz", ...}
        # Ale klíče v jsonu jsou "step_200", "step_1000", "final".
        # Musime odvodit filename.
        
        filename = f"{key}.npz" # default assumption
        # Ale moment, v repro skriptu: filename = "final.npz" if step == "final" else f"step_{step}.npz"
        # key "step_200" -> "step_200.npz". key "final" -> "final.npz". OK.
        
        fpath = ref_dir / filename
        
        if not fpath.exists():
            print(f"[FAIL] Chybí snapshot: {filename}")
            snapshots_ok = False
            hashes_ok = False # Nemůžeme ověřit hash
            continue
            
        # Load and verify hash
        try:
            with np.load(fpath) as data:
                psi = data['psi']
                phi = data['phi']
                
                # Metadata check (basic)
                if "_meta" not in data:
                     print(f"[FAIL] {filename} chybí _meta.")
                     snapshots_ok = False
                
                # Hash Validation
                psi_h = compute_strict_hash_verify(psi)
                phi_h = compute_strict_hash_verify(phi)
                
                if psi_h != info["psi_hash"]:
                    print(f"[FAIL] {filename} PSI hash mismatch!")
                    print(f"       Expected: {info['psi_hash']}")
                    print(f"       Got:      {psi_h}")
                    hashes_ok = False
                
                if phi_h != info["phi_hash"]:
                    print(f"[FAIL] {filename} PHI hash mismatch!")
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
    print(f"VERIFIKACE:          {final_status}")
    print("-" * 40)
    
    sys.exit(0 if final_status == "PASS" else 1)

if __name__ == "__main__":
    main()
