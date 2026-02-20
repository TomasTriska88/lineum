import os
import sys
import argparse
import pathlib
import zipfile
import hashlib
import tempfile
import numpy as np

def hash_data(data_bytes):
    sha = hashlib.sha256()
    sha.update(data_bytes)
    return sha.hexdigest()

def main():
    parser = argparse.ArgumentParser(description="Verifikace nezávislého Reference Packu.")
    parser.add_argument("--pack", type=str, required=True, help="Cesta k ZIP balíčku (.zip)")
    args = parser.parse_args()

    pack_path = pathlib.Path(args.pack).resolve()
    if not pack_path.exists():
        print(f"[FAIL] Zdrojový balíček nenalezen: {pack_path}")
        sys.exit(1)

    print(f"[INFO] Analyzuji pack: {pack_path.name}")

    # Initialize statuses
    pack_files_ok = True
    pack_hashes_ok = True
    pack_npz_ok = True

    required_files = [
        "manifest.json",
        "run_summary.csv",
        "SHA256SUMS.txt",
        "README.md",
        "reference/step_200.npz",
        "reference/step_1000.npz",
        "reference/final.npz"
    ]

    with zipfile.ZipFile(pack_path, 'r') as zf:
        zip_files = zf.namelist()
        
        # Security check: Reject suspicious paths
        for zf_name in zip_files:
            if ".." in zf_name or zf_name.startswith("/") or zf_name.startswith("\\") or os.path.isabs(zf_name):
                print(f"[FAIL] Bezpečnostní riziko: Nelegální cesta v archivu: {zf_name}")
                sys.exit(1)

        # 1. Rozbalené soubory - kontrola existence
        for req_file in required_files:
            if req_file not in zip_files:
                print(f"[FAIL] V balíčku chybí povinný soubor: {req_file}")
                pack_files_ok = False

        if not pack_files_ok:
             # Fast fail for files
             print("-" * 40)
             print("PACK_FILES:        FAIL")
             print("PACK_HASHES:       FAIL")
             print("PACK_NPZ_SCHEMA:   FAIL")
             print("VERIFICATION:      FAIL")
             print("-" * 40)
             sys.exit(1)

        # 2. SHA256SUMS.txt verifikace
        expected_hashes = {}
        try:
            sums_content = zf.read("SHA256SUMS.txt").decode("utf-8")
            for line in sums_content.splitlines():
                line = line.strip()
                if not line: continue
                parts = line.split("  ", 1)
                if len(parts) == 2:
                    expected_hashes[parts[1]] = parts[0]
        except Exception as e:
            print(f"[FAIL] Nelze přečíst SHA256SUMS.txt: {e}")
            pack_hashes_ok = False

        for arcname, expected_hash in expected_hashes.items():
            if arcname not in zip_files:
                print(f"[FAIL] Soubor {arcname} uveden v SHA256SUMS.txt neexistuje!")
                pack_files_ok = False
                pack_hashes_ok = False
            else:
                actual_hash = hash_data(zf.read(arcname))
                if actual_hash != expected_hash:
                    print(f"[FAIL] Hash mismatch pro {arcname}!")
                    print(f"       Očekáváno: {expected_hash}")
                    print(f"       Nalezeno:  {actual_hash}")
                    pack_hashes_ok = False

        if pack_hashes_ok:
            print("[OK] Všechny soubory prošly kontrolou SHA256 otisku.")

        # 3. NPZ Schema verifikace
        npz_files = ["reference/step_200.npz", "reference/step_1000.npz", "reference/final.npz"]
        for npz_name in npz_files:
            if npz_name not in zip_files:
                continue # Already caught above, but play safe
            
            try:
                import io
                npz_bytes = zf.read(npz_name)
                # Load NPZ from memory buffer
                with np.load(io.BytesIO(npz_bytes)) as data:
                    keys = list(data.keys())
                    if 'psi' not in keys:
                        print(f"[FAIL] Soubor {npz_name} neobsahuje proměnnou 'psi'.")
                        pack_npz_ok = False
                    elif data['psi'].dtype not in (np.complex128, np.complex64):
                        print(f"[FAIL] Soubor {npz_name} 'psi' není komplexní typ ({data['psi'].dtype}).")
                        pack_npz_ok = False

                    if 'phi' not in keys:
                        print(f"[FAIL] Soubor {npz_name} neobsahuje proměnnou 'phi'.")
                        pack_npz_ok = False
                    elif data['phi'].dtype not in (np.float64, np.float32):
                         print(f"[FAIL] Soubor {npz_name} 'phi' není reálný typ ({data['phi'].dtype}).")
                         pack_npz_ok = False

                    if '_meta' not in keys:
                        print(f"[FAIL] Soubor {npz_name} neobsahuje proměnnou '_meta'.")
                        pack_npz_ok = False
                    else:
                        meta_item = data['_meta'].item()
                        meta_data = None
                        
                        if isinstance(meta_item, dict):
                            meta_data = meta_item
                        elif isinstance(meta_item, str):
                            import json
                            try:
                                meta_data = json.loads(meta_item)
                            except Exception as e:
                                print(f"[FAIL] Nelze rozparsovat JSON v _meta pro {npz_name}: {e}")
                                pack_npz_ok = False
                        else:
                            print(f"[FAIL] Soubor {npz_name} '_meta' není slovník ani platný JSON string ({type(meta_item)}).")
                            pack_npz_ok = False
                            
                        if meta_data is not None:
                            expected_step = -1
                            if "step_200" in npz_name: expected_step = 200
                            elif "step_1000" in npz_name: expected_step = 1000
                            
                            # Validate step presence and correctness if expected_step > 0.
                            if expected_step > 0 and meta_data.get('step') != expected_step:
                                 print(f"[FAIL] Soubor {npz_name} má špatný krok v _meta: {meta_data.get('step')} vs očekávaný {expected_step}")
                                 pack_npz_ok = False

            except Exception as e:
                print(f"[FAIL] Chyba při čtení NPZ {npz_name}: {e}")
                pack_npz_ok = False

        if pack_npz_ok:
             print("[OK] Všechny NPZ snapshoty mají korektní schéma (psi, phi, _meta).")


    print("-" * 40)
    print(f"PACK_FILES:        {'PASS' if pack_files_ok else 'FAIL'}")
    print(f"PACK_HASHES:       {'PASS' if pack_hashes_ok else 'FAIL'}")
    print(f"PACK_NPZ_SCHEMA:   {'PASS' if pack_npz_ok else 'FAIL'}")

    final_verification = "PASS" if (pack_files_ok and pack_hashes_ok and pack_npz_ok) else "FAIL"
    print(f"VERIFICATION:      {final_verification}")
    print("-" * 40)

    sys.exit(0 if final_verification == "PASS" else 1)

if __name__ == "__main__":
    main()
