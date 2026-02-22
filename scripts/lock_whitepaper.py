import sys
import os
import json
import hashlib
import re
from datetime import datetime, timezone

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
        
    # Make frozen state visible
    # We will look for an existing Status tag line or add one near the top.
    # lineum-core.md currently uses `> **Status tags (v1.0.17-core).**`
    # Let's insert a direct `> **Document Status:** Frozen` if not there.
    
    if '> **Document Status:** Frozen' not in content:
        if '> **Document Status:**' in content:
            content = re.sub(r'> \*\*Document Status:\*\*.*', '> **Document Status:** Frozen', content)
        else:
            # Insert after the first major title
            content = re.sub(r'^(# .*?\n)', r'\1\n> **Document Status:** Frozen\n', content, count=1)
            
        with open(wp_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
        print(f"Updated {wp_path} to Frozen status.")
        
    # Now compute hash
    file_hash = compute_sha256(wp_path)
    lock_path = wp_path + '.lock.json'
    
    lock_data = {
        "whitepaper_file": os.path.basename(wp_path),
        "sha256": file_hash,
        "locked_at": datetime.now(timezone.utc).isoformat(),
        "status": "frozen"
    }
    
    with open(lock_path, 'w', encoding='utf-8') as f:
        json.dump(lock_data, f, indent=2)
        
    print(f"Locked {wp_path}. Lock file created at {lock_path}")
    print(f"SHA256: {file_hash}")

if __name__ == '__main__':
    main()
