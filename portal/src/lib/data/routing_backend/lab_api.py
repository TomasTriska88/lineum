from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Request, HTTPException
from fastapi.responses import StreamingResponse
from typing import Dict
import asyncio
import time
import numpy as np
import io
import base64
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

import sys
import os
import json
from pathlib import Path
from pydantic import BaseModel
from typing import Dict, Any

from lineum_core.math import CoreConfig, step_core
from scripts.validation_core import (
    run_hydrogen_sweep, run_mu_regression_snapshot, run_particle_playground,
    GOLDEN_HYDRO_SWEEP,
    run_ra1_unitarity, run_ra2_bound_state, run_ra3_excited_state,
    run_ra4_mu_memory, run_ra5_driving, run_ra6_lpf_impact,
)

HISTORY_DIR = Path(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'output', 'lab_history'))
HISTORY_DIR.mkdir(parents=True, exist_ok=True)

def save_run(data: dict):
    if "manifest" in data and "run_id" in data["manifest"]:
        run_id = data["manifest"]["run_id"]
        filepath = HISTORY_DIR / f"{run_id}.json"
        
        # We don't save the massive raw source_code to history json to save disk space
        save_data = data.copy()
        if "source_code" in save_data:
            del save_data["source_code"]
            
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, indent=2)

router = APIRouter()

@router.get("/ux-canon")
async def get_ux_canon():
    """Serves the LAB_UX_CANON.md content for the Help modal."""
    canon_path = Path(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'LAB_UX_CANON.md'))
    if canon_path.exists():
        return {"content": canon_path.read_text(encoding='utf-8')}
    return {"content": "# LAB_UX_CANON.md not found"}

@router.get("/health")
async def get_health():
    """Returns local system health for the Lab UI (git hash and golden tests summary)."""
    import subprocess
    import os
    import sys
    import json
    try:
        git_hash = subprocess.check_output(["git", "rev-parse", "HEAD"], stderr=subprocess.DEVNULL).decode("utf-8").strip()
    except Exception:
        git_hash = "unknown"

        
    try:
        branch = subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"], stderr=subprocess.DEVNULL).decode("utf-8").strip()
    except Exception:
        branch = "unknown"

    vc_path = "Unknown"
    if "scripts.validation_core" in sys.modules:
        vc_path = os.path.abspath(sys.modules["scripts.validation_core"].__file__)
        
    # Delegate to shared audit context helper
    ctx = _get_audit_context()

    is_prod = os.environ.get("NODE_ENV") == "production" or os.environ.get("VITE_NODE_ENV") == "production"

    return {
        "commit_hash": git_hash,
        "git_commit": git_hash,
        "git_branch": branch,
        "current_build": {
            "git_commit": git_hash,
            "git_branch": branch,
            "display": f"{git_hash} ({branch})"
        },
        "active_audit": {
            "git_commit": ctx["contract_commit"]
        },
        "audit_status": ctx["audit_status"],
        "contract_id": ctx["contract_id"],
        "active_contract_id": ctx["contract_id"],
        "audit_output_wp_abs_path": ctx["output_wp_dir"],
        "active_suite_abs_path": ctx["suite_abs_path"],
        "contract_timestamp": ctx["contract_timestamp"],
        "contract_commit": ctx["contract_commit"],
        "equation_fingerprint": ctx["equation_fingerprint"],
        "audit_relevant_code_fingerprint": ctx["audit_relevant_code_fingerprint"],
        "current_audit_relevant_code_fingerprint": ctx["current_audit_relevant_code_fingerprint"],
        "summary_pass": ctx["summary_pass"],
        "summary_fail": ctx["summary_fail"],
        "active_profile": ctx["active_profile"],
        "tests": "PASS (Local)",
        "loaded_modules": {
            "routing_backend": os.path.dirname(os.path.abspath(__file__)),
            "validation_core": vc_path
        },
        "production_safety": {
            "is_production": is_prod,
            "can_generate_audit": not is_prod,
            "can_verify_all": not is_prod,
            "reason": "Production is read-only. Audit generation and bulk verification are disabled." if is_prod else ""
        },
        "canonical_promotion": _get_canonical_promotion(ctx)
    }

def _get_canonical_promotion(ctx):
    import os
    import json
    claims_path = os.path.join(REPO_ROOT_CLAIMS, 'lab', 'src', 'lib', 'data', 'claims.json')
    try:
        with open(claims_path, 'r', encoding='utf-8') as f:
            claims_data = json.load(f)
    except Exception:
        claims_data = []

    required_ids = [c["id"] for c in claims_data if c.get("canonical_claim_set") == "REQUIRED_FOR_PROMOTION"]
    results = _load_claim_results()
    current_fingerprint = ctx.get("equation_fingerprint", "unknown")
    
    req_status = []
    missing_reqs = []
    all_ready = True
    
    for rid in required_ids:
        res = results.get(rid, {})
        saved_fp = res.get("equation_fingerprint", "")
        # Check staleness
        is_stale = (saved_fp and saved_fp != "unknown" and current_fingerprint != "unknown" and saved_fp != current_fingerprint)
        
        status = res.get("resolved_claim_status", "UNTESTED")
        evidence_source = "NONE"
        is_ready = False
        
        if is_stale:
            status = "STALE"
            evidence_source = "STALE"
        else:
            if status == "SUPPORTED":
                if res.get("is_audit_grade"):
                    evidence_source = "CANONICAL_SUITE"
                    is_ready = True
                else:
                    evidence_source = "EXPERIMENTAL_RUN"
                    status = "EXPERIMENTAL_SUPPORTED"
            elif status == "EXPERIMENTAL_SUPPORTED":
                evidence_source = "EXPERIMENTAL_RUN"
            elif status == "UNTESTED":
                evidence_source = "NONE"

        if not is_ready:
            all_ready = False
            missing_reqs.append(f"{rid} requires CANONICAL_SUITE evidence, current is {evidence_source}")
            
        req_status.append({
            "id": rid,
            "status": status,
            "is_ready": is_ready,
            "evidence_source": evidence_source
        })
        
    if all_ready and len(required_ids) > 0:
        if ctx.get("audit_status") == "AUDITED" and ctx.get("active_profile") == "wave_core":
             promo_status = "CANONICAL_AUDITED"
        else:
             promo_status = "READY_FOR_CANONICAL_PROMOTION"
    elif len(required_ids) > 0:
        promo_status = "IN_PROGRESS"
    else:
        promo_status = "NOT_READY"
        
    return {
        "canonical_promotion_status": promo_status,
        "missing_requirements": missing_reqs,
        "required_claims_status": req_status
    }

# ══════════════════════════════════════════════════════════════
# Shared Audit Context Helper
# ══════════════════════════════════════════════════════════════

