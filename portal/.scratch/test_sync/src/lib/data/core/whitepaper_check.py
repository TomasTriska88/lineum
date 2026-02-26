#!/usr/bin/env python3
import sys
import subprocess
import argparse
from pathlib import Path

# Paths
TOOLS_DIR = Path(__file__).parent
DOC_CHECK_SCRIPT = TOOLS_DIR / "check_whitepaper_docs.py"
RUNNER_SCRIPT = TOOLS_DIR / "whitepaper_contract.py"

def main():
    # Only parse known args to check if help is requested, otherwise pass everything to runner
    parser = argparse.ArgumentParser(description="Orchestrator for Whitepaper Contract Suite", add_help=False)
    parser.add_argument("--help", "-h", action="store_true")
    args, unknown = parser.parse_known_args()

    if args.help:
        print("Orchestrator for Whitepaper Contract Suite.")
        print("Usage: python tools/whitepaper_check.py [runner_args...]")
        print("\nFirst, checks documentation consistency.")
        print("Then, runs whitepaper_contract.py with provided arguments.")
        print("\nRunner Help:")
        subprocess.run([sys.executable, str(RUNNER_SCRIPT), "--help"])
        sys.exit(0)
    
    # 1. Run Documentation Consistency Check
    print("[Orchestrator] Checking documentation consistency...")
    try:
        subprocess.run(
            [sys.executable, str(DOC_CHECK_SCRIPT)],
            check=True
        )
    except subprocess.CalledProcessError:
        print("[Orchestrator] Documentation drift detected! Please update docs/whitepaper-contract.md.")
        sys.exit(2)
        
    # 2. Run Whitepaper Contract Suite
    print("[Orchestrator] Running Whitepaper Contract Suite...")
    
    cmd = [sys.executable, str(RUNNER_SCRIPT)]
    # Forward all original arguments (excluding script name)
    cmd.extend(sys.argv[1:])
    
    try:
        result = subprocess.run(cmd)
        sys.exit(result.returncode)
    except KeyboardInterrupt:
        sys.exit(130)

if __name__ == "__main__":
    main()
