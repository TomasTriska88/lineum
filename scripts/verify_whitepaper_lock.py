import sys
import os
import json
import hashlib
import glob

def compute_sha256(filepath):
    h = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            h.update(chunk)
    return h.hexdigest()

def verify_locks(whitepapers_dir):
    lock_files = glob.glob(os.path.join(whitepapers_dir, '*.lock.json'))
    
    if not lock_files:
        print("No whitepaper locks found.")
        return True
        
    all_valid = True
    for lock_path in lock_files:
        with open(lock_path, 'r', encoding='utf-8') as f:
            lock_data = json.load(f)
            
        wp_file = lock_data.get('whitepaper_file')
        expected_hash = lock_data.get('sha256')
        
        wp_path = os.path.join(whitepapers_dir, wp_file)
        if not os.path.exists(wp_path):
            print(f"FAIL: Locked whitepaper {wp_file} is missing.")
            all_valid = False
            continue
            
        actual_hash = compute_sha256(wp_path)
        if actual_hash != expected_hash:
            print(f"FAIL: Whitepaper {wp_file} has been tampered with or modified. Expected SHA256 {expected_hash}, got {actual_hash}.")
            all_valid = False
        else:
            print(f"PASS: Whitepaper {wp_file} matches locked SHA256.")
            
    return all_valid

def main():
    root = 'whitepapers' if len(sys.argv) < 2 else sys.argv[1]
    if not os.path.exists(root):
        print(f"Error: directory {root} not found.")
        sys.exit(1)
        
    is_valid = verify_locks(root)
    if not is_valid:
        sys.exit(1)
    print("All locked whitepapers are verified successfully.")
    
if __name__ == '__main__':
    main()