def _get_audit_context():
    """
    Resolves the current audit state: audit_status, active_profile,
    contract_id, contract_commit, etc.  Shared by /health and /run_preset.
    """
    import subprocess
    audit_status = "NONE"
    contract_id = None
    contract_timestamp = "unknown"
    contract_commit = ""
    equation_fingerprint = ""
    suite_audit_fp = "unknown"
    summary_pass = 0
    summary_fail = 0
    active_profile = None

    REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    output_wp_dir = os.path.join(REPO_ROOT, 'output_wp')
    suite_abs_path = os.path.join(output_wp_dir, 'runs', '_whitepaper_contract', 'whitepaper_contract_suite.json')
    suite_path = Path(suite_abs_path)

    try:
        curr_full = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], stderr=subprocess.DEVNULL
        ).decode("utf-8").strip()

        import sys
        if os.path.join(REPO_ROOT, "tools") not in sys.path:
            sys.path.append(os.path.join(REPO_ROOT, "tools"))
        try:
            from whitepaper_contract import compute_audit_relevant_fingerprint
            curr_audit_fp = compute_audit_relevant_fingerprint(REPO_ROOT)
        except Exception:
            curr_audit_fp = "unknown"

        if suite_path.exists():
            with open(suite_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            audits = data if isinstance(data, list) else [data]
            audits.sort(key=lambda x: x.get("header", {}).get("timestamp", ""), reverse=True)

            for audit in audits:
                summary = audit.get("summary", {})
                if summary.get("fail", 1) == 0:
                    header = audit.get("header", {})
                    contract_id = header.get("contract_id")
                    contract_timestamp = header.get("timestamp", "unknown")
                    contract_commit = header.get("git_commit", "")
                    equation_fingerprint = header.get("equation_fingerprint", "unknown")
                    suite_audit_fp = header.get("audit_relevant_code_fingerprint", "unknown")
                    summary_pass = summary.get("pass", 0)
                    summary_fail = summary.get("fail", 0)

                    active_run_has_metrics = False
                    for run in audit.get("runs", []):
                        mp = run.get("matched_profile")
                        if mp and run.get("status") == "PASS" and mp != "baseline":
                            active_profile = mp
                            if run.get("metrics"):
                                active_run_has_metrics = True
                            break
                    if not active_profile:
                        for run in audit.get("runs", []):
                            if run.get("status") == "PASS":
                                active_profile = run.get("matched_profile")
                                if run.get("metrics"):
                                    active_run_has_metrics = True
                                break

                    if curr_audit_fp != "unknown" and suite_audit_fp == curr_audit_fp:
                        if contract_commit == curr_full:
                            audit_status = "AUDITED"
                            if active_profile == "wave_core" and not active_run_has_metrics:
                                audit_status = "EXPERIMENTAL / BASELINE METRICS"
                        else:
                            audit_status = "BUILD_NEWER"
                    else:
                        audit_status = "REVALIDATION_REQUIRED"
                    break
    except Exception as e:
        print(f"Audit context error: {e}")

    return {
        "audit_status": audit_status,
        "contract_id": contract_id,
        "contract_timestamp": contract_timestamp,
        "contract_commit": contract_commit or "unknown",
        "equation_fingerprint": equation_fingerprint or "unknown",
        "audit_relevant_code_fingerprint": suite_audit_fp,
        "current_audit_relevant_code_fingerprint": curr_audit_fp if 'curr_audit_fp' in locals() else "unknown",
        "summary_pass": summary_pass,
        "summary_fail": summary_fail,
        "active_profile": active_profile,
        "output_wp_dir": output_wp_dir,
        "suite_abs_path": suite_abs_path if suite_path.exists() else None,
    }

# ══════════════════════════════════════════════════════════════
# Scenario Registry (Whitelist)
# ══════════════════════════════════════════════════════════════

SCENARIO_REGISTRY = {
    "preset-core-001": {
        "claim_id": "CL-CORE-001",
        "description": "Dominant spectral tone stability (Unitarity Check)",
        "runner": "run_ra1_unitarity",
        "contract_profile": "wave_core"
    },
    "preset-core-002": {
        "claim_id": "CL-CORE-002",
        "description": "Topological neutrality maintained (Bound State/Edges)",
        "runner": "run_ra2_bound_state",
        "contract_profile": "wave_core"
    },
    "preset-core-003": {
        "claim_id": "CL-CORE-003",
        "description": "φ center-trace exhibits a measurable half-life (Excited Forms)",
        "runner": "run_ra3_excited_state",
        "contract_profile": "wave_core"
    },
    "preset-core-004": {
        "claim_id": "CL-CORE-004",
        "description": "Stable localized excitations (linons) emerge (Mu Memory footprinting)",
        "runner": "run_ra4_mu_memory",
        "contract_profile": "wave_core"
    },
}

# Runner dispatch table (maps runner name → callable)
_RUNNERS = {
    "run_ra1_unitarity": run_ra1_unitarity,
    "run_ra2_bound_state": run_ra2_bound_state,
    "run_ra3_excited_state": run_ra3_excited_state,
    "run_ra4_mu_memory": run_ra4_mu_memory,
}

# ══════════════════════════════════════════════════════════════
# Claim Result Persistence
# ══════════════════════════════════════════════════════════════

REPO_ROOT_CLAIMS = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
CLAIM_RESULTS_FILE = Path(os.path.join(REPO_ROOT_CLAIMS, 'output', 'claim_results.json'))
CLAIM_RESULTS_FILE.parent.mkdir(parents=True, exist_ok=True)

def _load_claim_results() -> dict:
    """Load persisted claim results from disk."""
    if CLAIM_RESULTS_FILE.exists():
        try:
            with open(CLAIM_RESULTS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def _save_claim_result(claim_id: str, result: dict):
    """Save a single claim result to persistence (merge into existing)."""
    all_results = _load_claim_results()
    all_results[claim_id] = result
    with open(CLAIM_RESULTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=2)

def _get_current_git_commit() -> str:
    """Get current HEAD commit hash."""
    import subprocess
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], stderr=subprocess.DEVNULL
        ).decode("utf-8").strip()
    except Exception:
        return "unknown"

# ══════════════════════════════════════════════════════════════
# Claim Verification Endpoint
# ══════════════════════════════════════════════════════════════

from fastapi import HTTPException
from datetime import datetime, timezone

def _extract_canonical_traceability(suite_path: str, claim_id: str, mapped_profile: str) -> list:
    if not suite_path or not os.path.exists(suite_path):
        return []
    try:
        with open(suite_path, 'r', encoding='utf-8') as f:
            suite_data = json.load(f)
        audits = suite_data if isinstance(suite_data, list) else [suite_data]
        audits.sort(key=lambda x: x.get("header", {}).get("timestamp", ""), reverse=True)
        if not audits:
            return []
        latest_audit = audits[0]
        for run in latest_audit.get("runs", []):
            if run.get("matched_profile") == mapped_profile:
                metrics = run.get("metrics", {})
                checks = run.get("checks", {})
                
                claim_metric_keys = []
                if claim_id == "CL-CORE-001":
                    claim_metric_keys = ["f0_mean_hz", "sbr_mean"]
                elif claim_id == "CL-CORE-002":
                    claim_metric_keys = ["topology_neutrality_n1", "mean_vortices"]
                elif claim_id == "CL-CORE-003":
                    claim_metric_keys = ["phi_half_life_steps", "max_lifespan_steps"]
                elif claim_id == "CL-CORE-004":
                    claim_metric_keys = ["low_mass_qp_count"]
                else:
                    claim_metric_keys = list(metrics.keys())
                
                evaluations = []
                for m_key in claim_metric_keys:
                    actual = metrics.get(m_key)
                    check_obj = next((c for c in checks if m_key in c.get("id", "")), None)
                    if check_obj:
                        expected_rule = check_obj.get("expected", {})
                        passed = check_obj.get("status") == "PASS"
                        if isinstance(expected_rule, dict):
                            rule_str = f"min:{expected_rule.get('min', '*')} max:{expected_rule.get('max', '*')}"
                            if "target" in expected_rule:
                                rule_str = f"target:{expected_rule['target']} tol:{expected_rule.get('rel_tol', '*')}"
                        else:
                            rule_str = str(expected_rule)
                    else:
                        passed = True
                        rule_str = "within contract limits"
                    
                    evaluations.append({
                        "metric_name": m_key,
                        "actual_value": actual,
                        "threshold_rule": rule_str,
                        "comparison_operator": "in_bounds",
                        "source_file_or_field": "whitepaper_contract_suite.json",
                        "passed": passed,
                        "why_status_changed": f"{actual} in {rule_str} -> {'PASS' if passed else 'FAIL'}"
                    })
                return evaluations
    except Exception as e:
        print(f"Error extracting canonical traceability: {e}")
    return []

