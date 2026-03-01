import pytest
import tempfile
from pathlib import Path
import re
import os
import sys

# Import the module to test (requires modifying sys.path temporarily to find tools/)
tools_dir = Path(__file__).parent.parent / "tools"
sys.path.append(str(tools_dir))
try:
    from sync_version import update_file
except ImportError:
    pytest.skip("Could not import sync_version.py for testing")

def test_sync_version_readme(tmp_path):
    """Test replacing standard CANONICAL version in a standard file like README.md"""
    # Setup mock file
    file_path = tmp_path / "README.md"
    file_path.write_text("Hello Lineum v1.0.18 is great.", encoding="utf-8")
    
    # Define rules
    patterns = [(r'v\d+\.\d+\.\d+', '__CANONICAL_VERSION__')]
    
    # Execute update
    result = update_file(str(file_path), patterns, "v2.0.0", "v2.0.0-core")
    
    # Assert
    assert result is True, "Script should have reported making changes."
    content = file_path.read_text(encoding="utf-8")
    assert "Hello Lineum v2.0.0 is great." in content
    
def test_sync_version_citation(tmp_path):
    """Test replacing formatted CORE version in CITATION.cff"""
    # Setup mock file
    file_path = tmp_path / "CITATION.cff"
    file_path.write_text("version: v1.0.18-core\ntitle: Lineum", encoding="utf-8")
    
    # Define rules (citation has special file-level condition inside update_file)
    patterns = [(r'version:\s+v\d+\.\d+\.\d+(-core)?', lambda m: "dynamic_wont_be_used")] 
    
    # Execute update
    result = update_file(str(file_path), patterns, "v2.0.5", "v2.0.5-core")
    
    # Assert
    assert result is True
    content = file_path.read_text(encoding="utf-8")
    assert "version: v2.0.5-core" in content
    
def test_sync_version_no_changes(tmp_path):
    """Test script exits correctly when no matching version lines exist or when already synced"""
    file_path = tmp_path / "todo.md"
    file_path.write_text("version is v1.5.0-core, all good", encoding="utf-8")
    
    patterns = [(r'v\d+\.\d+\.\d+(-core)?', '__CANONICAL_VERSION__')]
    
    # It should report as False (no changes needed) because the content is already v1.5.0-core
    result = update_file(str(file_path), patterns, "v1.5.0", "v1.5.0-core")
    # Actually wait, our script replaces __CANONICAL_VERSION__ which is v1.5.0, so it would replace v1.5.0-core with v1.5.0 
    # To test pure "no changes", the file must match the replacement exactly.
    
    file_path2 = tmp_path / "README.md"
    file_path2.write_text("Lineum v1.5.0", encoding="utf-8")
    result2 = update_file(str(file_path2), patterns, "v1.5.0", "v1.5.0-core")
    
    assert result2 is False, "Script should report no changes made."
    content = file_path2.read_text(encoding="utf-8")
    assert "Lineum v1.5.0" in content
