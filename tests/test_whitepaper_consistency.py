import re
from pathlib import Path

def test_no_placeholders_in_whitepaper(project_root):
    """
    Checks that lineum-core.md does not contain any __REPLACE_WITH_...__ placeholders.
    """
    wp_path = Path(project_root) / "whitepapers" / "lineum-core.md"
    assert wp_path.exists(), f"Whitepaper not found at {wp_path}"
    
    content = wp_path.read_text(encoding="utf-8")
    placeholders = re.findall(r'__REPLACE_WITH_[A-Z_]+__', content)
    
    assert not placeholders, f"Found unresolved placeholders in whitepaper: {placeholders}"

def test_all_validated_claims_have_keys(project_root):
    """
    Checks that all [VALIDATED] claims in Appendix G have a corresponding contract key in the table.
    """
    wp_path = Path(project_root) / "whitepapers" / "lineum-core.md"
    content = wp_path.read_text(encoding="utf-8")
    
    # Very basic check: just ensure there are no placeholders and [VALIDATED] rows don't say N/A for keys
    # Extract the Appendix G table
    in_table = False
    validated_rows = []
    
    for line in content.splitlines():
        if "## Appendix G — Claim–Contract Map" in line:
            in_table = True
            continue
        if in_table and "## " in line and "Appendix G" not in line:
            break
            
        if in_table and "[VALIDATED]" in line:
            validated_rows.append(line)
            
    assert len(validated_rows) > 0, "No [VALIDATED] rows found in Appendix G"
    
    for row in validated_rows:
        parts = [p.strip() for p in row.split('|')]
        if len(parts) >= 5:
            contract_key_col = parts[4] # Index 4 because parts[0] is empty from leading |
            assert "N/A" not in contract_key_col, f"Validated claim missing contract key: {row}"
            assert contract_key_col != "", f"Validated claim missing contract key: {row}"