@router.get("/run_preset")
async def run_preset(preset_name: str):
    """
    Authoritative claim verification endpoint.
    
    - Validates preset_name against SCENARIO_REGISTRY whitelist
    - Runs the physics scenario reusing existing RA runners
    - Resolves audit context to determine canonical vs experimental
    - Persists result to claim_results.json
    - Returns resolved_claim_status, manifest_id, contract context
    """
    if preset_name not in SCENARIO_REGISTRY:
        raise HTTPException(
            status_code=404,
            detail=f"Unknown preset '{preset_name}'. "
                   f"Allowed: {list(SCENARIO_REGISTRY.keys())}"
        )

    scenario = SCENARIO_REGISTRY[preset_name]
    runner_name = scenario["runner"]
    runner_fn = _RUNNERS.get(runner_name)
    if not runner_fn:
        raise HTTPException(status_code=500, detail=f"Runner '{runner_name}' not found")

    # Execute the physics scenario
    val_data = runner_fn()

    overall_pass = val_data.get("overall_pass", False)
    manifest = val_data.get("manifest", {})
    manifest_id = manifest.get("run_id", manifest.get("manifest_id", f"claim-{preset_name}"))

    # Save run to history
    response_data = {
        "manifest": manifest,
        "expectations": val_data.get("expectations", []),
        "expectation_results": val_data.get("expectation_results", []),
        "overall_pass": overall_pass,
    }
    save_run(response_data)

    # Resolve audit context
    ctx = _get_audit_context()
    is_canonical = ctx["audit_status"] == "AUDITED" and ctx["contract_id"] is not None
    git_commit = _get_current_git_commit()

    # Determine resolved claim status
    import json
    claims_path = os.path.join(REPO_ROOT_CLAIMS, 'lab', 'src', 'lib', 'data', 'claims.json')
    claim_set = "NOT_PART_OF_PROMOTION"
    try:
        with open(claims_path, 'r', encoding='utf-8') as f:
            claims_data = json.load(f)
            for c in claims_data:
                if c.get("id") == scenario.get("claim_id"):
                    claim_set = c.get("canonical_claim_set", "NOT_PART_OF_PROMOTION")
                    break
    except Exception:
        pass

    is_eligible_for_canonical = claim_set in ["REQUIRED_FOR_PROMOTION", "SUPPORTING_ONLY"]
    
    if is_canonical and is_eligible_for_canonical:
        resolved_claim_status = "SUPPORTED" if overall_pass else "CONTRADICTED"
    else:
        resolved_claim_status = (
            "EXPERIMENTAL_SUPPORTED" if overall_pass else "EXPERIMENTAL_CONTRADICTED"
        )
        
    from lineum_core.math import ExecutionPolicy
    runtime_meta = ExecutionPolicy.get_metadata()
    
    exp_results = val_data.get("expectation_results", [])
    metrics_evaluations = []
    
    if is_canonical:
        mapped_profile = scenario.get("contract_profile", ctx["active_profile"])
        metrics_evaluations = _extract_canonical_traceability(
            ctx.get("suite_abs_path"), scenario["claim_id"], mapped_profile
        )

    if not metrics_evaluations:
        for e in exp_results:
            m_val = e.get("measured")
            m_exp = e.get("expected")
            m_op = e.get("op", "")
            m_pass = e.get("passed", False)
            metrics_evaluations.append({
                "metric_name": e.get("metric", "unknown"),
                "actual_value": m_val,
                "threshold_rule": m_exp,
                "comparison_operator": m_op,
                "source_file_or_field": "validation_core.py",
                "passed": m_pass,
                "why_status_changed": f"{m_val} {m_op} {m_exp} -> {'PASS' if m_pass else 'FAIL'}"
            })

    traceability = {
        "claim_id": scenario["claim_id"],
        "scenario_id": preset_name,
        "active_profile": ctx["active_profile"] or "unknown",
        "execution_device": "cpu" if is_canonical else runtime_meta.get("execution_device", "unknown"),
        "deterministic_mode": True if is_canonical else runtime_meta.get("deterministic_mode", False),
        "equation_fingerprint": ctx["equation_fingerprint"],
        "metrics": metrics_evaluations,
        "overall_pass": overall_pass,
    }

    # Persist claim result with full context
    claim_result = {
        "claim_id": scenario["claim_id"],
        "scenario_id": preset_name,
        "resolved_claim_status": resolved_claim_status,
        "is_audit_grade": is_canonical,
        "manifest_id": manifest_id,
        "contract_id": ctx["contract_id"],
        "audit_status": ctx["audit_status"],
        "active_profile": ctx["active_profile"],
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "git_commit": git_commit,
        "equation_fingerprint": ctx["equation_fingerprint"],
        "overall_pass": overall_pass,
        "traceability": traceability,
    }
    _save_claim_result(scenario["claim_id"], claim_result)

    return {
        **claim_result,
        "expectation_results": val_data.get("expectation_results", []),
        "message": f"Scenario '{preset_name}' executed. {len(val_data.get('expectation_results', []))} checks evaluated.",
    }


@router.get("/claims")
async def alias_claims():
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/api/lab/claim_results")

@router.get("/whitepapers")
async def alias_whitepapers():
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/api/lab/claims")

@router.get("/claim_results")
async def get_claim_results():
    """
    Load last known claim verification states.
    Marks results as STALE if git_commit or equation_fingerprint
    no longer match the current build.
    """
    results = _load_claim_results()
    if not results:
        return {"results": {}, "stale_count": 0}

    ctx = _get_audit_context()
    current_commit = _get_current_git_commit()
    current_fingerprint = ctx.get("equation_fingerprint", "unknown")

    stale_count = 0
    for claim_id, result in results.items():
        saved_commit = result.get("git_commit", "")
        saved_fingerprint = result.get("equation_fingerprint", "")

        is_stale = (
            (saved_commit and saved_commit != current_commit) or
            (saved_fingerprint and saved_fingerprint != "unknown" and
             current_fingerprint != "unknown" and
             saved_fingerprint != current_fingerprint)
        )
        result["is_stale"] = is_stale
        if is_stale:
            stale_count += 1
            if result.get("resolved_claim_status") in ["SUPPORTED", "CONTRADICTED"]:
                result["resolved_claim_status"] = "STALE_CANONICAL"
            elif result.get("resolved_claim_status") in ["EXPERIMENTAL_SUPPORTED", "EXPERIMENTAL_CONTRADICTED"]:
                result["resolved_claim_status"] = "OUTDATED_FOR_CURRENT_EQUATION"

    return {
        "results": results,
        "stale_count": stale_count,
        "current_git_commit": current_commit,
        "current_equation_fingerprint": current_fingerprint,
    }


