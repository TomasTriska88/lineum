import json
import os
from datetime import datetime, timezone

RUN_DIR = r"output_wp/runs/spec6_false_s41_20260214_101645"
MANIFEST_NAME = "spec6_false_s41_manifest.json"
MANIFEST_PATH = os.path.join(RUN_DIR, MANIFEST_NAME)

def patch_manifest():
    if not os.path.exists(MANIFEST_PATH):
        print(f"Error: Manifest not found at {MANIFEST_PATH}")
        return

    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Invariants to add
    data["invariants"] = {
        "dim": "2D",
        "bcs": "periodic",
        "precision": "float64"
    }
    
    # Add topo stride to logging config (Variant B+)
    if "logging" not in data:
        data["logging"] = {}
    data["logging"]["topo_log_stride"] = 25

    # Provenance
    data["provenance"] = {
        "patched_by": "whitepaper_contract",
        "patched_at": datetime.now(timezone.utc).isoformat(),
        "reason": "add invariants and topo log stride for contract suite"
    }

    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    
    print(f"Success: Patched {MANIFEST_PATH} with invariants and provenance.")

if __name__ == "__main__":
    patch_manifest()
