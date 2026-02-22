import sys
import json
import re
from pathlib import Path

def main():
    root = Path(__file__).parent.parent if 'scripts' in Path(__file__).parts else Path(__file__).parent
    wp_path = root / 'whitepapers' / 'lineum-core.md'
    suite_path = root / 'contracts' / 'lineum-core-1.0.18-core.contract.json'

    if not suite_path.exists():
        print(f"FAIL: Suite not found at {suite_path}")
        sys.exit(1)

    with open(suite_path, 'r', encoding='utf-8') as f:
        contract = json.load(f)

    canon = next((p for p in contract['profiles'] if p['name'] == 'canonical'), None)
    if not canon:
        print("FAIL: No canonical profile found in contract suite.")
        sys.exit(1)

    anchors = canon['checks'].get('numerical_anchors', {})

    with open(wp_path, 'r', encoding='utf-8') as f:
        wp_lines = f.readlines()

    in_app_g = False
    app_g_keys = set()
    found_mismatches = []
    
    for i, line in enumerate(wp_lines):
        if "Appendix G" in line:
            in_app_g = True
            
        if in_app_g and line.startswith("## Appendix H"):
            break
        
        if in_app_g and line.strip().startswith('|') and '[VALIDATED]' in line:
            codes = re.findall(r'`([^`]+)`', line)
            
            mapped = False
            for code in codes:
                if code in anchors:
                    mapped = True
                    app_g_keys.add(code)
                    
            if not mapped:
                found_mismatches.append(f"Line {i+1}: Could not find valid contract key in suite mapping. Found {codes}. Row: {line.strip()}")
                
    missing_in_wp = [k for k in anchors.keys() if k not in app_g_keys and anchors[k].get("severity") != "info"]

    if found_mismatches:
        print("FAIL: [VALIDATED] claims in Appendix G have mismatched or missing suite keys:")
        for m in found_mismatches:
            print("  ", m)
            
    if missing_in_wp:
        print("FAIL: Contract suite has MUST-HAVE anchors not mapped to a [VALIDATED] claim in Appendix G:")
        for k in missing_in_wp:
            print(f"   {k}")
            
    if found_mismatches or missing_in_wp:
        sys.exit(1)
        
    print("PASS: Core mapping check. All [VALIDATED] claims map perfectly to whitepaper_contract_suite.json.")

if __name__ == '__main__':
    main()
