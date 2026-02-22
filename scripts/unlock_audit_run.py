import os
import sys
import platform
import subprocess

def unlock_run(run_dir):
    if not os.path.isdir(run_dir):
        print(f"Directory {run_dir} does not exist.")
        sys.exit(1)
        
    lock_file = os.path.join(run_dir, "_LOCK.json")
    
    print("WARNING: You are unlocking an audit run. Modifying this run invalidates its evidentiary status.")
    print("If you change variables, you MUST generate a new run. Locked runs are considered read-only canonical data.")
    
    if platform.system() == "Windows":
        try:
            username = os.environ.get("USERNAME")
            if username:
                subprocess.check_call(f'icacls "{run_dir}" /remove:d "{username}" /T', shell=True)
            subprocess.check_call(f'attrib -R "{run_dir}\\*" /S /D', shell=True)
            print("Windows filesystem protections removed.")
        except subprocess.CalledProcessError as e:
            print(f"Failed to remove Windows permissions: {e}")
    else:
        try:
            subprocess.check_call(['chmod', '-R', 'u+w', run_dir])
            print("POSIX filesystem protections removed.")
        except subprocess.CalledProcessError as e:
            print(f"Failed to remove POSIX permissions: {e}")
            
    if os.path.exists(lock_file):
        os.remove(lock_file)
        print(f"Removed {lock_file}.")
        
    print(f"Run {run_dir} is now unlocked.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python unlock_audit_run.py <path_to_run_dir>")
        sys.exit(1)
    unlock_run(sys.argv[1])
