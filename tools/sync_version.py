import re
import sys
import os
import argparse
from pathlib import Path

# Files to update and their regex patterns
FILES_TO_UPDATE = {
    "CITATION.cff": [
        (r'version:\s+v\d+\.\d+\.\d+(-core)?', lambda m: f"version: {m.group(0).split(' ')[1].split('-')[0].replace('v', 'v') if not '-core' in m.group(0) else 'v' + '__CANONICAL_VERSION__-core'}"), # Will be replaced dynamically
    ],
    "README.md": [
        (r'v\d+\.\d+\.\d+', '__CANONICAL_VERSION__'),
    ],
    "todo.md": [
       (r'v\d+\.\d+\.\d+(-core)?', '__CANONICAL_VERSION__')
    ],
    "portal/static/portal_params.json": [
       (r'"version":\s*"v1\.\d+\.\d+-core"', '"version": "v__CANONICAL_VERSION__-core"')
    ],
    "portal/src/lib/data/core/lineum.py": [
       (r'"version":\s*"v1\.\d+\.\d+-core"', '"version": "v__CANONICAL_VERSION__-core"')
    ]
}


def update_file(filepath, patterns_and_replacements, canonical_version, core_version):
    path = Path(filepath)
    if not path.exists():
        print(f"File not found: {filepath}")
        return False
        
    try:
        content = path.read_text(encoding="utf-8")
        new_content = content
        
        for pattern, replacement in patterns_and_replacements:
            # Handle dynamic lambda replacements or raw strings
            if callable(replacement):
                # We need a hacky way to pass the dynamic version if lambda is used
                pass
            
            # Simple string replacement logic with tokens
            val = replacement
            if isinstance(val, str):
                val = val.replace('__CANONICAL_VERSION__', canonical_version)
            
            # Special case for CITATION.cff core version
            if "CITATION.cff" in filepath:
                new_content = re.sub(r'version:\s+v\d+\.\d+\.\d+(-core)?', f'version: {core_version}', new_content)
            else:
                new_content = re.sub(pattern, val, new_content)
            
        if new_content != content:
            path.write_text(new_content, encoding="utf-8")
            print(f"Updated: {filepath}")
            return True
        else:
            print(f"No changes needed: {filepath}")
            return False
            
    except Exception as e:
        print(f"Error updating {filepath}: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Synchronize Lineum version string across the repository.")
    parser.add_argument("version", help="The new version to set (e.g., v1.1.0)")
    args = parser.parse_args()

    canonical_version = args.version
    if not canonical_version.startswith("v"):
        canonical_version = f"v{canonical_version}"
        
    core_version = f"{canonical_version}-core"
    
    print(f"Syncing version to: {canonical_version} (Core: {core_version})")
    
    changes_made = False
    for filename, patterns in FILES_TO_UPDATE.items():
        if update_file(filename, patterns, canonical_version, core_version):
            changes_made = True
            
    if changes_made:
        print("Versions synchronized successfully.")
    else:
        print("All files are already up to date.")

if __name__ == "__main__":
    main()