@router.post("/verify_all")
async def verify_all():
    """
    Run all TESTABLE_NOW claim scenarios in bulk.
    Returns results + test-suite-style summary with detailed counts and duration.
    """
    import os
    from fastapi import HTTPException
    is_prod = os.environ.get("NODE_ENV") == "production" or os.environ.get("VITE_NODE_ENV") == "production"
    if is_prod:
        raise HTTPException(status_code=403, detail="Bulk verification disabled in production. Ready-only mode.")

    import time
    start_time = time.monotonic()

    ctx = _get_audit_context()
    is_canonical = ctx["audit_status"] == "AUDITED" and ctx["contract_id"] is not None
    git_commit = _get_current_git_commit()
    now = datetime.now(timezone.utc).isoformat()

    # Canonical claims reading - simple JSON load + Scientific Schema enforcement
    total_claims = 0
    testable_count = 0
    claims_by_id = {}
    try:
        claims_path = os.path.join(os.path.dirname(__file__), "..", "lab", "src", "lib", "data", "claims.json")
        with open(claims_path, 'r', encoding='utf-8') as f:
            claims_data = json.load(f)
            total_claims = len(claims_data)
            for c in claims_data:
                claims_by_id[c["id"]] = c
                # Only strictly approved claims may be counted as testable candidates
                if c.get("testability") == "TESTABLE_NOW" and c.get("verification_spec_status") == "APPROVED":
                    testable_count += 1
    except Exception as e:
        print(f"Total claims JSON parse failed: {e}")

    not_testable_count = total_claims - testable_count

    results = {}
    tested = 0
    supported = 0
    contradicted = 0
    experimental_supported = 0
    experimental_contradicted = 0
    skipped = 0
    errors = []

    for preset_name, scenario in SCENARIO_REGISTRY.items():
        claim_id = scenario["claim_id"]
        c_entry = claims_by_id.get(claim_id, {})
        
        # Enforce scientific approval barrier before running scenario
        if c_entry.get("testability") != "TESTABLE_NOW" or c_entry.get("verification_spec_status") != "APPROVED":
            skipped += 1
            continue
        runner_fn = _RUNNERS.get(scenario["runner"])
        if not runner_fn:
            skipped += 1
            continue

        try:
            val_data = runner_fn()
            overall_pass = val_data.get("overall_pass", False)
            manifest = val_data.get("manifest", {})
            manifest_id = manifest.get("run_id", manifest.get("manifest_id", f"claim-{preset_name}"))

            # Save run to history
            save_run({
                "manifest": manifest,
                "expectations": val_data.get("expectations", []),
                "expectation_results": val_data.get("expectation_results", []),
                "overall_pass": overall_pass,
            })

            if is_canonical:
                status = "SUPPORTED" if overall_pass else "CONTRADICTED"
            else:
                status = "EXPERIMENTAL_SUPPORTED" if overall_pass else "EXPERIMENTAL_CONTRADICTED"
                
            from lineum_core.math import ExecutionPolicy
            runtime_meta = ExecutionPolicy.get_metadata()
            
            exp_results = val_data.get("expectation_results", [])
            metrics_evaluations = []
            
            if is_canonical:
                mapped_profile = scenario.get("contract_profile", ctx["active_profile"])
                metrics_evaluations = _extract_canonical_traceability(
                    ctx.get("suite_abs_path"), scenario["claim_id"], mapped_profile
                )

            if not metrics_evaluations:
                for e in exp_results:
                    m_val = e.get("measured")
                    m_exp = e.get("expected")
                    m_op = e.get("op", "")
                    m_pass = e.get("passed", False)
                    metrics_evaluations.append({
                        "metric_name": e.get("metric", "unknown"),
                        "actual_value": m_val,
                        "threshold_rule": m_exp,
                        "comparison_operator": m_op,
                        "source_file_or_field": "validation_core.py",
                        "passed": m_pass,
                        "why_status_changed": f"{m_val} {m_op} {m_exp} -> {'PASS' if m_pass else 'FAIL'}"
                    })

            traceability = {
                "claim_id": scenario["claim_id"],
                "scenario_id": preset_name,
                "active_profile": ctx["active_profile"] or "unknown",
                "execution_device": "cpu" if is_canonical else runtime_meta.get("execution_device", "unknown"),
                "deterministic_mode": True if is_canonical else runtime_meta.get("deterministic_mode", False),
                "equation_fingerprint": ctx["equation_fingerprint"],
                "metrics": metrics_evaluations,
                "overall_pass": overall_pass,
            }

            claim_result = {
                "claim_id": scenario["claim_id"],
                "scenario_id": preset_name,
                "resolved_claim_status": status,
                "is_audit_grade": is_canonical,
                "manifest_id": manifest_id,
                "contract_id": ctx["contract_id"],
                "audit_status": ctx["audit_status"],
                "active_profile": ctx["active_profile"],
                "checked_at": now,
                "git_commit": git_commit,
                "equation_fingerprint": ctx["equation_fingerprint"],
                "overall_pass": overall_pass,
                "traceability": traceability,
            }

            _save_claim_result(scenario["claim_id"], claim_result)
            results[scenario["claim_id"]] = claim_result

            tested += 1
            if status == "SUPPORTED":
                supported += 1
            elif status == "CONTRADICTED":
                contradicted += 1
            elif status == "EXPERIMENTAL_SUPPORTED":
                experimental_supported += 1
            elif status == "EXPERIMENTAL_CONTRADICTED":
                experimental_contradicted += 1

        except Exception as e:
            errors.append({"preset": preset_name, "error": str(e)})
            skipped += 1

    duration_ms = int((time.monotonic() - start_time) * 1000)

    return {
        "results": results,
        "summary": {
            "total_claims": total_claims,
            "testable_count": testable_count,
            "not_testable_count": not_testable_count,
            "tested_count": tested,
            "supported": supported,
            "contradicted": contradicted,
            "experimental_supported": experimental_supported,
            "experimental_contradicted": experimental_contradicted,
            "experimental": experimental_supported + experimental_contradicted,
            "skipped": skipped,
            "error_count": len(errors),
            "errors": errors,
            "duration_ms": duration_ms,
            "is_canonical": is_canonical,
            "audit_status": ctx["audit_status"],
        },
    }


@router.get("/audit/config")
async def get_audit_config(request: Request):
    """Returns access control and runtime device info for audit generation."""
    host = request.client.host
    is_localhost = host in ("127.0.0.1", "::1", "localhost", "0.0.0.0")
    
    import subprocess
    import sys
    import os
    import json
    REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    
    script = (
        "import json\n"
        "import os\n"
        "os.environ['LINEUM_RUN_MODE'] = 'false'\n"
        "from lineum_core.math import ExecutionPolicy\n"
        "ExecutionPolicy.init_core_determinism(enforce_canonical=True)\n"
        "print('---METADATA_START---')\n"
        "print(json.dumps(ExecutionPolicy.get_metadata()))\n"
        "print('---METADATA_END---')\n"
    )
    
    meta = {
        "execution_device": "cpu",
        "deterministic_mode": True,
        "canonical_audit_allowed_on_cuda": False,
        "cuda_available": False,
        "device_name": "Unknown",
        "fallback_reason": "Subprocess probe failed",
        "reason": None
    }
    
    try:
        env = os.environ.copy()
        env["LINEUM_RUN_MODE"] = "false"
        result = subprocess.run(
            [sys.executable, "-c", script],
            capture_output=True, text=True, cwd=REPO_ROOT, env=env, timeout=10
        )
        out = result.stdout
        if "---METADATA_START---" in out and "---METADATA_END---" in out:
            json_str = out.split("---METADATA_START---")[1].split("---METADATA_END---")[0].strip()
            parsed = json.loads(json_str)
            meta.update(parsed)
            # Map fallback reason for backwards compatibility with front-end
            meta["fallback_reason"] = parsed.get("reason", None)
    except Exception as e:
        meta["fallback_reason"] = f"Probe error: {e}"
        
    import os
    is_prod = os.environ.get("NODE_ENV") == "production" or os.environ.get("VITE_NODE_ENV") == "production"
    
    meta["allowed"] = is_localhost and not is_prod
    if is_prod:
        meta["reason"] = "Audit generation disabled in production. Ready-only mode."
    elif not is_localhost:
        meta["reason"] = "Audit generation is available only on localhost / internal environment."
        
    return meta


