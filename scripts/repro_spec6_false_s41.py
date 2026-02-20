import os
import sys
import subprocess
import argparse
import pathlib
import glob

def main():
    parser = argparse.ArgumentParser(description="Spustí kanonický běh spec6_false_s41 (Lineum).")
    parser.add_argument("--steps", type=str, default="2000", help="Počet kroků simulace (default: 2000)")
    parser.add_argument("--quick", action="store_true", help="Rychlý režim: 200 kroků, vypnuté ukládání artefaktů.")
    args = parser.parse_args()

    # Základní cesty
    # Předpokládáme, že skript je v root/scripts/, takže root je o jednu úroveň výš.
    script_dir = pathlib.Path(__file__).parent.resolve()
    root_dir = script_dir.parent
    lineum_py = root_dir / "lineum.py"
    
    # Výstupní adresář pro repro
    repro_output_dir = root_dir / "output" / "repro"
    repro_output_dir.mkdir(parents=True, exist_ok=True)

    # Nastavení prostředí (env vars)
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
        print("[INFO] Zapínám --quick režim: steps=200, artefakty VYPNUTY.")
        env["LINEUM_STEPS"] = "200"
        # Vypnutí těžkých artefaktů
        env["LINEUM_SAVE_STATE"] = "0"
        env["LINEUM_SAVE_GIFS"] = "0"
        env["LINEUM_SAVE_POV"] = "0"
        env["LINEUM_SAVE_PNGS"] = "0" # Pro jistotu vypneme i PNG, pokud to lineum podporuje (env override)
        env["LINEUM_STORE_EVERY"] = "50" # Méně časté ukládání
    else:
        env["LINEUM_STEPS"] = args.steps
        # Defaultní chování lineum.py (ukládá artefakty) necháme být, 
        # případně můžeme explicitně zapnout, ale lineum.py má v defaultu zapnuto, 
        # pokud CONFIGS neřekne jinak. Pro run_id 6 false je config definován.

    # Sestavení příkazu
    cmd = [sys.executable, str(lineum_py)]

    print(f"[INFO] Spouštím lineum.py: {' '.join(cmd)}")
    print(f"[INFO] CWD: {root_dir}")
    print(f"[INFO] ENV overrides: RUN_ID={env['LINEUM_RUN_ID']}, STEPS={env['LINEUM_STEPS']}")

    # Spuštění subprocessu
    try:
        subprocess.run(cmd, cwd=str(root_dir), env=env, check=True)
    except subprocess.CalledProcessError as e:
        print(f"[CHYBA] Simulace selhala s kódem {e.returncode}.")
        sys.exit(e.returncode)

    # Po doběhu nalezení run directory
    # Hledáme složku v output/repro/runs/spec6_false_s41_*
    # lineum.py tvoří: runs/{RUN_TAG}_{timestamp}
    # Takže: output/repro/runs/spec6_false_s41_YYYYMMDD_HHMMSS
    
    # Poznámka: lineum.py v 'runs' modu tvoří podadresář 'runs'.
    # Pokud je BASE_OUTPUT_DIR="output/repro", pak runs budou v "output/repro/runs".
    runs_dir = repro_output_dir / "runs"
    
    if not runs_dir.exists():
         # Fallback, kdyby lineum.py ukládalo přímo (ale podle analýzy ukládá do runs/)
         runs_dir = repro_output_dir 

    print("[INFO] Hledám nejnovější run_summary.csv...")
    
    # Rekurzivní hledání všech run_summary.csv
    # Pattern: runs/spec6_false_s41_*/run_summary.csv
    # Použijeme rglob, ale musíme filtrovat ty správné tagy, abychom nevzali jiné běhy (kdyby tam byly)
    found_summaries = []
    
    # Projdeme všechny složky začínající spec6_false_s41
    candidate_dirs = sorted(runs_dir.glob("spec6_false_s41_*"))
    
    for d in candidate_dirs:
        summary_file = d / "run_summary.csv"
        if summary_file.exists():
            found_summaries.append(summary_file)
            
    if not found_summaries:
        print("[VAROVÁNÍ] Nenalezen žádný run_summary.csv v očekávaných cestách.")
        sys.exit(0)

    # Seřadíme podle mtime (nejnovější = poslední)
    found_summaries.sort(key=lambda p: p.stat().st_mtime)
    
    latest_summary = found_summaries[-1]
    latest_run_dir = latest_summary.parent
    
    # Detekce více běhů
    # Pokud jsme našli více než 1, varujeme, ale vracíme ten nejnovější (podle zadání)
    # Zadání: "Očekávej přesně 1 “nejnovější”; pokud je více, vezmi max(mtime) a vypiš varování se seznamem nalezených."
    # Tady je to myšleno asi tak, že pokud jich vzniklo víc v tom samém čase nebo kontextu, 
    # v praxi budeme mít v adresáři historii. Takže varování spíš pokud jsme teď spustili jeden, a už tam jich je 10 starých.
    # Ale text říká: "pokud je více, vezmi max(mtime) a vypiš varování se seznamem nalezených."
    if len(found_summaries) > 1:
        print(f"[VAROVÁNÍ] Nalezeno více ({len(found_summaries)}) souborů run_summary.csv pro tento tag.")
        print("Seznam nalezených:")
        for s in found_summaries:
            print(f" - {s}")
        print("Používám ten s nejnovějším časem změny (mtime).")

    print("-" * 40)
    print(f"HOTOVO. Výsledky běhu:")
    print(f"Run Directory: {latest_run_dir}")
    print(f"Summary File:  {latest_summary}")
    print("-" * 40)

    if not args.quick:
        print("[INFO] Exporting strict reference snapshots according to manifest...")
        export_cmd = [sys.executable, str(script_dir / "export_reference_from_checkpoints.py"), str(latest_run_dir), str(root_dir / "docs" / "reference_manifest_spec6_false_s41.json")]
        try:
            subprocess.run(export_cmd, check=True)
        except subprocess.CalledProcessError as e:
            print("[FAIL] Reference export failed! Cannot produce canonical output.")
            sys.exit(e.returncode)

if __name__ == "__main__":
    main()
