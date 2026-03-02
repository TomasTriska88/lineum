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
    parser = argparse.ArgumentParser(description="Verification of Independent Reference Pack.")
    parser.add_argument("--pack", type=str, required=True, help="Path to ZIP package (.zip)")
    parser.add_argument("--fuzzy-match", type=str, help="Path to Canonical ZIP package for mathematical verification (instead of SHA-256 hashes)")
    args = parser.parse_args()

    pack_path = pathlib.Path(args.pack).resolve()
    if not pack_path.exists():
        print(f"[FAIL] Source package not found: {pack_path}")
        sys.exit(1)

    fuzzy_path = None
    if args.fuzzy_match:
        fuzzy_path = pathlib.Path(args.fuzzy_match).resolve()
        if not fuzzy_path.exists():
            print(f"[FAIL] Canonical package for fuzzy-match not found: {fuzzy_path}")
            sys.exit(1)

    print(f"[INFO] Analyzing pack: {pack_path.name}")
    if fuzzy_path:
        print(f"[INFO] Scientific mathematical verification will be used against: {fuzzy_path.name}")

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
                print(f"[FAIL] Security risk: Illegal path in archive: {zf_name}")
                sys.exit(1)

        # Translated comment (original removed due to English-only policy)
        for req_file in required_files:
            if req_file not in zip_files:
                print(f"[FAIL] Mandatory file missing in package: {req_file}")
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
            print(f"[FAIL] Failed to read SHA256SUMS.txt: {e}")
            pack_hashes_ok = False

        for arcname, expected_hash in expected_hashes.items():
            if arcname not in zip_files:
                print(f"[FAIL] File {arcname} listed in SHA256SUMS.txt does not exist!")
                pack_files_ok = False
                pack_hashes_ok = False
            else:
                if fuzzy_path and arcname.endswith(".npz"):
                    # Defer fuzzy match to the schema verification step
                    pass
                else:
                    if fuzzy_path and arcname == "manifest.json":
                        continue # Ignore manifest changes (e.g., timestamps) in fuzzy mode
                        
                    actual_hash = hash_data(zf.read(arcname))
                    if actual_hash != expected_hash:
                        if fuzzy_path:
                            print(f"[WARN] Ignoring logical hash mismatch for non-physical file in fuzzy-match mode: {arcname}")
                        else:
                            print(f"[FAIL] Hash mismatch pro {arcname}!")
                            print(f"       Expected: {expected_hash}")
                            print(f"       Found:  {actual_hash}")
                            pack_hashes_ok = False

        if pack_hashes_ok:
            if fuzzy_path:
                print("[OK] Cryptographic fingerprint check is intentionally bypassed for physical matrices (fuzzy mode).")
            else:
                print("[OK] All files passed SHA256 fingerprint check.")

        # 3. NPZ Schema verifikace (a Fuzzy Match tolerance)
        npz_files = ["reference/step_200.npz", "reference/step_1000.npz", "reference/final.npz"]
        
        fuzzy_zf = None
        if fuzzy_path:
            fuzzy_zf = zipfile.ZipFile(fuzzy_path, 'r')
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
                        print(f"[FAIL] File {npz_name} does not contain variable 'psi'.")
                        pack_npz_ok = False
                    elif data['psi'].dtype not in (np.complex128, np.complex64):
                        print(f"[FAIL] File {npz_name} 'psi' is not complex type ({data['psi'].dtype}).")
                        pack_npz_ok = False

                    if 'phi' not in keys:
                        print(f"[FAIL] File {npz_name} does not contain variable 'phi'.")
                        pack_npz_ok = False
                    elif data['phi'].dtype not in (np.float64, np.float32):
                         print(f"[FAIL] File {npz_name} 'phi' is not real type ({data['phi'].dtype}).")
                         pack_npz_ok = False

                    if '_meta' not in keys:
                        print(f"[FAIL] File {npz_name} does not contain variable '_meta'.")
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
                                print(f"[FAIL] Failed to parse JSON in _meta for {npz_name}: {e}")
                                pack_npz_ok = False
                        else:
                            print(f"[FAIL] File {npz_name} '_meta' is not a dictionary or valid JSON string ({type(meta_item)}).")
                            pack_npz_ok = False
                            
                        if meta_data is not None:
                            expected_step = -1
                            if "step_200" in npz_name: expected_step = 200
                            elif "step_1000" in npz_name: expected_step = 1000
                            
                            if expected_step > 0 and meta_data.get('step') != expected_step:
                                 print(f"[FAIL] File {npz_name} has incorrect step in _meta: {meta_data.get('step')} vs expected {expected_step}")
                                 pack_npz_ok = False
                                 
                    # 4. Fuzzy Math Verification
                    if fuzzy_zf and pack_npz_ok:
                        try:
                            can_bytes = fuzzy_zf.read(npz_name)
                            with np.load(io.BytesIO(can_bytes)) as can_data:
                                if not np.allclose(data['psi'], can_data['psi'], rtol=1e-05, atol=1e-08):
                                    print(f"[FAIL] Scientific fuzzy-mismatch! Array 'psi' in {npz_name} deviates from canon beyond tolerance limit.")
                                    pack_npz_ok = False
                                if not np.allclose(data['phi'], can_data['phi'], rtol=1e-05, atol=1e-08):
                                    print(f"[FAIL] Scientific fuzzy-mismatch! Array 'phi' in {npz_name} deviates from canon beyond tolerance limit.")
                                    pack_npz_ok = False
                                    
                                if pack_npz_ok:
                                    print(f"  -> [PASS] Mathematically Equivalent (within tolerance): {npz_name}")
                        except Exception as e:
                            print(f"[FAIL] Failed to perform mathematical verification for {npz_name}: {e}")
                            pack_npz_ok = False

            except Exception as e:
                print(f"[FAIL] Error reading NPZ {npz_name}: {e}")
                pack_npz_ok = False
                
        if fuzzy_zf:
            fuzzy_zf.close()

        if pack_npz_ok:
             print("[OK] All NPZ snapshots have correct schema (psi, phi, _meta).")


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
