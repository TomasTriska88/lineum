import os
import json
import pytest
from pathlib import Path

# Need to be able to find the portal's compiled ai_index.json
PROJECT_ROOT = Path(__file__).resolve().parent.parent
AI_INDEX_PATH = PROJECT_ROOT / "portal" / "src" / "lib" / "data" / "ai_index.json"

def test_portal_whitepapers_ingestion():
    if not AI_INDEX_PATH.exists():
        pytest.skip("ai_index.json does not exist. Please run 'npm run stage' or ensure sync-data.js has executed.")
        
    index_data = json.loads(AI_INDEX_PATH.read_text(encoding="utf-8"))
    
    # Get all markdown files that actually exist in the physical directory
    whitepapers_dir = PROJECT_ROOT / "whitepapers"
    expected_files = [f.name for f in whitepapers_dir.glob("*.md")]
    
    # Filter the index data to find what was ingested
    ingested_whitepapers = [item["name"] for item in index_data if "whitepapers" in item.get("path", "")]
    
    for expected in expected_files:
        assert expected in ingested_whitepapers, f"Whitepaper missing from portal index: {expected}"
