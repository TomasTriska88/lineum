#!/usr/bin/env python3
import sys
import subprocess
from pathlib import Path

# Paths
TOOLS_DIR = Path(__file__).parent
RUNNER_SCRIPT = TOOLS_DIR / "whitepaper_contract.py"
PROJECT_ROOT = TOOLS_DIR.parent
DOCS_PATH = PROJECT_ROOT / "portal" / "src" / "lib" / "data" / "docs" / "whitepaper-contract.md"

MARKER_START = "<!-- CLI_DOC_START -->"
MARKER_END = "<!-- CLI_DOC_END -->"

def main():
    print("Checking documentation consistency...")
    
    # 1. Get canonical doc block from runner
    try:
        result = subprocess.run(
            [sys.executable, str(RUNNER_SCRIPT), "--print-doc-block"],
            capture_output=True,
            text=True,
            check=True
        )
        canonical_doc = result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error running {RUNNER_SCRIPT} --print-doc-block")
        print(e.stderr)
        sys.exit(2)

    # 2. Read existing documentation
    if not DOCS_PATH.exists():
        print(f"Error: Docs not found at {DOCS_PATH}")
        sys.exit(2)
        
    with open(DOCS_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    # 3. Extract block
    start_idx = content.find(MARKER_START)
    end_idx = content.find(MARKER_END)
    
    if start_idx == -1 or end_idx == -1:
        print(f"Error: Markers {MARKER_START} or {MARKER_END} not found in {DOCS_PATH}")
        sys.exit(2)
        
    # Content between markers
    current_doc_block = content[start_idx + len(MARKER_START):end_idx].strip()
    
    # 4. Compare
    # Normalize newlines just in case
    canonical_doc = canonical_doc.replace("\r\n", "\n")
    current_doc_block = current_doc_block.replace("\r\n", "\n")
    
    if canonical_doc == current_doc_block:
        print("PASS: Documentation matches CLI output.")
        sys.exit(0)
    else:
        print("FAIL: Documentation drift detected!")
        print("-" * 20 + " Expected " + "-" * 20)
        print(canonical_doc)
        print("-" * 20 + " Actual " + "-" * 20)
        print(current_doc_block)
        print("-" * 50)
        print(f"To fix, copy the output of 'python tools/whitepaper_contract.py --print-doc-block' into {DOCS_PATH} between the markers.")
        sys.exit(2)

if __name__ == "__main__":
    main()
