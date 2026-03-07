import os
import json
from pathlib import Path

def test_audit_suite_header_fields():
    """
    Ensure that the generated whitepaper_contract_suite.json has dynamic 
    tool_version, git_commit, and git_branch fields.
    """
    suite_path = Path(__file__).parent.parent / "output_wp" / "runs" / "_whitepaper_contract" / "whitepaper_contract_suite.json"
    
    # If the suite hasn't been generated yet, skip the test or fail it depending on CI.
    # For now, we assert it exists if we are running the test suite after generation.
    if not suite_path.exists():
        pytest.skip(f"No audit suite found at {suite_path}")

    with open(suite_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Convert to list if it's a single dict (though the generator outputs a dict with 'header')
    audits = [data] if isinstance(data, dict) and "header" in data else data

    for audit in audits:
        header = audit.get("header", {})
        
        tool_version = header.get("tool_version")
        git_commit = header.get("git_commit")
        git_branch = header.get("git_branch")
        # Use "MISSING" as default to verify the key exists even if the value is null
        release_tag = header.get("release_tag", "MISSING")

        assert tool_version, "tool_version is missing or empty"
        assert tool_version not in ["1.0.14-core", "unknown"], f"tool_version failed to generate properly: {tool_version}"
        assert tool_version.startswith("release:") or tool_version == "unreleased", f"tool_version has wrong format: {tool_version}"

        assert git_commit, "git_commit is missing or empty"
        assert git_commit != "unknown", "git_commit failed to generate (got 'unknown')"
        assert len(git_commit) == 40, f"git_commit should be a 40-char SHA, got {git_commit}"

        assert git_branch, "git_branch is missing or empty"
        assert git_branch != "unknown", "git_branch failed to generate (got 'unknown')"
        
        assert release_tag != "MISSING", "release_tag key must be present in header (even if null)"
        
        eq_fingerprint = header.get("equation_fingerprint")
        codebase_sha = audit.get("fingerprints", {}).get("codebase_sha256")
        assert eq_fingerprint, "equation_fingerprint is missing"
        assert eq_fingerprint != "unknown", "equation_fingerprint failed to generate"
        assert eq_fingerprint != codebase_sha, "equation_fingerprint must be a distinct serialization hash of the canonical equation/config (e.g. expected_hash), not just the codebase contents"

def test_metric_traceability():
    suite_path = Path(__file__).parent.parent / "output_wp" / "runs" / "_whitepaper_contract" / "whitepaper_contract_suite.json"
    if not suite_path.exists():
        pytest.skip(f"No audit suite found at {suite_path}")

    with open(suite_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    audits = [data] if isinstance(data, dict) and "header" in data else data
    
    for audit in audits:
        metric_spec = audit.get("metric_spec", {})
        assert len(metric_spec) > 0, "metric_spec is empty"
        
        # Verify traceability format
        for metric_id, spec in metric_spec.items():
            assert "computed_in" in spec, f"Metric {metric_id} is missing 'computed_in' traceability."
            assert ":" in spec["computed_in"], f"Metric {metric_id} computed_in should follow 'file:function' format (got '{spec['computed_in']}')."
            
        # Verify every derived or numerical_anchor check is documented in metric_spec
        for run in audit.get("runs", []):
            for check in run.get("checks", []):
                chk_id = check.get("id", "")
                if "anchor." in chk_id:
                    # e.g. "canonical.anchor.f0_mean_hz" or "baseline.anchor.sbr_mean"
                    metric_name = chk_id.split("anchor.")[-1]
                    assert metric_name in metric_spec, f"Anchor '{metric_name}' used in contract but not documented in metric_spec!"
                elif "derived." in chk_id:
                    metric_name = chk_id.split("derived.")[-1]
                    assert metric_name in metric_spec, f"Derived metric '{metric_name}' used in contract but not documented in metric_spec!"

if __name__ == "__main__":
    import pytest
    pytest.main([__file__])
