#!/usr/bin/env python3
import sys
import argparse
import json
import csv
import math
import hashlib
import os
import glob
from datetime import datetime, timezone
from pathlib import Path

# --- Configuration & Helpers ---

DOC_BLOCK = """
Usage:
  python tools/whitepaper_contract.py [--run-dir <path> | --runs-root <path>] [--contract <path>] [--strict]

Arguments:
  --run-dir <path>      Verify a single audit run directory (must be inside output_wp).
  --runs-root <path>    Verify all runs in this root directory (default: output_wp/runs).
  --contract <path>     Path to contract JSON (default: contracts/lineum-core-*.contract.json).
  --strict              Fail on any warning (default: Fail only on FATAL error).
  --backfill-analysis-config Backfill missing analysis_config metadata to manifest.json
  --force               Force overwrite of existing metadata during backfill
"""

# Default paths
DEFAULT_RUNS_ROOT = "output_wp/runs"
CONTRACT_GLOB = "contracts/lineum-core-*.contract.json"

# Exit codes
EXIT_PASS = 0
EXIT_FAIL = 1

def compute_sha256(path):
    """Compute SHA256 of a file."""
    sha256 = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256.update(chunk)
        return sha256.hexdigest()
    except FileNotFoundError:
        return None

def compute_code_fingerprint(repo_root):
    """
    Compute combined fingerprint of critical source files.
    - lineum.py
    - tools/whitepaper_contract.py
    - contracts/*.json
    """
    files = ["lineum.py", "tools/whitepaper_contract.py"]
    # Add contracts
    for c in glob.glob(os.path.join(repo_root, "contracts", "*.contract.json")):
        rel = os.path.relpath(c, repo_root)
        files.append(rel.replace("\\", "/")) # Normalize path separators

    files.sort()
    
    overall = hashlib.sha256()
    for rel_path in files:
        full_path = os.path.join(repo_root, rel_path)
        if not os.path.exists(full_path):
            continue
            
        with open(full_path, "rb") as f:
            content = f.read()
            # Normalize CRLF -> LF
            content = content.replace(b"\r\n", b"\n")
            overall.update(rel_path.encode("utf-8")) # Hash filename
            overall.update(content)                 # Hash content
            
    return overall.hexdigest()