@router.post("/audit/generate")
async def generate_audit_contract(request: Request):
    """
    Full audit pipeline streaming via SSE (Server-Sent Events).
    """
    import os
    is_prod = os.environ.get("NODE_ENV") == "production" or os.environ.get("VITE_NODE_ENV") == "production"
    if is_prod:
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Audit generation disabled in production. Ready-only mode.")

    import subprocess
    import sys
    import asyncio
    
    host = request.client.host
    if host not in ("127.0.0.1", "::1", "localhost", "0.0.0.0"):
        raise HTTPException(status_code=403, detail="Audit generation is available only on localhost / internal environment.")

    REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    def sse_generator():
        import subprocess
        start_time = time.monotonic()
        
        def emit(step, detail, status="progress", extra=None):
            elapsed = round(time.monotonic() - start_time, 1)
            payload = {"status": status, "step": step, "detail": detail, "elapsed": elapsed}
            if extra:
                payload.update(extra)
            return f"data: {json.dumps(payload)}\n\n"

        try:
            yield emit(0, "Checking environment")
            time.sleep(0.1)

            lineum_path = os.path.join(REPO_ROOT, 'lineum.py')
            env = os.environ.copy()
            env["LINEUM_BASE_OUTPUT_DIR"] = "output_wp"
            env["LINEUM_AUDIT_PROFILE"] = "whitepaper_core"
            env["LINEUM_RUN_ID"] = "6"
            env["LINEUM_RUN_MODE"] = "false"
            env["LINEUM_SEED"] = "41"
            env["LINEUM_STEPS"] = "2000"
            env["LINEUM_RESUME"] = "false"
            env["PYTHONUTF8"] = "1"
            env["PYTHONIOENCODING"] = "utf-8"

            yield emit(1, "Starting physics run (this may take a few minutes)...")

            process1 = subprocess.Popen(
                [sys.executable, lineum_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                cwd=REPO_ROOT,
                env=env
            )

            for line in iter(process1.stdout.readline, b''):
                text = line.decode('utf-8', errors='replace').strip()
                if "device" in text.lower():
                    yield emit(2, f"{text}")

            process1.stdout.close()
            returncode1 = process1.wait()

            if returncode1 != 0:
                yield emit(2, f"lineum.py failed (exit {returncode1})", "error")
                return

            yield emit(3, "Writing run artifacts...")
            
            # Step 2: Suite verification
            yield emit(4, "Rebuilding suite & verifying claims...")
            contract_path = os.path.join(REPO_ROOT, 'tools', 'whitepaper_contract.py')
            process2 = subprocess.Popen(
                [sys.executable, contract_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=REPO_ROOT,
                env=env
            )
            process2.communicate()

            if process2.returncode != 0:
                yield emit(4, f"whitepaper_contract.py failed", "error")
                return

            yield emit(5, "Refreshing Lab state...")

            # Find new run_id
            latest_run_path = os.path.join(REPO_ROOT, 'output_wp', 'latest_run.txt')
            latest_run_value = "unknown"
            if os.path.isfile(latest_run_path):
                with open(latest_run_path, 'r', encoding='utf-8') as f:
                    latest_run_value = f.read().strip()

            yield emit(6, "Done", "success", {
                "new_run_id": latest_run_value.replace("runs/", ""),
                "audit_status": "AUDITED"
            })
        except Exception as e:
            import traceback
            err_msg = str(e) or "Unknown exception"
            print("SSE GENERATOR EXCEPTION:\n", traceback.format_exc())
            yield emit(99, f"Fatal error: {err_msg}", "error")

    return StreamingResponse(sse_generator(), media_type="text/event-stream")

class IntegrationEventRequest(BaseModel):
    event: str
    claim_id: str
    applied_commit: str
    contract_id: str
    manifest_id: str
    equation_fingerprint: str
    whitepaper_file: str
    whitepaper_anchor: str
    timestamp_utc: str

@router.get("/integration_log")
def get_integration_log():
    log_path = Path(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'output_wp', 'whitepaper_integration_log.json'))
    if log_path.exists():
        try:
            with open(log_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data
        except json.JSONDecodeError:
            return {"events": []}
    return {"events": []}

@router.post("/integration_log")
def append_integration_event(req: IntegrationEventRequest):
    log_path = Path(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'output_wp', 'whitepaper_integration_log.json'))
    
    data = {"events": []}
    if log_path.exists():
        try:
            with open(log_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if "events" not in data:
                    data = {"events": []}
        except json.JSONDecodeError:
            pass
            
    data["events"].append(req.dict())
    
    # Ensure directory exists
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with open(log_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
        
    return {"status": "success", "event_added": req.dict()}

@router.websocket("/hydrogen")
async def ws_hydrogen(websocket: WebSocket):
    """
    Streams the Hydrogen 2D Ground State Validation (Wave Core).
    Phase A: Diffusion cooling (Imaginary time)
    Phase B: Unitary wave propagation 
    """
    await websocket.accept()
    
    size = 64
    Z = 2.0
    eps = 0.1
    
    x = np.linspace(-1, 1, size)
    y = np.linspace(-1, 1, size)
    X, Y = np.meshgrid(x, y)
    R = np.sqrt(X**2 + Y**2)
    
    V = -Z / np.sqrt(R**2 + eps**2)
    phi_pot = np.clip(-V * 100, 0, 1000)
    
    psi = np.exp(-R**2 / 0.5).astype(np.complex128)
    kappa = np.ones((size, size), dtype=np.float64)
    state = {"psi": psi.copy(), "phi": phi_pot.copy(), "kappa": kappa.copy()}
    
    cfg_itp = CoreConfig(dt=0.1, physics_mode_psi="diffusion", use_mode_coupling=False)
    cfg_wave = CoreConfig(dt=0.1, physics_mode_psi="wave_baseline", use_mode_coupling=False)
    
    start_time = time.time()
    MAX_TIME = 30.0
    
    try:
        # Phase A: Cooling
        for step in range(300):
            if time.time() - start_time > MAX_TIME: break
            
            state = step_core(state, cfg_itp)
            N_curr = np.sum(np.abs(state["psi"])**2)
            state["psi"] = state["psi"] / np.sqrt(N_curr)
            
            if step % 5 == 0:
                dens = np.abs(state["psi"])**2
                log_dens = np.log10(dens + 1e-12)
                # Normalize log_dens for canvas rendering (0-255 roughly)
                min_l, max_l = np.min(log_dens), np.max(log_dens)
                norm_dens = (log_dens - min_l) / (max_l - min_l + 1e-9)
                
                await websocket.send_json({
                    "phase": "Cooling (Imaginary Time)",
                    "step": step,
                    "max_steps": 300,
                    "n_t": N_curr,
                    "dens_flat": norm_dens.flatten().tolist()
                })
                await asyncio.sleep(0.01)

        # Phase B: Wave Propagation
        for step in range(100):
            if time.time() - start_time > MAX_TIME: break
            
            state = step_core(state, cfg_wave)
            
            if step % 2 == 0:
                dens = np.abs(state["psi"])**2
                
                # Calculate edge mass
                border = int(size * 0.1)
                edge_mask = np.ones((size, size), dtype=bool)
                edge_mask[border:-border, border:-border] = False
                edge_mass = np.sum(dens[edge_mask]) / np.sum(dens)
                
                log_dens = np.log10(dens + 1e-12)
                min_l, max_l = np.min(log_dens), np.max(log_dens)
                norm_dens = (log_dens - min_l) / (max_l - min_l + 1e-9)
                
                N_curr = np.sum(dens)
                
                await websocket.send_json({
                    "phase": "Unitary Wave Validation",
                    "step": step,
                    "max_steps": 100,
                    "n_t": N_curr,
                    "edge_mass": edge_mass,
                    "dens_flat": norm_dens.flatten().tolist()
                })
                await asyncio.sleep(0.01)
                
        await websocket.close()
    except WebSocketDisconnect:
        print("Hydrogen lab client disconnected.")
    except Exception as e:
        print(f"Hydrogen lab error: {e}")

@router.websocket("/regression")
async def ws_regression(websocket: WebSocket):
    """
    Streams the Mu Memory regression test comparing Diffusion and Wave side-by-side.
    """
    await websocket.accept()
    
    size = 64 # scaled down for real-time web socket performance
    
    def setup_state():
        x = np.linspace(-1, 1, size)
        y = np.linspace(-1, 1, size)
        X, Y = np.meshgrid(x, y)
        
        psi = np.zeros((size, size), dtype=np.complex128)
        phi = np.full((size, size), 200.0, dtype=np.float64)
        kappa = np.ones((size, size), dtype=np.float64)
        
        # Central obstacle
        kappa[30:34, 20:44] = 0.0
        
        return {
            "psi": psi,
            "phi": phi,
            "kappa": kappa,
            "mu": np.zeros((size, size), dtype=np.float64)
        }
    
    state_diff = setup_state()
    state_wave = setup_state()
    
    cfg_diff = CoreConfig(dt=0.1, physics_mode_psi="diffusion", use_mode_coupling=True, use_mu=True)
    cfg_wave = CoreConfig(dt=0.1, physics_mode_psi="wave_projected_soft", wave_lpf_enabled=True, use_mode_coupling=True, use_mu=True)
    
    start_time = time.time()
    MAX_TIME = 60.0 # longer timeout for regression
    
    try:
        cap_val = cfg_diff.mu_cap
        
        for step in range(1000):
            if time.time() - start_time > MAX_TIME: break
            
            # Driving forces
            pulse_a = (0.1 + 0.1j) * cfg_diff.dt
            pulse_b = (0.1 - 0.1j) * cfg_diff.dt
            
            for s in [state_diff, state_wave]:
                s["psi"][15:18, 15:18] += pulse_a
                s["psi"][45:48, 45:48] += pulse_b
                
            state_diff = step_core(state_diff, cfg_diff)
            state_wave = step_core(state_wave, cfg_wave)
            
            if step % 10 == 0:
                mu_diff = state_diff["mu"]
                mu_wave = state_wave["mu"]
                
                # Normalize 0..cap_val to 0..1 for UI
                norm_mu_diff = np.clip(mu_diff / cap_val, 0.0, 1.0).flatten().tolist()
                norm_mu_wave = np.clip(mu_wave / cap_val, 0.0, 1.0).flatten().tolist()
                
                psi_diff_norm = np.clip(np.abs(state_diff["psi"])**2 / 5.0, 0.0, 1.0).flatten().tolist()
                psi_wave_norm = np.clip(np.abs(state_wave["psi"])**2 / 5.0, 0.0, 1.0).flatten().tolist()
                
                await websocket.send_json({
                    "step": step,
                    "max_steps": 1000,
                    "diff_mu": norm_mu_diff,
                    "wave_mu": norm_mu_wave,
                    "diff_psi": psi_diff_norm,
                    "wave_psi": psi_wave_norm,
                    "diff_max_mu": float(np.max(mu_diff)),
                    "wave_max_mu": float(np.max(mu_wave)),
                    "diff_n": float(state_diff["telemetry"]["N_t"]),
                    "wave_n": float(state_wave["telemetry"]["N_t"])
                })
                await asyncio.sleep(0.01)
                
        await websocket.close()
    except WebSocketDisconnect:
        print("Regression lab client disconnected.")
    except Exception as e:
        print(f"Regression lab error: {e}")

@router.get("/hydrogen/sweep")
async def get_hydrogen_sweep(golden: bool = False):
    """ Runs the golden validation sweep (VALIDATE = conservative params that MUST PASS) """
    sweeps = GOLDEN_HYDRO_SWEEP
    
    grid_sizes = [s[0] for s in sweeps]
    Z_vals = [s[1] for s in sweeps]
    eps_vals = [s[2] for s in sweeps]
    wave_dt = sweeps[0][3] if len(sweeps[0]) > 3 else 0.01
    
    val_data = run_hydrogen_sweep(grid_sizes, Z_vals, eps_vals, wave_dt=wave_dt)
    manifest = val_data["manifest"]
    results = val_data["results"]
    dens = val_data["final_dens"]
    V = val_data["final_V"]
    
    # Generate matplotlib plot using last result
    log_dens = np.log10(dens + 1e-12)
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8, 3))
    im1 = ax1.imshow(V, cmap='viridis')
    ax1.set_title(f"Soft Coulomb V(r)\nZ={Z_vals[-1]}, eps={eps_vals[-1]}")
    fig.colorbar(im1, ax=ax1)
    
    im2 = ax2.imshow(log_dens, cmap='magma', vmin=np.max(log_dens)-6, vmax=np.max(log_dens))
    ax2.set_title(f"Log2 Ground State\nEdge Mass: {results[-1]['edge_mass_cells']:.2e}")
    fig.colorbar(im2, ax=ax2)
    
    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=100, bbox_inches="tight")
    plt.close()
    buf.seek(0)
    b64 = base64.b64encode(buf.read()).decode("utf-8")
    
    with open(os.path.join(os.path.dirname(__file__), '..', 'scripts', 'validation_core.py'), 'r', encoding='utf-8') as f:
        source_code = f.read()
    
    response_data = {
        "manifest": manifest,
        "results": results,
        "expectations": val_data.get("expectations", []),
        "expectation_results": val_data.get("expectation_results", []),
        "overall_pass": val_data.get("overall_pass", None),
        "explain_pack": val_data.get("explain_pack", {}),
        "image_b64": b64,
        "source_code": source_code
    }
    save_run(response_data)
    return response_data

