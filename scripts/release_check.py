import os
import sys
import json
import subprocess
from datetime import datetime

def run_command(cmd):
    try:
        return subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT).decode('utf-8').strip()
    except subprocess.CalledProcessError as e:
        return e.output.decode('utf-8').strip()

def check_release_readiness(prepare_tag=None):
    print("🚀 Running Lineum Release Readiness Check...")
    
    # 1. Clean Working Tree
    status = run_command("git status --porcelain")
    tree_clean = len(status) == 0
    print(f"[{'PASS' if tree_clean else 'FAIL'}] Working Tree Clean")

    # 2. Extract active audit context using the lab_api helper directly
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    sys.path.append(os.path.join(repo_root, "routing_backend"))
    try:
        from lab_api import _get_audit_context
        ctx = _get_audit_context()
    except Exception as e:
        print(f"[FAIL] Backend context unreachable: {e}")
        sys.exit(1)

    # 3. Audit Status Verification
    valid_statuses = ["AUDITED", "BUILD_NEWER"]
    audit_status = ctx.get("audit_status", "NONE")
    status_pass = audit_status in valid_statuses
    print(f"[{'PASS' if status_pass else 'FAIL'}] Audit Status: {audit_status}")

    # 4. Profile Verification
    active_profile = ctx.get("active_profile")
    profile_pass = active_profile == "whitepaper_core"
    print(f"[{'PASS' if profile_pass else 'FAIL'}] Target Profile: {active_profile}")

    # 5. Quarantine Check (No contamination)
    q_reg = os.path.join(repo_root, "output_wp", "archive", "quarantine", "_quarantine_registry.json")
    quarantine_clean = True
    quarantine_count = 0
    if os.path.exists(q_reg):
        try:
            with open(q_reg, 'r', encoding='utf-8') as f:
                q_data = json.load(f)
                quarantine_count = len(q_data.get("quarantined_directories", []))
                print(f"[INFO] Quarantine Archive holds {quarantine_count} tampered runs (isolated).")
        except:
            pass

    import requests
    try:
        res = requests.get("http://127.0.0.1:8000/api/claims")
        data = res.json()
        total_claims = len(data)
        supported = sum(1 for c in data if c.get("status") == "Supported")
        contradicted = sum(1 for c in data if c.get("status") == "Contradicted")
        empty = sum(1 for c in data if c.get("status") == "Untested")
        claims_summary = f"{supported} Supported, {contradicted} Contradicted, {empty} Untested (Total: {total_claims})"
    except:
        claims_summary = "Backend Unreachable"

    all_passed = tree_clean and status_pass and profile_pass

    if prepare_tag:
        preview = f"""# Release Candidate: {prepare_tag}

## Readiness Check
- **Working Tree Clean:** {'✅' if tree_clean else '❌'}
- **Audit Status:** {audit_status} {'✅' if status_pass else '❌'}
- **Active Profile:** {active_profile} 
- **Equation Fingerprint:** `{ctx.get('equation_fingerprint')}`
- **Quarantined Runs (Isolated):** {quarantine_count}

## Claims Summary
- {claims_summary}

## Git Commit
`{ctx.get('commit_hash', run_command("git rev-parse HEAD"))}`
"""
        out_path = os.path.join(repo_root, "_release_candidate_summary.md")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(preview)
        print(f"\n📄 Release Notes preview generated at: {_release_candidate_summary.md}")

    if not all_passed:
        print("\n❌ RELEASE READINESS FAILED. Fix the issues above before publishing.")
        sys.exit(1)
    
    print("\n✅ RELEASE READINESS PASSED.")
    sys.exit(0)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--prepare", type=str, help="Version tag to prepare")
    args = parser.parse_args()
    
    check_release_readiness(args.prepare)
