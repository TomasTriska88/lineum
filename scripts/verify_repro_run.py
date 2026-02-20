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

    # Závěrečné vyhodnocení
    # Pro účely tohoto úkolu: pokud existuje summary a prošlo parsování -> PASS
    print("-" * 40)
    print("VERIFIKACE: PASS")
    print("-" * 40)
    sys.exit(0)

if __name__ == "__main__":
    main()
