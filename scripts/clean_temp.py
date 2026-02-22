import os
import shutil
import glob
from pathlib import Path

def clean_temp_dir():
    root = Path(__file__).parent.parent
    temp_dir = root / "temp"
    
    if not temp_dir.exists():
        temp_dir.mkdir(parents=True, exist_ok=True)
        print(f"Created {temp_dir}")
        return
        
    cleaned = 0
    # Wipe temp/* if safe (all files inside temp are transient)
    for item in temp_dir.iterdir():
        if item.name == ".gitkeep":
             continue
        try:
            if item.is_file() or item.is_symlink():
                item.unlink()
            elif item.is_dir():
                shutil.rmtree(item)
            cleaned += 1
        except Exception as e:
            print(f"Failed to delete {item}: {e}")
            
    print(f"Auto-cleaned {cleaned} items from {temp_dir}")

if __name__ == "__main__":
    clean_temp_dir()
