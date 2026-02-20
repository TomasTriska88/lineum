import os
import sys
import argparse
import pathlib
import csv
import glob

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

    # --- VERIFIKACE REFERENCE SNAPSHOTŮ (Nový audit krok) ---
    print("-" * 40)
    print("REFERENCE SNAPSHOTS CHECK")
    
    ref_dir = target_run_dir / "reference"
    expected_snapshots = ["step_200.npz", "step_1000.npz", "final.npz"]
    
    # Check 1: Existence souborů
    missing_snapshots = []
    if not ref_dir.exists():
        print(f"[FAIL] Adresář 'reference' chybí v {target_run_dir}.")
        snapshots_ok = False
    else:
        for snap in expected_snapshots:
            if not (ref_dir / snap).exists():
                missing_snapshots.append(snap)
        
        if missing_snapshots:
            print(f"[FAIL] Chybí referenční snapshoty: {missing_snapshots}")
            snapshots_ok = False
        else:
            print(f"[OK] Nalezeny všechny 3 kritické snapshoty: {expected_snapshots}")
            snapshots_ok = True

    # Check 2: Metadata consistency (pokud soubory existují)
    meta_ok = True
    if snapshots_ok:
        import numpy as np
        import json
        for snap in expected_snapshots:
            try:
                with np.load(ref_dir / snap) as data:
                    if "_meta" not in data:
                        print(f"[FAIL] {snap} neobsahuje '_meta'.")
                        meta_ok = False
                        break
                    
                    meta = json.loads(str(data["_meta"]))
                    
                    # Kontrola, zda step v metadatech odpovídá názvu (pro step_X.npz)
                    if snap.startswith("step_"):
                        expected_step = int(snap.split("_")[1].split(".")[0])
                        if int(meta.get("step", -1)) != expected_step:
                            print(f"[FAIL] {snap}: step v metadata ({meta.get('step')}) neodpovídá názvu.")
                            meta_ok = False
                    
                    # Kontrola základních klíčů
                    required_meta = ["seed", "run_id", "grid"]
                    if not all(k in meta for k in required_meta):
                         print(f"[FAIL] {snap}: chybí povinná metadata {required_meta}")
                         meta_ok = False

            except Exception as e:
                print(f"[FAIL] Chyba při čtení {snap}: {e}")
                meta_ok = False
        
        if meta_ok:
            print("[OK] Metadata snapshotů jsou konzistentní.")

    # Check 3: Hashes (pokud existuje reference_hashes.json)
    hashes_ok = True # Defaultně PASS, pokud soubor neexistuje (dle zadání)
    hashes_json_path = ref_dir / "reference_hashes.json"
    
    if hashes_json_path.exists() and snapshots_ok:
        print("[INFO] Ověřuji bit-exact shodu hashů (reference_hashes.json)...")
        try:
            with open(hashes_json_path, "r") as f:
                saved_hashes = json.load(f)
            
            import hashlib
            
            # Helper pro kanonický hash (musí být identický s repro skriptem)
            def compute_canonical_hash_verify(data_array):
                if data_array.dtype.byteorder == '>':
                    data_array = data_array.byteswap().newbyteorder('<')
                if not data_array.flags['C_CONTIGUOUS']:
                    data_array = np.ascontiguousarray(data_array)
                return hashlib.sha256(data_array.tobytes()).hexdigest()

            for snap in expected_snapshots:
                if snap not in saved_hashes:
                    print(f"[WARN] {snap} není v reference_hashes.json, přeskakuji.")
                    continue
                
                expected = saved_hashes[snap]
                
                with np.load(ref_dir / snap) as data:
                    psi_h = compute_canonical_hash_verify(data["psi"])
                    phi_h = compute_canonical_hash_verify(data["phi"])
                    
                    if psi_h != expected["psi_sha256"]:
                        print(f"[FAIL] Hash mismatch pro {snap} (psi)!")
                        print(f"       Expected: {expected['psi_sha256']}")
                        print(f"       Got:      {psi_h}")
                        hashes_ok = False
                    
                    if phi_h != expected["phi_sha256"]:
                        print(f"[FAIL] Hash mismatch pro {snap} (phi)!")
                        hashes_ok = False
            
            if hashes_ok:
                print("[OK] Všechny hashe odpovídají (Bit-Exact Verified).")

        except Exception as e:
            print(f"[FAIL] Chyba při verifikaci hashů: {e}")
            hashes_ok = False
    elif not hashes_json_path.exists() and snapshots_ok:
        print("[INFO] reference_hashes.json nenalezen -> SKIP hash check (PASS).")

    print("-" * 40)
    
    # Finální report
    print(f"REFERENCE_SNAPSHOTS: {'PASS' if (snapshots_ok and meta_ok) else 'FAIL'}")
    print(f"REFERENCE_HASHES:    {'PASS' if hashes_ok else 'FAIL'}")
    
    final_status = "PASS" if (snapshots_ok and meta_ok and hashes_ok) else "FAIL"
    print(f"VERIFIKACE:          {final_status}")
    print("-" * 40)
    
    if final_status == "FAIL":
        sys.exit(1)
    
    sys.exit(0)

if __name__ == "__main__":
    main()