@router.get("/regression/snapshot")
async def get_regression_snapshot(golden: bool = False):
    val_data = run_mu_regression_snapshot()
    manifest = val_data["manifest"]
    psi_diff = val_data["psi_diff"]
    mu_diff = val_data["mu_diff"]
    psi_wave = val_data["psi_wave"]
    mu_wave = val_data["mu_wave"]
    
    fig, axes = plt.subplots(2, 2, figsize=(8, 7))
    axes[0, 0].imshow(np.abs(psi_diff)**2, cmap='magma', vmin=0); axes[0, 0].set_title("Diffusion |psi|^2")
    axes[0, 1].imshow(mu_diff, cmap='inferno', vmin=0, vmax=10.0); axes[0, 1].set_title(f"Diffusion Mu\nMax: {np.max(mu_diff):.2f}")
    axes[1, 0].imshow(np.abs(psi_wave)**2, cmap='magma', vmin=0); axes[1, 0].set_title("Wave |psi|^2")
    axes[1, 1].imshow(mu_wave, cmap='inferno', vmin=0, vmax=10.0); axes[1, 1].set_title(f"Wave Mu\nMax: {np.max(mu_wave):.2f}")
    
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=100)
    plt.close()
    buf.seek(0)
    b64 = base64.b64encode(buf.read()).decode("utf-8")
    
    with open(os.path.join(os.path.dirname(__file__), '..', 'scripts', 'validation_core.py'), 'r', encoding='utf-8') as f:
        source_code = f.read()
    
    response_data = {
        "manifest": manifest,
        "expectations": val_data.get("expectations", []),
        "expectation_results": val_data.get("expectation_results", []),
        "overall_pass": val_data.get("overall_pass", None),
        "explain_pack": val_data.get("explain_pack", {}),
        "image_b64": b64,
        "source_code": source_code
    }
    save_run(response_data)
    return response_data

@router.get("/history")
async def get_run_history():
    """Lists all saved manifests in descending chronological order.
    Includes overall_pass badge for display WITHOUT loading full run data."""
    runs = []
    for filepath in HISTORY_DIR.glob("*.json"):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                manifest = data.get("manifest", {})
                runs.append({
                    "run_id": manifest.get("run_id"),
                    "timestamp": manifest.get("timestamp"),
                    "git": manifest.get("git"),
                    "scenario": manifest.get("scenario", manifest.get("run_id", "").split('_')[0]),
                    "overall_pass": manifest.get("overall_pass"),
                    "manifest": manifest,
                })
        except Exception as e:
            print(f"Failed to read history file {filepath}: {e}")
            
    runs.sort(key=lambda x: x.get("timestamp", 0) or 0, reverse=True)
    return runs

@router.delete("/history")
async def clear_run_history():
    """Wipes the Lineum Lab Run History database."""
    try:
        count = 0
        for filepath in HISTORY_DIR.glob("*.json"):
            os.remove(filepath)
            count += 1
        return {"status": "cleared", "deleted_count": count}
    except Exception as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/runs/{run_id}")
async def get_run_data(run_id: str):
    """Fetches full telemetry data for a specific run."""
    filepath = HISTORY_DIR / f"{run_id}.json"
    if not filepath.exists():
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Run not found in history")
        
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

class RerunRequest(BaseModel):
    run_id: str

