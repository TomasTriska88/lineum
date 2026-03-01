import json
import re
import pytest
from pathlib import Path

def test_contract_version_matches_whitepaper_header(project_root):
    """
    Extracts the contract ID and version from lineum-core.md and ensures
    it matches the suite output.
    """
    wp_path = Path(project_root) / "whitepapers" / "1-core" / "01-core-lineum.md"
    suite_json_path = Path(project_root) / "output_wp" / "runs" / "_whitepaper_contract" / "whitepaper_contract_suite.json"
    
    # 1. Parse whitepaper for contract info
    content = wp_path.read_text(encoding="utf-8")
    
    # Looking for: **Contract evidence (core v1.0.18-core).** ... contract suite `lineum-core-1.0.18-core` (contract_version `1.1.5`)
    match_id = re.search(r'contract suite `([^`]+)`', content)
    match_ver = re.search(r'\(contract_version `([^`]+)`\)', content)
    
    assert match_id, "Could not find expected contract suite ID in whitepaper (e.g., `lineum-core-1.0.18-core`)"
    assert match_ver, "Could not find expected contract_version in whitepaper (e.g., `1.1.5`)"
    
    wp_contract_id = match_id.group(1)
    wp_contract_ver = match_ver.group(1)
    
    # 2. Find the referenced suite JSON file
    if not suite_json_path.exists():
        pytest.skip(f"Suite JSON file not found at {suite_json_path}. Cannot verify version consistency.")
    
    # 3. Read suite JSON and verify
    suite_data = json.loads(suite_json_path.read_text(encoding="utf-8"))
    header = suite_data.get("header", {})
    
    assert header.get("contract_id") == wp_contract_id, f"Contract ID mismatch: {header.get('contract_id')} != {wp_contract_id}"
    assert header.get("contract_version") == wp_contract_ver, f"Contract Version mismatch: {header.get('contract_version')} != {wp_contract_ver}"
