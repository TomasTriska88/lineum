import subprocess
from pathlib import Path

def test_no_untracked_files_in_root():
    root = Path(__file__).resolve().parent.parent
    result = subprocess.run(["git", "ls-files", "--others", "--exclude-standard"], cwd=root, capture_output=True, text=True)
    
    assert result.returncode == 0, f"Git command failed: {result.stderr}"
    
    untracked_files = [f for f in result.stdout.splitlines() if f.strip() and not "/" in f and not f.startswith(".scratch/")]
    
    assert len(untracked_files) == 0, f"Found untracked files in root: {untracked_files}. Please move them to .scratch/ or add to .gitignore."

def test_critical_files_exist():
    """Ensures that the project's key configuration files have not been accidentally deleted."""
    root = Path(__file__).resolve().parent.parent
    critical_files = [
        # Root configs
        "package.json",
        "requirements.txt",
        ".gitignore",
        "pytest.ini",
        "README.md",
        
        # Sub-projects
        "lab/package.json",
        "portal/package.json",
        
        # Important infrastructure
        "scripts/check-czech.mjs",
        "helpers/check-czech-lib.js"
    ]
    
    for relative_path in critical_files:
        file_path = root / relative_path
        assert file_path.exists(), f"CRITICAL FILE MISSING: {relative_path}. This file must never be deleted!"
