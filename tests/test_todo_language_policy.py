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
    # Check for diacritics and words line by line for better error reporting
    czech_chars = set("áčďéěíňóřšťúůýžÁČĎÉĚÍŇÓŘŠŤÚŮÝŽ")
    czech_words = ["že", "ať", "prosím", "přečteno", "výstup", "ano", "proč", "jak", "co", "kde", "kdy", "kdo", "tento"]
    
    errors = []
    lines = content.splitlines()
    
    for i, line in enumerate(lines, 1):
        # 1. Check diacritics
        found_chars = set(c for c in line if c in czech_chars)
        if found_chars:
            errors.append(f"Line {i}: Found Czech diacritics {found_chars} -> '{line.strip()}'")
            
        # 2. Check complete words
        line_lower = line.lower()
        for word in czech_words:
            pattern = r'\b' + word + r'\b'
            if re.search(pattern, line_lower):
                errors.append(f"Line {i}: Found common Czech word '{word}' -> '{line.strip()}'")
                
    assert not errors, "todo.md must be English only. Found violations:\n" + "\n".join(errors)
