import pytest
from pathlib import Path
import re

def test_todo_contains_no_czech(project_root):
    """
    Ensure todo.md contains no Czech words or diacritics. 
    Rule: 'All TODO content must be English only (no Czech).'
    """
    todo_path = Path(project_root) / "todo.md"
    assert todo_path.exists(), "todo.md not found"
    
    content = todo_path.read_text(encoding="utf-8")
    
    # Check for diacritics (lowercase and uppercase representation).
    # Allowed symbols: standard overlapping characters are removed or checked specifically.
    czech_chars = set("áčďéěíňóřšťúůýžÁČĎÉĚÍŇÓŘŠŤÚŮÝŽ")
    
    found_chars = set(c for c in content if c in czech_chars)
    assert not found_chars, f"todo.md must be English only, found Czech diacritics: {found_chars}"
    
    # Check for common Czech words - surrounded by boundaries
    # Avoid words that overlap with English like "to", "ten", "ne"
    czech_words = ["že", "ať", "prosím", "přečteno", "výstup", "ano", "proč", "jak", "co", "kde", "kdy", "kdo", "tento"]
    
    content_lower = content.lower()
    for word in czech_words:
        # Use regex border to avoid matching substrings like "to" inside "today"
        pattern = r'\b' + word + r'\b'
        matches = re.findall(pattern, content_lower)
        assert not matches, f"todo.md must be English only, found common Czech word '{word}'"
