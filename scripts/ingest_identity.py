import argparse
import os
import zipfile
import json
import uuid
import datetime
import numpy as np
import sys
import re

# Add core to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from lineum_core.math import CoreConfig, step_core
from routing_backend.text_to_wave_encoder import TextToWaveEncoder

GRID_SIZE = 64

def _chunk_text(text, target_tokens=600):
    """
    Very rough character-based approximation of token chunking respecting paragraphs.
    1 token ~= 4 chars broadly. So 600 tokens ~= 2400 chars.
    """
    target_chars = target_tokens * 4
    paragraphs = text.split("\\n\\n")
    chunks = []
    current_chunk = ""
    
    for p in paragraphs:
        if len(current_chunk) + len(p) < target_chars:
            current_chunk += p + "\\n\\n"
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = p + "\\n\\n"
            
    if current_chunk:
        chunks.append(current_chunk.strip())
        
    return chunks

def _categorize_chunk(chunk_text):
    """
    Category A (Physics Core): Ontology, hypotheses, universal rules, math, mechanics.
    Category B/C (Context): Temporal facts, chit-chat, simple Q&A.
    """
    # Deterministic regex categorization first
    physics_keywords = [
        "physics", "ontology", "hypothesis", "equation", "mechanics", 
        "lineum", "tensor", "gradient", "manifold", "thermodynamics",
        "psi", "phi", "mu", "kappa", "determinism", "emergence", "fluid"
    ]
    
    chunk_lower = chunk_text.lower()
    score = sum(1 for kw in physics_keywords if kw in chunk_lower)
    
    if score >= 2:
        return "A"
    else:
        return "B"

def build_identity_pipeline(zip_path, identifier=None):
    """
    The strict automated pipeline for ingesting user chat histories into a native Lineum HDD.
    """
    if identifier is None:
        identifier = str(uuid.uuid4())[:8]

    out_dir = f"artifacts/identity_{identifier}"
    os.makedirs(out_dir, exist_ok=True)
    
    print(f"\\n=== LINEUM MODE=train PIPELINE START ===")
    print(f"Identifier: {identifier}")
    print(f"Source: {zip_path}\\n")

    # 1. State Initialization
    cfg = CoreConfig(
        use_mode_coupling=True, 
        use_mu=True,
        stencil_type="LAP4"  # Default deterministic kernel
    )
    
    encoder = TextToWaveEncoder(grid_size=GRID_SIZE, plasticity_tau=200)
    
    # Virgin state
    state = {
        "psi": np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.complex128),
        "phi": np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.float64),
        "kappa": np.ones((GRID_SIZE, GRID_SIZE), dtype=np.float64),
        "mu": np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.float64),
    }

    audit_log = []
    context_chunks = []
    
    # 2. Extract and Parse
    with zipfile.ZipFile(zip_path, 'r') as zf:
        for filename in zf.namelist():
            if not filename.endswith(('.txt', '.md')):
                continue
                
            print(f"-> Parsing {filename}...")
            content = zf.read(filename).decode('utf-8')
            chunks = _chunk_text(content)
            
            for i, chunk in enumerate(chunks):
                cat = _categorize_chunk(chunk)
                
                # Audit entry
                entry = {
                    "source": filename,
                    "chunk_id": i,
                    "length": len(chunk),
                    "category": cat
                }
                
                # 3. Routing
                if cat == "A":
                    # --- Core Physics Injection ---
                    # Use the new Hybrid Text-to-Wave Encoder
                    state, metrics = encoder.encode(
                        text=chunk,
                        state=state,
                        cfg=cfg,
                        step_fn=step_core,
                        mode="identity_burn",
                        personalization_depth=1.0
                    )
                    
                    # Log physical cost
                    entry["hdd_cost_kj"] = metrics.get("hdd_cost_kj", 0.0)
                    entry["rtb_stability"] = metrics.get("rtb_stability_score", 0.0)
                    entry["drift_index"] = metrics.get("identity_drift_index", 0.0)
                    print(f"   [Category A] Baked into Mu grid. (Cost: {entry['hdd_cost_kj']:.2f}, RTB: {entry['rtb_stability']:.4f})")
                
                else:
                    # --- Context Overhead ---
                    context_chunks.append({
                        "id": f"{filename}_{i}",
                        "content": chunk,
                        "metadata": {"type": "temporal_fact"}
                    })
                    print(f"   [Category B] Appended to Context Library.")
                    
                audit_log.append(entry)

    # 4. Finalization (Cooling Phase)
    print("\\n-> Cooling Phase (Running 200 ticks without input to rest topology)...")
    state["delta"] = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.float64)
    for _ in range(200):
        state = step_core(state, cfg)

    # 5. Export
    npz_path = os.path.join(out_dir, f"identity_seed_{identifier}.npz")
    np.savez_compressed(
        npz_path, 
        kappa=state["kappa"], 
        mu=state["mu"],
        phi=state["phi"],
        psi_real=state["psi"].real,
        psi_imag=state["psi"].imag,
        stencil_type=cfg.stencil_type
    )
    
    json_path = os.path.join(out_dir, "context.json")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(context_chunks, f, indent=2, ensure_ascii=False)
        
    audit_path = os.path.join(out_dir, "audit_trace.log")
    with open(audit_path, 'w', encoding='utf-8') as  f:
        json.dump(audit_log, f, indent=2)

    print(f"\\n=== MEMORY ENGRAVING COMLETE ===")
    print(f"Generated {npz_path}")
    print(f"Generated {json_path}")
    print(f"Target Mu Mass Engraved: {np.sum(state['mu']):.2f}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="LINEUM MODE=train Memory Engraving Pipeline")
    parser.add_argument("zip_path", type=str, help="Path to the user's .zip chat export.")
    parser.add_argument("--id", type=str, default=None, help="Optional identity label.")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.zip_path):
        print(f"FATAL: Could not find '{args.zip_path}'.")
        sys.exit(1)
        
    build_identity_pipeline(args.zip_path, args.id)