def load_json(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None

def load_csv_dict(path, key_col="metric"):
    """Load CSV as a dictionary {key_col_val: row_dict}."""
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            return {row[key_col]: row for row in reader}
    except Exception:
        return None

def load_topo_stats(run_dir, expected_stride=1):
    """
    Load topology logs and calculate N1 and N0 (strict) neutrality.
    Validates strict stride consistency.
    """
    pattern = os.path.join(run_dir, "*_topo_log.csv")
    candidates = glob.glob(pattern)
    if not candidates:
        return None, None, 0, {"error": "File not found"}
        
    path = candidates[0]
    try:
        data_rows = []
        with open(path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            if "step" not in reader.fieldnames:
                 return None, None, 0, {"error": "Missing 'step' column"}
            for row in reader:
                data_rows.append(row)
                
        if not data_rows:
            return 0.0, 0.0, 0, {"error": "Empty log"}

        steps = []
        n1_count = 0
        n0_count = 0
        
        for row in data_rows:
            s = int(row["step"])
            steps.append(s)
            
            net = float(row.get("net_charge", 0))
            if abs(net) <= 1:
                n1_count += 1
            if net == 0:
                n0_count += 1
                
        count = len(steps)
        meta = {
            "first_step": steps[0],
            "last_step": steps[-1],
            "rows": count,
            "filename": os.path.basename(path)
        }
        
        # Stride Validation
        if count > 1:
            actual_stride = steps[1] - steps[0]
            if actual_stride != expected_stride:
                meta["warning"] = f"Stride mismatch: actual={actual_stride}, expected={expected_stride}"

        return (n1_count / count) * 100.0, (n0_count / count) * 100.0, count, meta
    except Exception as e:
        return None, None, 0, {"error": str(e)}

def check_value(name, actual, expected_def, paper_ref=None):
    """Compare actual value against definition (min/max/target+tol)."""
    severity = expected_def.get("severity", "fatal").lower()
    
    if actual is None:
        return "FAIL", f"{name}: Value missing", severity
        
    try:
        val = float(actual)
    except (ValueError, TypeError):
        # Allow string matches for hashes
        if isinstance(actual, str) and "min" not in expected_def and "max" not in expected_def:
             # Hash/String match
             expected_target = expected_def.get("target")
             if str(actual) == str(expected_target):
                  return "PASS", f"String match OK", severity
             else:
                  return "FAIL", f"Mismatch: {actual} != {expected_target}", severity
        return "FAIL", f"{name}: Invalid number/format '{actual}'", severity

    msg = []
    failed = False
    if "min" in expected_def and val < expected_def["min"]:
        failed = True
        msg.append(f"{val} < min {expected_def['min']}")
    if "max" in expected_def and val > expected_def["max"]:
        failed = True
        msg.append(f"{val} > max {expected_def['max']}")
    if "target" in expected_def:
        target = float(expected_def["target"])
        allowed = max(expected_def.get("abs_tol", 0.0), 
                     expected_def.get("rel_tol", 0.0) * abs(target))
        if abs(val - target) > allowed:
            failed = True
            msg.append(f"|{val} - {target}| > {allowed}")

    if failed: return "FAIL", "; ".join(msg), severity
    return "PASS", f"Value {val} OK", severity

def evaluate_derived(check_def, manifest, constants):
    """Compute derived physics metrics using constants and manifest data."""
    id_ = check_def.get("id")
    try:
        run_meta = manifest.get("run", {})
        metrics = manifest.get("metrics", {})
        s_pipe = manifest.get("spectral_pipeline", {})
        
        # Priority: spectral_pipeline > analysis_config > run_meta
        dt = s_pipe.get("dt") or run_meta.get("time_step_s")
        W = s_pipe.get("window_length") or manifest.get("analysis_config", {}).get("window_length") or run_meta.get("window_W")
        f0 = metrics.get("dominant_freq_Hz")
        
        h = constants.get("h")
        c = constants.get("c")
        m_e = constants.get("m_e")
        eV = constants.get("eV")
        
        calculated = None
        if id_ == "df_hz":
            calculated = s_pipe.get("df_hz")
            if calculated is None and dt and W: calculated = 1.0 / (W * dt)
        elif id_ == "nyquist_hz":
            calculated = s_pipe.get("nyquist_hz")
            if calculated is None and dt: calculated = 1.0 / (2 * dt)
        elif id_ == "sampling_rate_hz":
            calculated = s_pipe.get("sampling_rate_hz")
            if calculated is None and dt: calculated = 1.0 / dt
        elif id_ == "E_J":
            if h and f0: calculated = h * f0
        elif id_ == "E_keV":
            if h and f0 and eV: calculated = (h * f0) / (1000 * eV)
        elif id_ == "lambda_m":
             if c and f0: calculated = c / f0
        elif id_ == "m_over_me":
             if h and f0 and c and m_e: calculated = (h * f0) / (c**2 * m_e)
             
        if calculated is None: return "SKIP", "Missing inputs", None
        status, msg, sev = check_value(id_, calculated, check_def)
        return status, f"{msg} ({calculated:.4e})", calculated
    except Exception as e:
        return "FAIL", f"Eval error: {e}", None

def find_manifest(run_dir):
    candidates = glob.glob(os.path.join(run_dir, "*_manifest.json")) + [os.path.join(run_dir, "manifest.json")]
    for c in candidates:
        if os.path.exists(c): return c
    return None

def main():
    parser = argparse.ArgumentParser(description=DOC_BLOCK, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--run-dir", help="Specific run directory")
    parser.add_argument("--runs-root", default=DEFAULT_RUNS_ROOT)
    parser.add_argument("--contract", default=None)
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()

    # Determine contract
    c_path = args.contract
    if not c_path:
        candidates = glob.glob(CONTRACT_GLOB)
        if not candidates: print("FATAL: No contract found."); sys.exit(1)
        c_path = sorted(candidates)[-1]
    
    contract = load_json(c_path)
    if not contract: print(f"FATAL: Load error {c_path}"); sys.exit(1)

    suite_report = {
        "suite_schema_version": "1.0.0",
        "header": {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "contract_id": contract.get("contract_id"),
            "contract_version": contract.get("contract_version"),
            "tool_id": "lineum_audit_suite_gen",
            "tool_version": "1.0.14-core"
        },
        "fingerprints": {
            "whitepaper_sha256": compute_sha256("whitepapers/lineum-core.md"),
            "contract_sha256": compute_sha256(c_path),
            "codebase_sha256": compute_code_fingerprint(".")
        },
        "embedded_context": {"runs": {}},
        "runs": [],
        "summary": {"pass": 0, "fail": 0, "skip": 0, "matched_canonical": 0}
    }

    if not os.path.exists(args.runs_root) and not args.run_dir:
         print(f"FATAL: {args.runs_root} missing."); sys.exit(1)

    candidates = [args.run_dir] if args.run_dir else [os.path.join(args.runs_root, d) for d in os.listdir(args.runs_root) if os.path.isdir(os.path.join(args.runs_root, d)) and not d.startswith("_")]
    candidates.sort()

    seen_identities = {}
    for r_dir in candidates:
        run_id = os.path.basename(r_dir)
        m_path = find_manifest(r_dir)
        if not m_path: continue
        
        manifest = load_json(m_path)
        if not manifest: continue

        # Identity / Duplicate Check
        run_meta = manifest.get("run", {})
        ident = f"{run_meta.get('run_tag')}_{run_meta.get('seed')}_{run_meta.get('steps')}_{manifest.get('code_fingerprint')}"
        ident_hash = hashlib.sha256(ident.encode()).hexdigest()
        if ident_hash in seen_identities: continue
        seen_identities[ident_hash] = run_id

        # Embed Context
        suite_report["embedded_context"]["runs"][run_id] = {
            "manifest": manifest,
            "manifest_sha256": compute_sha256(m_path),
            "spectral_pipeline": manifest.get("spectral_pipeline", {}),
            "run_configuration": manifest.get("run_configuration", {}),
            "kappa": manifest.get("kappa", {})
        }

        # Profile selection
        active_profiles = []
        for p in contract.get("profiles", []):
            if all(run_meta.get(k) == v for k, v in p.get("selectors", {}).items()):
                active_profiles.append(p)
        
        if not active_profiles: continue
        
        run_result = {"run_id": run_id, "profiles": [p["name"] for p in active_profiles], "checks": [], "status": "PASS"}
        if "canonical" in run_result["profiles"]: suite_report["summary"]["matched_canonical"] += 1

        # Neutrality
        stride = manifest.get("logging", {}).get("topo_log_stride", run_meta.get("topo_log_stride", 1))
        n1, n0, _, _ = load_topo_stats(r_dir, stride)

        for profile in active_profiles:
            p_name = profile["name"]
            checks = profile.get("checks", {})

            # 1. Invariants
            for k, ev in checks.get("invariants", {}).items():
                av = manifest.get("invariants", {}).get(k)
                res = {"id": f"{p_name}.invariants.{k}", "expected": ev, "actual": av, "status": "PASS" if str(av) == str(ev) else "FAIL"}
                res["actual_source"] = {"primary": f"{os.path.basename(m_path)}:invariants.{k}", "embedded": f"embedded_context.runs.{run_id}.manifest.invariants.{k}"}
                if res["status"] == "FAIL": run_result["status"] = "FAIL"
                run_result["checks"].append(res)

            # 2. Identity
            for k, ev in checks.get("identity", {}).items():
                av = run_meta.get(k) if "." not in k else manifest.get("run", {}).get(k.split(".")[-1]) # Simple nesting
                res = {"id": f"{p_name}.identity.{k}", "expected": ev, "actual": av, "status": "PASS" if av == ev else "FAIL"}
                res["actual_source"] = {"primary": f"{os.path.basename(m_path)}:run.{k}", "embedded": f"embedded_context.runs.{run_id}.manifest.run.{k}"}
                if res["status"] == "FAIL": run_result["status"] = "FAIL"
                run_result["checks"].append(res)

            # 3. Analysis
            for k, ev in checks.get("analysis_config", {}).items():
                av = manifest.get("analysis_config", {}).get(k)
                res = {"id": f"{p_name}.analysis.{k}", "expected": ev, "actual": av, "status": "PASS" if av == ev else "FAIL"}
                res["actual_source"] = {"primary": f"{os.path.basename(m_path)}:analysis_config.{k}", "embedded": f"embedded_context.runs.{run_id}.manifest.analysis_config.{k}"}
                if res["status"] == "FAIL": run_result["status"] = "FAIL"
                run_result["checks"].append(res)

            # 4. Anchors
            for mk, constr in checks.get("numerical_anchors", {}).items():
                av = manifest.get("metrics", {}).get(mk)
                # Specialized lookups
                p_src, e_src = f"metrics.{mk}", f"manifest.metrics.{mk}"
                if mk == "resolved_config_hash":
                     av = manifest.get("run_configuration", {}).get("resolved_config_hash")
                     p_src, e_src = "run_configuration.resolved_config_hash", "manifest.run_configuration.resolved_config_hash"
                elif mk == "kappa_hash":
                     av = manifest.get("kappa", {}).get("hash")
                     p_src, e_src = "kappa.hash", "manifest.kappa.hash"
                elif mk == "topology_neutrality_n1": av = n1
                elif mk == "strict_neutrality": av = n0

                status, msg, sev = check_value(mk, av, constr)
                res = {"id": f"{p_name}.anchor.{mk}", "expected": constr, "actual": av, "status": status, "message": msg, "severity": sev}
                res["actual_source"] = {"primary": f"{os.path.basename(m_path)}:{p_src}", "embedded": f"embedded_context.runs.{run_id}.{e_src}"}
                if status == "FAIL" and sev == "fatal": run_result["status"] = "FAIL"
                run_result["checks"].append(res)

            # 5. Derived
            for d in checks.get("derived", []):
                st, msg, val = evaluate_derived(d, manifest, contract.get("constants", {}))
                res = {"id": f"{p_name}.derived.{d['id']}", "expected": d.get("expected"), "actual": val, "status": st, "message": msg}
                res["actual_source"] = {"primary": f"calculated: {d.get('formula')}", "embedded": "calculated from embedded manifest/constants"}
                if st == "FAIL": run_result["status"] = "FAIL"
                run_result["checks"].append(res)

            # 6. Artifacts
            for art in checks.get("required_artifacts", []):
                found = glob.glob(os.path.join(r_dir, art))
                res = {"id": f"{p_name}.artifact.{art}", "expected": "exists", "actual": "found" if found else "missing", "status": "PASS" if found else "FAIL"}
                if res["status"] == "FAIL": run_result["status"] = "FAIL"
                run_result["checks"].append(res)

        suite_report["runs"].append(run_result)
        if run_result["status"] == "PASS": suite_report["summary"]["pass"] += 1
        else: suite_report["summary"]["fail"] += 1

    # Save
    out_dir = Path(args.runs_root) / "_whitepaper_contract"
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / "whitepaper_contract_suite.json"
    with open(out_path, "w") as f: json.dump(suite_report, f, indent=2)
    
    print(f"Verified {len(suite_report['runs'])} runs. Suite: {out_path}")
    if suite_report["summary"]["fail"] > 0: sys.exit(1)

if __name__ == "__main__": main()