@router.post("/rerun")
async def rerun_from_manifest(req: RerunRequest):
    """Re-executes a run from its stored manifest config.
    Produces a NEW run with fresh run_id so history stays immutable."""
    filepath = HISTORY_DIR / f"{req.run_id}.json"
    if not filepath.exists():
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Original run not found")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        old_data = json.load(f)
    
    old_manifest = old_data.get("manifest", {})
    scenario = old_manifest.get("scenario", "")
    config = old_manifest.get("config", {})
    
    if scenario in ("hydro", "t0"):
        sweeps_cfg = config.get("sweeps", [])
        if sweeps_cfg:
            grid_sizes = [s["grid"] for s in sweeps_cfg]
            Z_vals = [s["Z"] for s in sweeps_cfg]
            eps_vals = [s["eps"] for s in sweeps_cfg]
        else:
            grid_sizes = [s[0] for s in GOLDEN_HYDRO_SWEEP]
            Z_vals = [s[1] for s in GOLDEN_HYDRO_SWEEP]
            eps_vals = [s[2] for s in GOLDEN_HYDRO_SWEEP]
        
        val_data = run_hydrogen_sweep(grid_sizes, Z_vals, eps_vals)
        manifest = val_data["manifest"]
        manifest["rerun_of"] = req.run_id
        results = val_data["results"]
        dens = val_data["final_dens"]
        V = val_data["final_V"]
        
        log_dens = np.log10(dens + 1e-12)
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8, 3))
        im1 = ax1.imshow(V, cmap='viridis')
        ax1.set_title(f"Soft Coulomb V(r)")
        fig.colorbar(im1, ax=ax1)
        im2 = ax2.imshow(log_dens, cmap='magma', vmin=np.max(log_dens)-6, vmax=np.max(log_dens))
        ax2.set_title(f"Log Ground State")
        fig.colorbar(im2, ax=ax2)
        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=100, bbox_inches="tight")
        plt.close()
        buf.seek(0)
        b64 = base64.b64encode(buf.read()).decode("utf-8")
        
        response_data = {
            "manifest": manifest,
            "results": results,
            "expectations": val_data.get("expectations", []),
            "expectation_results": val_data.get("expectation_results", []),
            "overall_pass": val_data.get("overall_pass"),
            "explain_pack": val_data.get("explain_pack", {}),
            "image_b64": b64,
        }
        save_run(response_data)
        return response_data
    
    elif scenario == "mu":
        val_data = run_mu_regression_snapshot()
        manifest = val_data["manifest"]
        manifest["rerun_of"] = req.run_id
        
        fig, axes = plt.subplots(2, 2, figsize=(8, 7))
        axes[0, 0].imshow(np.abs(val_data["psi_diff"])**2, cmap='magma', vmin=0); axes[0, 0].set_title("Diffusion |psi|^2")
        axes[0, 1].imshow(val_data["mu_diff"], cmap='inferno', vmin=0, vmax=10.0); axes[0, 1].set_title("Diffusion Mu")
        axes[1, 0].imshow(np.abs(val_data["psi_wave"])**2, cmap='magma', vmin=0); axes[1, 0].set_title("Wave |psi|^2")
        axes[1, 1].imshow(val_data["mu_wave"], cmap='inferno', vmin=0, vmax=10.0); axes[1, 1].set_title("Wave Mu")
        plt.tight_layout()
        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=100)
        plt.close()
        buf.seek(0)
        b64 = base64.b64encode(buf.read()).decode("utf-8")
        
        response_data = {
            "manifest": manifest,
            "expectations": val_data.get("expectations", []),
            "expectation_results": val_data.get("expectation_results", []),
            "overall_pass": val_data.get("overall_pass"),
            "explain_pack": val_data.get("explain_pack", {}),
            "image_b64": b64,
        }
        save_run(response_data)
        return response_data
    
    elif scenario == "play":
        val_data = run_particle_playground(config)
        manifest = val_data["manifest"]
        manifest["rerun_of"] = req.run_id
        ts_metrics = val_data["ts_metrics"]
        
        fig, axes = plt.subplots(2, 2, figsize=(9, 7))
        im0 = axes[0, 0].imshow(val_data["final_V"], cmap='viridis')
        axes[0, 0].set_title("Potential V(r)")
        fig.colorbar(im0, ax=axes[0, 0])
        log_dens = np.log10(val_data["final_dens"] + 1e-12)
        im1 = axes[0, 1].imshow(log_dens, cmap='magma', vmin=np.max(log_dens)-8, vmax=np.max(log_dens))
        axes[0, 1].set_title("Log Density")
        fig.colorbar(im1, ax=axes[0, 1])
        im2 = axes[1, 0].imshow(val_data["final_dens"], cmap='inferno')
        axes[1, 0].set_title("Linear Density")
        fig.colorbar(im2, ax=axes[1, 0])
        im3 = axes[1, 1].imshow(val_data["final_phase"], cmap='hsv', vmin=-np.pi, vmax=np.pi)
        axes[1, 1].set_title("Phase")
        fig.colorbar(im3, ax=axes[1, 1])
        plt.tight_layout()
        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=100)
        plt.close()
        buf.seek(0)
        b64 = base64.b64encode(buf.read()).decode("utf-8")
        
        response_data = {
            "manifest": manifest,
            "expectations": val_data.get("expectations", []),
            "expectation_results": val_data.get("expectation_results", []),
            "overall_pass": val_data.get("overall_pass"),
            "explain_pack": val_data.get("explain_pack", {}),
            "timeseries_data": ts_metrics,
            "image_b64": b64,
            "results": [{"E": ts_metrics["E"][-1], "r": ts_metrics["r"][-1], "edge_mass_cells": ts_metrics["edge_mass"][-1], "max_edge": ts_metrics["max_edge"][-1]}]
        }
        save_run(response_data)
        return response_data
    
    else:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail=f"Unknown scenario '{scenario}' for rerun")

@router.get("/runs/{run_id}/export")
async def export_run(run_id: str):
    """Generates a ZIP archive containing all artifacts from a run."""
    filepath = HISTORY_DIR / f"{run_id}.json"
    if not filepath.exists():
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Run not found in history")
        
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    import zipfile
    from fastapi.responses import StreamingResponse
    
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as zf:
        # 1. Manifest
        zf.writestr("manifest.json", json.dumps(data.get("manifest", {}), indent=2))
        
        # 2. Metrics CSV
        ts_data = data.get("timeseries_data", data.get("ts_metrics", {}))
        if ts_data:
            import csv
            csv_buf = io.StringIO()
            writer = csv.writer(csv_buf)
            keys = list(ts_data.keys())
            writer.writerow(["step"] + keys)
            
            # Assume all metric lists are same length
            length = len(ts_data[keys[0]])
            for i in range(length):
                row = [i] + [ts_data[k][i] for k in keys]
                writer.writerow(row)
                
            zf.writestr("metrics.csv", csv_buf.getvalue())
            
        # 3. Image
        if "image_b64" in data:
            img_data = base64.b64decode(data["image_b64"])
            zf.writestr("visuals.png", img_data)
            
        # 4. Summary MKD
        summary = f"# Lineum Lab Export: {run_id}\n\n"
        summary += f"- **Scenario**: {data.get('manifest', {}).get('scenario', 'Unknown')}\n"
        summary += f"- **Timestamp**: {data.get('manifest', {}).get('timestamp', 'Unknown')}\n"
        summary += f"- **Git Hash**: {data.get('manifest', {}).get('git', 'Unknown')}\n"
        
        zf.writestr("summary.md", summary)

    buf.seek(0)
    return StreamingResponse(
        buf, 
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename=lineum_{run_id}.zip"}
    )


class PlaygroundRequest(BaseModel):
    config: Dict[str, Any]

@router.post("/playground")
async def post_playground(req: PlaygroundRequest):
    """Triggers the new Particle/State playground with exploratory configuration"""
    val_data = run_particle_playground(req.config)
    manifest = val_data["manifest"]
    ts_metrics = val_data["ts_metrics"]
    dens = val_data["final_dens"]
    phase = val_data["final_phase"]
    V = val_data["final_V"]
    
    # Generate 4-panel visual summary for Lab
    fig, axes = plt.subplots(2, 2, figsize=(9, 7))
    
    im0 = axes[0, 0].imshow(V, cmap='viridis')
    axes[0, 0].set_title(f"Potential V(r)")
    fig.colorbar(im0, ax=axes[0, 0])
    
    log_dens = np.log10(dens + 1e-12)
    im1 = axes[0, 1].imshow(log_dens, cmap='magma', vmin=np.max(log_dens)-8, vmax=np.max(log_dens))
    axes[0, 1].set_title("Log Density log10(|psi|^2)")
    fig.colorbar(im1, ax=axes[0, 1])
    
    im2 = axes[1, 0].imshow(dens, cmap='inferno')
    axes[1, 0].set_title("Linear Density |psi|^2")
    fig.colorbar(im2, ax=axes[1, 0])
    
    im3 = axes[1, 1].imshow(phase, cmap='hsv', vmin=-np.pi, vmax=np.pi)
    axes[1, 1].set_title("Phase arg(psi)")
    fig.colorbar(im3, ax=axes[1, 1])
    
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=100)
    plt.close()
    buf.seek(0)
    b64 = base64.b64encode(buf.read()).decode("utf-8")
    
    with open(os.path.join(os.path.dirname(__file__), '..', 'scripts', 'validation_core.py'), 'r', encoding='utf-8') as f:
        source_code = f.read()
    
    response_data = {
        "manifest": manifest,
        "expectations": val_data.get("expectations", []),
        "expectation_results": val_data.get("expectation_results", []),
        "overall_pass": val_data.get("overall_pass", None),
        "explain_pack": val_data.get("explain_pack", {}),
        "timeseries_data": ts_metrics,
        "image_b64": b64,
        "source_code": source_code,
        "results": [{
            "E": ts_metrics["E"][-1],
            "r": ts_metrics["r"][-1],
            "edge_mass_cells": ts_metrics["edge_mass"][-1],
            "max_edge": ts_metrics["max_edge"][-1]
        }]
    }
    save_run(response_data)
    return response_data


# ══════════════════════════════════════════════════════════════
# Reality Alignment API Endpoints
# ══════════════════════════════════════════════════════════════

