import subprocess
from pathlib import Path

def test_no_untracked_files_in_root():
    root = Path(__file__).resolve().parent.parent
    result = subprocess.run(["git", "ls-files", "--others", "--exclude-standard"], cwd=root, capture_output=True, text=True)
    
    assert result.returncode == 0, f"Git command failed: {result.stderr}"
    
    untracked_files = [f for f in result.stdout.splitlines() if f.strip() and not "/" in f and not f.startswith("temp/")]
    
    assert len(untracked_files) == 0, f"Found untracked files in root: {untracked_files}. Please move them to temp/ or add to .gitignore."
