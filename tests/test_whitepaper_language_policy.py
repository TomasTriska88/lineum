import pytest
from pathlib import Path
import re

def test_whitepapers_contain_no_czech(project_root):
    """
    Ensure no whitepaper documents contain Czech words or diacritics.
    Rule: 'All whitepaper content must be English only (no Czech).'
    """
    whitepapers_dir = Path(project_root) / "whitepapers"
    assert whitepapers_dir.exists(), "whitepapers directory not found"
    
    # Check all markdown files in the whitepapers folder
    md_files = list(whitepapers_dir.glob("**/*.md"))
    
    czech_stop_words = [
        "že", "ať", "prosím", "přečteno", "výstup", "ano", "proč", 
        "jak", "kdy", "kdo", "tento", "proto", "toto",
        "je", "jsou", "byl", "bude", "jako", "když", "nebo"
    ]
    
    errors = []
    
    for md_file in md_files:
        if md_file.name in ["README.md", "TEMPLATE.md", "lina_manifest.md", "LINA_PERSONA.md"]:
            continue
            
        content = md_file.read_text(encoding="utf-8")
        lines = content.splitlines()
        for i, line in enumerate(lines, 1):
            line_lower = line.lower()
            for word in czech_stop_words:
                pattern = r'\b' + word + r'\b'
                if re.search(pattern, line_lower):
                    errors.append(f"{md_file.name}:{i} contains Czech word '{word}' -> '{line.strip()}'")

    assert not errors, "Whitepapers must be strictly English. Found violations:\n" + "\n".join(errors)