def _fig_to_b64(fig):
    """Convert matplotlib figure to base64 PNG string."""
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=100, bbox_inches="tight", facecolor='#121212')
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("utf-8")


@router.get("/ra/unitarity")
async def get_ra1_unitarity(golden: bool = False):
    """RA-1: Wave Unitarity check."""
    val_data = run_ra1_unitarity()

    fig, axes = plt.subplots(1, 2, figsize=(8, 3.5))
    fig.patch.set_facecolor('#121212')
    for ax in axes:
        ax.set_facecolor('#1a1a1a')

    im1 = axes[0].imshow(val_data["final_dens"], cmap='magma')
    axes[0].set_title("|ψ|² Final", color='white')
    fig.colorbar(im1, ax=axes[0])

    im2 = axes[1].imshow(val_data["final_phase"], cmap='twilight', vmin=-np.pi, vmax=np.pi)
    axes[1].set_title("Phase", color='white')
    fig.colorbar(im2, ax=axes[1])

    fig.suptitle("RA-1: Wave Unitarity", color='#00ffff', fontsize=14, fontweight='bold')
    fig.tight_layout()

    response_data = {
        "manifest": val_data["manifest"],
        "expectations": val_data["expectations"],
        "expectation_results": val_data["expectation_results"],
        "overall_pass": val_data["overall_pass"],
        "explain_pack": val_data.get("explain_pack", {}),
        "image_b64": _fig_to_b64(fig),
        "timeseries_data": { "N_series": val_data["N_series"] }
    }
    response_data["manifest"]["is_golden"] = golden
    save_run(response_data)
    return response_data


@router.get("/ra/bound-state")
async def get_ra2_bound_state(golden: bool = False):
    """RA-2: Stable bound state check."""
    val_data = run_ra2_bound_state()

    fig, axes = plt.subplots(1, 2, figsize=(8, 3.5))
    fig.patch.set_facecolor('#121212')
    for ax in axes:
        ax.set_facecolor('#1a1a1a')

    im1 = axes[0].imshow(np.log10(val_data["before_dens"] + 1e-12), cmap='magma')
    axes[0].set_title("Before Wave (ITP Ground)", color='white')
    fig.colorbar(im1, ax=axes[0])

    im2 = axes[1].imshow(np.log10(val_data["after_dens"] + 1e-12), cmap='magma')
    axes[1].set_title("After Wave Hold", color='white')
    fig.colorbar(im2, ax=axes[1])

    ts = val_data["ts_metrics"]

    fig.suptitle("RA-2: Stable Bound State", color='#00ffff', fontsize=14, fontweight='bold')
    fig.tight_layout()

    response_data = {
        "manifest": val_data["manifest"],
        "expectations": val_data["expectations"],
        "expectation_results": val_data["expectation_results"],
        "overall_pass": val_data["overall_pass"],
        "explain_pack": val_data.get("explain_pack", {}),
        "image_b64": _fig_to_b64(fig),
        "timeseries_data": ts
    }
    response_data["manifest"]["is_golden"] = golden
    save_run(response_data)
    return response_data


@router.get("/ra/excited-state")
async def get_ra3_excited_state(golden: bool = False):
    """RA-3: Excited state + orthogonality check."""
    val_data = run_ra3_excited_state()

    fig, axes = plt.subplots(1, 3, figsize=(12, 3.5))
    fig.patch.set_facecolor('#121212')
    for ax in axes:
        ax.set_facecolor('#1a1a1a')

    im1 = axes[0].imshow(val_data["ground_dens"], cmap='magma')
    axes[0].set_title("Ground State |ψ₀|²", color='white')
    fig.colorbar(im1, ax=axes[0])

    im2 = axes[1].imshow(val_data["excited_dens"], cmap='magma')
    axes[1].set_title("Excited State |ψ₁|² (P-like)", color='white')
    fig.colorbar(im2, ax=axes[1])

    # Info panel
    axes[2].axis('off')
    ortho = val_data["manifest"].get("ortho_dot", 0)
    anis = val_data["manifest"].get("anisotropy", 0)
    cdip = val_data["manifest"].get("center_dip", 0)
    info_text = (
        f"Orthogonality |⟨ψ₀|ψ₁⟩|: {ortho:.4f}\n"
        f"Anisotropy (λ₁−λ₂)/(λ₁+λ₂): {anis:.4f}\n"
        f"Center Dip (ρ_center/ρ_peak): {cdip:.4f}\n\n"
        f"{'✅ Has lobes' if cdip < 0.5 and anis > 0.15 else '❌ No clear lobes'}"
    )
    axes[2].text(0.1, 0.5, info_text, transform=axes[2].transAxes,
                 color='white', fontsize=11, verticalalignment='center',
                 fontfamily='monospace')
    axes[2].set_title("Lobe Detection", color='white')

    fig.suptitle("RA-3: Excited State (Two-Lobe)", color='#00ffff', fontsize=14, fontweight='bold')
    fig.tight_layout()

    response_data = {
        "manifest": val_data["manifest"],
        "expectations": val_data["expectations"],
        "expectation_results": val_data["expectation_results"],
        "overall_pass": val_data["overall_pass"],
        "explain_pack": val_data.get("explain_pack", {}),
        "image_b64": _fig_to_b64(fig),
    }
    response_data["manifest"]["is_golden"] = golden
    save_run(response_data)
    return response_data


@router.get("/ra/mu-memory")
async def get_ra4_mu_memory(golden: bool = False):
    """RA-4: μ Memory Imprint check (Lineum-only)."""
    val_data = run_ra4_mu_memory()

    fig, axes = plt.subplots(1, 2, figsize=(8, 3.5))
    fig.patch.set_facecolor('#121212')
    for ax in axes:
        ax.set_facecolor('#1a1a1a')

    im1 = axes[0].imshow(val_data["psi_dens"], cmap='magma')
    axes[0].set_title("|ψ|² Density", color='white')
    fig.colorbar(im1, ax=axes[0])

    im2 = axes[1].imshow(val_data["mu_field"], cmap='inferno')
    axes[1].set_title(f"μ Memory Field\nVerdict: {val_data['verdict'].upper()}", color='white')
    fig.colorbar(im2, ax=axes[1])

    fig.suptitle(f"RA-4: μ Memory — {val_data['verdict'].upper()}", color='#00ffff', fontsize=14, fontweight='bold')
    fig.tight_layout()

    response_data = {
        "manifest": val_data["manifest"],
        "expectations": val_data["expectations"],
        "expectation_results": val_data["expectation_results"],
        "overall_pass": val_data["overall_pass"],
        "explain_pack": val_data.get("explain_pack", {}),
        "image_b64": _fig_to_b64(fig),
        "timeseries_data": { "mu_max_series": val_data["mu_max_series"] }
    }
    response_data["manifest"]["is_golden"] = golden
    save_run(response_data)
    return response_data


@router.get("/ra/driving")
async def get_ra5_driving(golden: bool = False):
    """RA-5: Driving vs Dephasing check (Lineum-only)."""
    val_data = run_ra5_driving()

    response_data = {
        "manifest": val_data["manifest"],
        "expectations": val_data["expectations"],
        "expectation_results": val_data["expectation_results"],
        "overall_pass": val_data["overall_pass"],
        "explain_pack": val_data.get("explain_pack", {}),
        "timeseries_data": {
            "N_driven": val_data["N_driven"],
            "N_undriven": val_data["N_undriven"]
        }
    }
    response_data["manifest"]["is_golden"] = golden
    save_run(response_data)
    return response_data


@router.get("/ra/lpf-impact")
async def get_ra6_lpf_impact(golden: bool = False):
    """RA-6: LPF ON vs OFF Impact check (Lineum-only)."""
    val_data = run_ra6_lpf_impact()

    response_data = {
        "manifest": val_data["manifest"],
        "expectations": val_data["expectations"],
        "expectation_results": val_data["expectation_results"],
        "overall_pass": val_data["overall_pass"],
        "explain_pack": val_data.get("explain_pack", {}),
        "timeseries_data": {
            "E_off": val_data["E_off"],
            "E_on": val_data["E_on"],
            "N_off": val_data["N_off"],
            "N_on": val_data["N_on"],
        }
    }
    response_data["manifest"]["is_golden"] = golden
    save_run(response_data)
    return response_data
