import os
import json
import pytest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
AI_INDEX_PATH = PROJECT_ROOT / "portal" / "src" / "lib" / "data" / "ai_index.json"
CHAT_TS_PATH = PROJECT_ROOT / "portal" / "src" / "lib" / "server" / "chat.ts"
PERSONA_PATH = PROJECT_ROOT / "portal" / "src" / "lib" / "data" / "core" / "LINA_PERSONA.md"

def test_track_separation_policy_in_index():
    if not AI_INDEX_PATH.exists():
        pytest.skip("ai_index.json missing")
        
    index_data = json.loads(AI_INDEX_PATH.read_text(encoding="utf-8"))
    
    for item in index_data:
        if "whitepapers" not in item.get("path", ""):
            continue
            
        name = item.get("name", "")
        track = item.get("track", "")
        status = item.get("status", "")
        
        if name.startswith("lineum-core"):
            assert track == "core", f"Expected track 'core' for {name}, got {track}"
        elif name.startswith("lineum-exp"):
            assert track == "exp", f"Expected track 'exp' for {name}, got {track}"
            assert "OUT OF CORE SCOPE" in status, f"Missing strict boundary status in {name}"
        elif name.startswith("lineum-extension"):
            assert track == "extension", f"Expected track 'extension' for {name}, got {track}"
            assert "OUT OF CORE SCOPE" in status, f"Missing strict boundary status in {name}"

def test_prompt_contains_explicit_track_rules():
    assert CHAT_TS_PATH.exists(), "chat.ts missing"
    chat_content = CHAT_TS_PATH.read_text(encoding="utf-8")
    
    # Check that the strict boundary explicitly exists in prompt setup
    assert "TRACK SEPARATION POLICY" in chat_content
    assert "OUT OF CORE SCOPE" in chat_content
    assert "whitepaper_contract_suite.json" in chat_content

    assert PERSONA_PATH.exists(), "LINA_PERSONA.md missing"
    persona_content = PERSONA_PATH.read_text(encoding="utf-8")
    assert "OUT OF CORE SCOPE" in persona_content
