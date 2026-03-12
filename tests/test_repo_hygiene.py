import subprocess
from pathlib import Path

def test_no_untracked_files_in_root():
    root = Path(__file__).resolve().parent.parent
    result = subprocess.run(["git", "ls-files", "--others", "--exclude-standard"], cwd=root, capture_output=True, text=True)
    
    assert result.returncode == 0, f"Git command failed: {result.stderr}"
    
    untracked_files = [f for f in result.stdout.splitlines() if f.strip() and not "/" in f and not f.startswith(".scratch/")]
    
    assert len(untracked_files) == 0, f"Found untracked files in root: {untracked_files}. Please move them to .scratch/ or add to .gitignore."

def test_no_forbidden_tracked_files():
    """
    Ensures that temporary scripts, scratch files, and debug outputs
    are not accidentally tracked in the git repository.
    """
    root = Path(__file__).resolve().parent.parent
    result = subprocess.run(["git", "ls-files"], cwd=root, capture_output=True, text=True)
    
    assert result.returncode == 0, f"Git command failed: {result.stderr}"
    
    tracked_files = [f.strip() for f in result.stdout.splitlines() if f.strip()]
    
    forbidden_patterns = [
        "debug_out.txt",
        "debug_valid.txt",
        "pytest_output.txt",
        "validation_errors.txt",
        "test_output.json",
        "test_output2.json",
        "fix_czech_claim.js",
        "clean_whitepaper_map.js",
        "add_claim_036.js"
    ]

    violations = []
    for file in tracked_files:
        for pattern in forbidden_patterns:
            if pattern in file.lower():
                violations.append(file)
                break

    if violations:
        assert False, f"Repository hygiene test failed. 🚨 Forbidden artifacts are tracked in git:\n" + "\n".join(violations) + "\nRemove them using `git rm --cached <file>` and add them to .gitignore or .scratch/."

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

def test_no_duplicate_whitepaper_numbers():
    """Ensures that no two whitepapers in the same category directory share the same numerical prefix."""
    root = Path(__file__).resolve().parent.parent
    wp_dir = root / "whitepapers"
    
    if not wp_dir.exists():
        return
        
    for category_dir in wp_dir.iterdir():
        if not category_dir.is_dir():
            continue
            
        hypotheses_dir = category_dir / "hypotheses"
        if not hypotheses_dir.exists():
            continue
            
        seen_numbers = {}
        for md_file in hypotheses_dir.glob("*.md"):
            name = md_file.name
            # Extract the leading number, e.g. "35" from "35-cosmo-hyp-neural-resonance.md"
            parts = name.split('-')
            if parts and parts[0].isdigit():
                num = int(parts[0])
                if num in seen_numbers:
                    assert False, f"DUPLICATE WHITEPAPER NUMBER DETECTED in {category_dir.name}: #{num}\nFiles: {seen_numbers[num]} AND {name}"
                seen_numbers[num] = name
