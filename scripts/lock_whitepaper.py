import sys
import os
import json
import hashlib
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path

def compute_sha256(filepath):
    h = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            h.update(chunk)
    return h.hexdigest()

def main():
    if len(sys.argv) < 2:
        print("Usage: python lock_whitepaper.py <path_to_whitepaper.md>")
        sys.exit(1)
        
    wp_path = sys.argv[1]
    if not os.path.exists(wp_path) or not wp_path.endswith('.md'):
        print(f"Error: {wp_path} not found or not a markdown file.")
        sys.exit(1)
        
    with open(wp_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Extract version
    version_match = re.search(r'\*\*Version:\*\*\s*(.+)', content)
    if not version_match:
        print(f"Error: Could not find '**Version:**' string in {wp_path}.")
        sys.exit(1)
    
    version_str = version_match.group(1).strip()
    
    # Create releases directory
    releases_dir = os.path.join(os.path.dirname(wp_path), "releases")
    os.makedirs(releases_dir, exist_ok=True)
    
    # Construct new snapshot filename
    base_name = os.path.splitext(os.path.basename(wp_path))[0]
    snapshot_filename = f"{base_name}-{version_str}-FROZEN.md"
    snapshot_path = os.path.join(releases_dir, snapshot_filename)
    
    # Update status to Frozen in the snapshot content
    if '**Status:**' in content:
        content = re.sub(r'\*\*Status:\*\*\s*.*', '**Status:** Frozen', content)
    elif '> **Document Status:**' in content:
        content = re.sub(r'> \*\*Document Status:\*\*.*', '> **Document Status:** Frozen', content)
    else:
        content = re.sub(r'^(# .*?\n)', r'\1\n**Status:** Frozen\n', content, count=1)
            
    with open(snapshot_path, 'w', encoding='utf-8') as f:
        f.write(content)
        
    # Compute hash of the snapshot
    file_hash = compute_sha256(snapshot_path)
    lock_path = snapshot_path + '._LOCK.json'
    
    lock_data = {
        "whitepaper_file": snapshot_filename,
        "sha256": file_hash,
        "locked_at": datetime.now(timezone.utc).isoformat(),
        "status": "frozen",
        "version": version_str
    }
    
    with open(lock_path, 'w', encoding='utf-8') as f:
        json.dump(lock_data, f, indent=2)
        
    print(f"Snapshot created: {snapshot_path}")
    print(f"Lock file created: {lock_path}")
    print(f"SHA256: {file_hash}")

if __name__ == '__main__':
    main()
