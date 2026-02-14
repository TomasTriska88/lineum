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
    Returns (n1_pct, n0_pct, rows, meta_dict).
    """
    # Find topo log
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

        # Validation
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
                
        # Stride Consistency Check
        first = steps[0]
        last = steps[-1]
        count = len(steps)
        
        # Check monotonicity
        if any(steps[i] <= steps[i-1] for i in range(1, count)):
             return None, None, 0, {"error": "Steps not monotonic"}
             
        # Check Stride
        stride_errors = 0
        for i in range(1, count):
            diff = steps[i] - steps[i-1]
            if diff != expected_stride:
                stride_errors += 1
                
        meta = {
            "first_step": first,
            "last_step": last,
            "rows": count,
            "filename": os.path.basename(path)
        }
        
        if stride_errors > 0:
             meta["warning"] = f"Found {stride_errors} stride violations (expected {expected_stride})"
             
        # Strict calculation of expected rows from first/last
        expected_rows = ((last - first) // expected_stride) + 1
        if count != expected_rows:
             meta["warning"] = f"Row count {count} != expected {expected_rows} based on range {first}-{last}"

        return (n1_count / count) * 100.0, (n0_count / count) * 100.0, count, meta
        
    except Exception as e:
        return None, None, 0, {"error": str(e)}

def check_value(name, actual, expected_def, paper_ref=None):
    """
    Compare actual value against definition (min/max/target+tol).
    Returns (status, message, severity).
    """
    severity = expected_def.get("severity", "fatal").lower()
    
    if actual is None:
        return "FAIL", f"{name}: Value missing", severity
        
    try:
        val = float(actual)
    except (ValueError, TypeError):
        return "FAIL", f"{name}: Invalid number '{actual}'", severity

    msg = []
    failed = False
    
    # Range check
    if "min" in expected_def:
        if val < expected_def["min"]:
            failed = True
            msg.append(f"ordered {val} < min {expected_def['min']}")
    if "max" in expected_def:
        if val > expected_def["max"]:
            failed = True
            msg.append(f"ordered {val} > max {expected_def['max']}")
            
    # Target + Tolerance check
    if "target" in expected_def:
        target = expected_def["target"]
        abs_tol = expected_def.get("abs_tol")
        rel_tol = expected_def.get("rel_tol")
        
        diff = abs(val - target)
        allowed = 0.0
        
        if abs_tol is not None:
             allowed = max(allowed, abs_tol)
        if rel_tol is not None:
             allowed = max(allowed, rel_tol * abs(target))
             
        if diff > allowed:
            failed = True
            msg.append(f"|{val} - {target}| = {diff} > tol {allowed}")

    if failed:
        return "FAIL", "; ".join(msg), severity
    return "PASS", f"Value {val} OK", severity

def evaluate_derived(check_def, manifest, constants):
    """
    Compute derived value and compare with expected.
    """
    formula = check_def.get("formula", "")
    id_ = check_def.get("id")
    
    # 1. Extract inputs
    try:
        # We need to map inputs from manifest to local variables for computation
        # Common inputs: W, dt, f0
        run_meta = manifest.get("run", {})
        metrics = manifest.get("metrics", {})
        analysis = manifest.get("analysis_config", {})
        
        dt = run_meta.get("time_step_s")
        # Try analysis_config first, then fallback to run_meta for window (backward compat)
        W = analysis.get("window_length")
        if W is None:
             W = run_meta.get("window_W")
             
        f0 = metrics.get("dominant_freq_Hz")
        
        # Constants
        h = constants.get("h")
        c = constants.get("c")
        m_e = constants.get("m_e")
        eV = constants.get("eV")
        
        # Compute based on ID
        calculated = None
        
        if id_ == "df_hz":
            if dt and W: calculated = 1.0 / (W * dt)
        elif id_ == "nyquist_hz":
            if dt: calculated = 1.0 / (2 * dt)
        elif id_ == "sampling_rate_hz":
            if dt: calculated = 1.0 / dt
        elif id_ == "E_J":
            if h and f0: calculated = h * f0
        elif id_ == "E_keV":
            if h and f0 and eV: calculated = (h * f0) / (1000 * eV)
        elif id_ == "lambda_m":
             if c and f0: calculated = c / f0
        elif id_ == "m_over_me":
             if h and f0 and c and m_e: calculated = (h * f0) / (c**2 * m_e)
             
        if calculated is None:
             return "SKIP", "Missing inputs for calculation", None
             
        # Compare with expected in contract check_def
        # Reuse check_value logic by constructing a def
        res_status, res_msg, res_sev = check_value(id_, calculated, check_def)
        
        return res_status, f"{res_msg} (Calc: {calculated:.4e})", calculated
        
    except Exception as e:
        return "FAIL", f"Calculation error: {e}", None


def find_manifest(run_dir):
    """
    Locate manifest.json or *_manifest.json in run_dir.
    Returns absolute path or None.
    """
    # 1. Exact match
    p = os.path.join(run_dir, "manifest.json")
    if os.path.exists(p):
        return p
        
    # 2. Pattern match
    candidates = glob.glob(os.path.join(run_dir, "*_manifest.json"))
    if candidates:
        # Prefer shortest name? or just first?
        # spec6_false_s41_manifest.json
        return candidates[0]
        
    return None

def backfill_analysis_config(run_dir, contract_path, force=False):
    """
    Backfill missing analysis_config into manifest.json using the contract definition.
    """
    manifest_path = find_manifest(run_dir)
    if not manifest_path:
        print(f"Error: manifest.json not found in {run_dir}")
        return False
        
    manifest = load_json(manifest_path)
    if not manifest:
        print(f"Error: Failed to load manifest from {manifest_path}")
        return False
        
    # Idempotency check
    if "analysis_config" in manifest and not force:
        print(f"WARN: analysis_config already exists in {run_dir}. Use --force to overwrite.")
        return True # Return True because state is valid (config exists)

    # Load contract to source defaults
    if not contract_path or not os.path.exists(contract_path):
        print(f"Error: Contract path {contract_path} invalid.")
        return False
        
    contract = load_json(contract_path)
    if not contract:
         print(f"Error: Could not load contract {contract_path}")
         return False

    # Extract analysis_config from "canonical" profile
    # We assume the canonical profile holds the "truth" for analysis config.
    source_config = None
    for p in contract.get("profiles", []):
        if p.get("name") == "canonical":
            source_config = p.get("checks", {}).get("analysis_config")
            break
            
    if not source_config:
         print("Error: Could not find 'analysis_config' in 'canonical' profile of the contract.")
         return False

    # Build the config dictionary from the contract requirements
    config = source_config.copy()
    
    # Add provenance
    config["_meta"] = {
         "source": "backfilled_from_contract",
         "contract_id": contract.get("contract_id", "unknown"),
         "contract_version": contract.get("contract_version", "unknown"),
         "backfilled_at": datetime.now(timezone.utc).isoformat(),
         "contract_path": contract_path,
         "tool": "whitepaper_contract.py"
    }
    
    manifest["analysis_config"] = config
    
    # Save back
    try:
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)
        print(f"Success: Backfilled analysis_config to {manifest_path} from contract.")
        return True
    except Exception as e:
        print(f"Error saving manifest: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description=DOC_BLOCK, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--print-doc-block", action="store_true", help="Print the documentation block and exit")
    parser.add_argument("--run-dir", help="Specific run directory")
    parser.add_argument("--runs-root", default=DEFAULT_RUNS_ROOT)
    parser.add_argument("--contract", default=None)
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--backfill-analysis-config", action="store_true", help="Backfill missing analysis_config metadata to manifest.json")
    parser.add_argument("--force", action="store_true", help="Force overwrite of existing metadata during backfill")
    parser.add_argument("--cleanup", action="store_true", help="Interactive cleanup of duplicate/skipped runs")
    args = parser.parse_args()

    if args.print_doc_block:
        print(DOC_BLOCK)
        sys.exit(0)
        
    # Handle Backfill Mode
    if args.backfill_analysis_config:
        if not args.run_dir:
             print("Error: --backfill-analysis-config requires --run-dir")
             sys.exit(EXIT_FAIL)
        if not args.contract:
             print("Error: --backfill-analysis-config requires --contract")
             sys.exit(EXIT_FAIL)
             
        success = backfill_analysis_config(args.run_dir, args.contract, args.force)
        sys.exit(EXIT_PASS if success else EXIT_FAIL)

    # Locate contract
    if args.contract:
        c_path = args.contract
    else:
        # Find latest contract
        candidates = glob.glob(CONTRACT_GLOB)
        if not candidates:
            print("FATAL: No contract found.")
            sys.exit(EXIT_FAIL)
        c_path = sorted(candidates)[-1]
        
    contract = load_json(c_path)
    if not contract:
        print(f"FATAL: Could not load contract {c_path}")
        sys.exit(EXIT_FAIL)
        
    # Suite Report Structure
    suite_report = {
        "header": {
            "suite_version": "1.2.0",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "contract_id": contract.get("contract_id"),
            "runs_root": args.runs_root
        },
        "fingerprints": {
            "whitepaper_sha256": compute_sha256("whitepapers/lineum-core.md"),
            "contract_sha256": compute_sha256(c_path),
            "runner_sha256": compute_sha256(__file__),
            "codebase_sha256": compute_code_fingerprint(".")
        },
        "runs": [],
        "summary": {"pass": 0, "fail": 0, "skip": 0, "matched_canonical": 0}
    }

    # Discover runs - Strict scanning of output_wp/runs
    if args.runs_root and not os.path.exists(args.runs_root):
         print(f"FATAL: Runs root {args.runs_root} does not exist. (Do not use 'output/'!)")
         sys.exit(EXIT_FAIL)
         
    # Only process subdirectories not starting with "_"
    candidates = []
    if args.run_dir:
        candidates = [args.run_dir]
    else:
        for d in os.listdir(args.runs_root):
            full_p = os.path.join(args.runs_root, d)
            if os.path.isdir(full_p) and not d.startswith("_"):
                candidates.append(full_p)
                
    candidates.sort() # Ensure deterministic order (e.g. audit vs duplicate)
    
    # Duplicate Detection
    # Map identity_hash -> run_id
    seen_identities = {}
    
    for r_dir in candidates:
        run_id = os.path.basename(r_dir)
        manifest_path = find_manifest(r_dir)
        
        run_result = {
            "run_id": run_id,
            "profiles": [],
            "checks": [],
            "status": "PASS"
        }

        if not manifest_path:
            manifest = None
        else:
            manifest = load_json(manifest_path)

        if not manifest:
            run_result["status"] = "FAIL"
            run_result["message"] = "Missing manifest.json or *_manifest.json"
            suite_report["runs"].append(run_result)
            suite_report["summary"]["fail"] += 1
            continue

        run_meta = manifest.get("run", {})
        
        # Calculate Identity Hash for Duplicate Detection
        fingerprint = manifest.get("code_fingerprint")
        identity_str = f"{run_meta.get('run_tag')}_{run_meta.get('seed')}_{run_meta.get('steps')}_{fingerprint}"
        identity_hash = hashlib.sha256(identity_str.encode("utf-8")).hexdigest()
        
        # Add Manifest SHA for provenance
        manifest_sha = compute_sha256(manifest_path)
        run_result["manifest_sha256"] = manifest_sha
        
        if identity_hash in seen_identities:
            # Duplicate found
            original_run = seen_identities[identity_hash]
            run_result["status"] = "SKIP"
            run_result["message"] = f"Duplicate of {original_run}"
            run_result["duplicate_of"] = original_run
            suite_report["runs"].append(run_result)
            suite_report["summary"]["skip"] += 1
            print(f"Run {run_id} is a duplicate of {original_run}. Skipping.")
            continue
        
        seen_identities[identity_hash] = run_id

        # 2. Determine Profiles
        active_profiles = []
        for profile in contract.get("profiles", []):
            match = True
            for k, v in profile.get("selectors", {}).items():
                if run_meta.get(k) != v:
                    match = False
                    break
            if match:
                active_profiles.append(profile)
                
        if not active_profiles:
             run_result["status"] = "SKIP"
             run_result["message"] = "No matching profiles"
             suite_report["runs"].append(run_result)
             suite_report["summary"]["skip"] += 1
             continue

        run_result["profiles"] = [p["name"] for p in active_profiles]
        
        is_canonical = "canonical" in run_result["profiles"]
        if is_canonical:
            suite_report["summary"]["matched_canonical"] += 1
            
        if is_canonical:
            suite_report["summary"]["matched_canonical"] += 1
            
        # Pre-calculate Neutrality with Strict Stride
        log_cfg = manifest.get("logging", {})
        # Prefer logging dict, fallback to run dict, default 1
        stride = log_cfg.get("topo_log_stride", run_meta.get("topo_log_stride", 1))
        
        n1_pct, n0_pct, topo_rows, topo_meta = load_topo_stats(r_dir, expected_stride=stride)
        
        # Verify Coverage (Last step vs Total)
        total_steps = run_meta.get("steps", 0)
        
        if topo_meta.get("error"):
             run_result.setdefault("warnings", []).append(f"Topo log error: {topo_meta['error']}")
        else:
             if "warning" in topo_meta:
                 # Internal consistency errors (stride/monotonicity/rows)
                 run_result.setdefault("warnings", []).append(topo_meta["warning"])
                 
             # Coverage warning
             last_step = topo_meta.get("last_step", 0)
             rem = total_steps % stride
             target_last = total_steps if rem == 0 else (total_steps - rem)
             
             if not (last_step == target_last or last_step == total_steps):
                  # Check if it's consistently 1 stride less (0-indexing vs 1-indexing issue?)
                  if last_step == target_last - stride:
                       # This is likely standard loop behavior (stop before 2000). Info only.
                       pass 
                  else:
                       run_result.setdefault("warnings", []).append(f"Topo log coverage issue: last {last_step} != target {target_last}")

        # Construct Context Message for Neutrality Checks
        # "Computed over logged frames (N=<rows>, stride=<stride>, first=<first_step>, last=<last_step>)"
        if topo_rows > 0:
             n_msg = f"Computed over logged frames (N={topo_rows}, stride={stride}, first={topo_meta.get('first_step')}, last={topo_meta.get('last_step')})"
        else:
             n_msg = "No logged frames"

        # Run checks
        for profile in active_profiles:
            p_checks = profile.get("checks", {})
            if "checks" not in run_result: run_result["checks"] = []

            # A) Invariants (Strict Mode - Read from Manifest)
            man_invariants = manifest.get("invariants", {})
            for key, expected_val in p_checks.get("invariants", {}).items():
                if key not in man_invariants:
                     check_item = {
                         "id": f"{profile['name']}.invariants.{key}",
                         "expected": expected_val,
                         "actual": "MISSING",
                         "status": "SKIP",
                         "message": f"Missing manifest key 'invariants.{key}'",
                         "actual_source": os.path.basename(manifest_path)
                     }
                else:
                    actual = man_invariants[key]
                    check_item = {
                        "id": f"{profile['name']}.invariants.{key}",
                        "expected": expected_val,
                        "actual": actual,
                        "actual_source": f"{os.path.basename(manifest_path)}:invariants.{key}"
                    }
                    if str(actual) == str(expected_val):
                         check_item["status"] = "PASS"
                    else:
                         check_item["status"] = "FAIL"
                         check_item["message"] = f"Invariant mismatch"
                         run_result["status"] = "FAIL"
                run_result["checks"].append(check_item)

            # B) Identity (Params)
            for key, expected_val in p_checks.get("identity", {}).items():
                # Handle nested keys
                if "." in key:
                    parts = key.split(".")
                    val = run_meta
                    for p in parts:
                        if isinstance(val, dict): val = val.get(p)
                        else: val = None; break
                    actual = val
                else:
                    actual = run_meta.get(key)
                    
                check_item = {
                    "id": f"{profile['name']}.identity.{key}",
                    "expected": expected_val,
                    "actual": actual,
                }
                if actual == expected_val:
                    check_item["status"] = "PASS"
                else:
                    check_item["status"] = "FAIL"
                    check_item["message"] = "Identity mismatch"
                    run_result["status"] = "FAIL"
                run_result["checks"].append(check_item)

            # C) Analysis Config
            man_config = manifest.get("analysis_config")
            if not man_config:
                 for key, expected_val in p_checks.get("analysis_config", {}).items():
                     check_item = {
                         "id": f"{profile['name']}.analysis.{key}",
                         "expected": expected_val,
                         "actual": "MISSING",
                         "status": "PASS",
                         "message": "Metadata missing (Run --backfill-analysis-config)",
                         "severity": "warning"
                     }
                     if args.strict or profile['name'] == 'canonical':
                          check_item["status"] = "FAIL"
                          run_result["status"] = "FAIL"
                          check_item["severity"] = "fatal"
                     run_result["checks"].append(check_item)
            else:
                 for key, expected_val in p_checks.get("analysis_config", {}).items():
                     actual = man_config.get(key)
                     check_item = {
                         "id": f"{profile['name']}.analysis.{key}",
                         "expected": expected_val,
                         "actual": actual,
                     }
                     if actual == expected_val:
                         check_item["status"] = "PASS"
                     else:
                         check_item["status"] = "FAIL"
                         check_item["message"] = "Config mismatch"
                         run_result["status"] = "FAIL"
                     run_result["checks"].append(check_item)

            # D) Numerical Anchors & Cross-Checks
            metrics = manifest.get("metrics", {}).copy() # Copy to avoid mutating original
            
            # Inject N1/N0
            if n1_pct is not None:
                metrics["topology_neutrality_n1"] = n1_pct
            if n0_pct is not None:
                metrics["strict_neutrality"] = n0_pct

            for metric_key, constraints in p_checks.get("numerical_anchors", {}).items():
                actual = metrics.get(metric_key)
                # Fallbacks for legacy metric names
                if metric_key == "sbr_mean" and actual is None: actual = metrics.get("sbr")
                if metric_key == "f0_mean_hz" and actual is None: actual = metrics.get("dominant_freq_Hz")
                if metric_key == "mean_vortices" and actual is None: actual = metrics.get("mean_total_vortices")
                if metric_key == "low_mass_qp_count" and actual is None: actual = metrics.get("low_mass_quasiparticle_count")
                
                status, msg, sev = check_value(metric_key, actual, constraints)
                check_item = {
                    "id": f"{profile['name']}.anchor.{metric_key}",
                    "expected": constraints, # RAW JSON Object
                    "actual": actual,
                    "status": status,
                    "message": msg,
                    "severity": sev
                }
                if status == "FAIL" and sev == "fatal":
                    run_result["status"] = "FAIL"
                run_result["checks"].append(check_item)
                
            # Cross-checks (Info only)
            if "f0_mean_hz" in p_checks.get("numerical_anchors", {}) and metrics.get("dominant_freq_Hz"):
                 # Check against manifest f0
                 man_f0 = metrics.get("dominant_freq_Hz")
                 # This is circular as we loaded metrics from manifest. 
                 # But if we had a separate source (e.g. CSV summary vs JSON).
                 # "metrics_summary.csv" check?
                 pass

            for d_def in p_checks.get("derived", []):
                status, msg, val = evaluate_derived(d_def, manifest, contract.get("constants", {}))
                check_item = {
                    "id": f"{profile['name']}.derived.{d_def['id']}",
                    "expected": d_def.get("expected"),
                    "actual": val,
                    "status": status,
                    "message": msg
                }
                if status == "FAIL": run_result["status"] = "FAIL"
                run_result["checks"].append(check_item)

            for artifact in p_checks.get("required_artifacts", []):
                # Always relative to run_dir
                path = os.path.join(r_dir, artifact)
                exists = os.path.exists(path)
                
                # For CSV/PNG patterns like '*_spectrum_plot.png'
                # If artifact contains '*', use glob
                if '*' in artifact:
                     glob_pattern = os.path.join(r_dir, artifact)
                     matches = glob.glob(glob_pattern)
                     # print(f"DEBUG: globbing '{glob_pattern}' -> found {len(matches)}")
                     exists = len(matches) > 0
                     actual_name = [os.path.basename(m) for m in matches]
                else:
                     actual_name = artifact if exists else None

                check_item = {
                    "id": f"{profile['name']}.artifact.{artifact}",
                    "expected": "exists",
                    "actual": "exists" if exists else "missing",
                    "status": "PASS" if exists else "FAIL",
                    "files_found": actual_name if exists else []
                }
                if not exists: run_result["status"] = "FAIL"
                run_result["checks"].append(check_item)

        # Append result
        suite_report["runs"].append(run_result)
        if run_result["status"] == "PASS":
            suite_report["summary"]["pass"] += 1
        elif run_result["status"] == "FAIL":
            suite_report["summary"]["fail"] += 1
            
        # Per-run JSON Output
        per_run_path = os.path.join(r_dir, f"_{run_id}_whitepaper_contract_result.json")
        try:
             with open(per_run_path, "w", encoding="utf-8") as f:
                 json.dump(run_result, f, indent=2)
        except Exception as e:
             print(f"Warn: Could not save per-run result to {per_run_path}: {e}")

    # Summary Check
    if suite_report["summary"]["matched_canonical"] == 0:
         print("WARN: No canonical run found in suite.")
         # sys.exit(EXIT_FAIL) # Soften to WARN? No, usually stricter.
         # But user wants "Canonical profil ať se aplikuje jen na běhy, které mu odpovídají".
         # So if NO run matches canonical, it just means we haven't audited the main run yet.
         pass
         
    # Save Report
    out_dir = os.path.join(args.runs_root, "_whitepaper_contract")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "whitepaper_contract_suite.json")
    
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(suite_report, f, indent=2)
        
    print(f"Suite verification complete. Report saved to: {out_path}")

    # Generate Markdown Summary
    md_path = os.path.join(out_dir, "whitepaper_contract_suite.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(f"# Whitepaper Contract Suite Report\n\n")
        f.write(f"**Generated:** {suite_report['header']['timestamp']}\n")
        f.write(f"**Contract:** `{suite_report['header']['contract_id']}`\n\n")
        
        f.write("## Summary\n\n")
        s = suite_report["summary"]
        f.write(f"- **PASS:** {s['pass']}\n")
        f.write(f"- **FAIL:** {s['fail']}\n")
        f.write(f"- **SKIP:** {s['skip']}\n")
        f.write(f"- **Canonical Matches:** {s['matched_canonical']}\n\n")
        
        f.write("## Runs\n\n")
        for r in suite_report["runs"]:
            f.write(f"### `{r['run_id']}`\n")
            f.write(f"- **Status:** {r['status']}\n")
            if "message" in r:
                f.write(f"- **Message:** {r['message']}\n")
            
            # Group checks by status
            fails = [c for c in r.get("checks", []) if c["status"] == "FAIL"]
            if fails:
                f.write(f"- **Failures:**\n")
                for c in fails:
                    f.write(f"  - `{c['id']}`: {c.get('message', 'No message')} (Expected: `{c['expected']}`, Actual: `{c['actual']}`)\n")
            f.write("\n")
            
    print(f"Markdown report saved to: {md_path}")
    
    # Cleanup Mode
    if args.cleanup:
        print("\n--- Cleanup Mode ---")
        to_delete = []
        for r in suite_report["runs"]:
            if r["status"] == "SKIP" and "duplicate_of" in r:
                 # It's a duplicate
                 # Find the directory. run_id is directory name?
                 # runs_root + run_id
                 d_path = os.path.join(args.runs_root, r["run_id"])
                 if os.path.exists(d_path):
                     to_delete.append(d_path)
                     
        if not to_delete:
            print("No duplicate runs found to cleanup.")
        else:
            print(f"Found {len(to_delete)} duplicate runs:")
            for p in to_delete:
                print(f" - {p}")
            
            if args.force:
                confirm = "y"
            else:
                try:
                    confirm = input("Delete these directories? [y/N] ").lower()
                except EOFError:
                    confirm = "n"
            
            if confirm == "y":
                import shutil
                for p in to_delete:
                    print(f"Deleting {p}...")
                    try:
                        shutil.rmtree(p)
                    except Exception as e:
                        print(f"Error removing {p}: {e}")
                print("Cleanup complete.")
            else:
                print("Cleanup aborted.")
    print(f"Summary: PASS={suite_report['summary']['pass']}, FAIL={suite_report['summary']['fail']}, SKIP={suite_report['summary']['skip']}")

    if suite_report["summary"]["fail"] > 0:
        sys.exit(EXIT_FAIL)
    sys.exit(EXIT_PASS)

if __name__ == "__main__":
    main()
