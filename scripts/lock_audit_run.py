import os
import sys
import glob
import json
import hashlib
import platform
import subprocess
from datetime import datetime, timezone

def compute_sha256(path):
    sha256 = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256.update(chunk)
    return sha256.hexdigest()

def lock_run(run_dir):
    if not os.path.isdir(run_dir):
        print(f"Directory {run_dir} does not exist.")
        sys.exit(1)
        
    lock_file = os.path.join(run_dir, "_LOCK.json")
    if os.path.exists(lock_file):
        print(f"Run {run_dir} is already locked.")
        sys.exit(0)
        
    all_files = []
    for root, _, files in os.walk(run_dir):
        for file in files:
            all_files.append(os.path.join(root, file))
            
    file_registry = {}
    for fpath in all_files:
        rel_path = os.path.relpath(fpath, run_dir).replace('\\', '/')
        file_registry[rel_path] = {
            "size": os.path.getsize(fpath),
            "sha256": compute_sha256(fpath)
        }
        
    run_id = os.path.basename(os.path.normpath(run_dir))
    
    suite_path = os.path.join(os.path.dirname(os.path.dirname(run_dir)), "_whitepaper_contract", "whitepaper_contract_suite.json")
    suite_sha256 = compute_sha256(suite_path) if os.path.exists(suite_path) else None
    
    lock_data = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "locked": True,
        "run_id": run_id,
        "file_count": len(file_registry),
        "suite_sha256": suite_sha256,
        "contract_id": "resolved_from_suite_or_manifest", # Could parse manifest if needed
        "files": file_registry
    }
    
    with open(lock_file, "w", encoding="utf-8") as f:
        json.dump(lock_data, f, indent=2)
        
    print(f"Created {lock_file} with {len(file_registry)} files.")
    
    # Apply filesystem protections
    if "--no-os-lock" not in sys.argv:
        if platform.system() == "Windows":
            try:
                subprocess.check_call(f'attrib +R "{run_dir}\\*" /S /D', shell=True)
                # Apply deny ACL for current user for Write, Modify, Delete Child
                username = os.environ.get("USERNAME")
                if username:
                    subprocess.check_call(f'icacls "{run_dir}" /deny "{username}":(OI)(CI)(W,M,DC)', shell=True)
                print("Windows filesystem protections applied (attrib +R and icacls deny).")
            except subprocess.CalledProcessError as e:
                print(f"Failed to apply Windows permissions: {e}")
        else:
            try:
                subprocess.check_call(['chmod', '-R', 'a-w', run_dir])
                print("POSIX filesystem protections applied (chmod -R a-w).")
            except subprocess.CalledProcessError as e:
                print(f"Failed to apply POSIX permissions: {e}")
    else:
        print("Skipped OS-level filesystem protections (--no-os-lock).")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python lock_audit_run.py <path_to_run_dir> [--no-os-lock]")
        sys.exit(1)
    
    target_dir = sys.argv[1]
    if target_dir == "--no-os-lock" and len(sys.argv) > 2:
        target_dir = sys.argv[2]
        
    lock_run(target_dir)
