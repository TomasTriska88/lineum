import numpy as np
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from routing_backend.translator import TranslatorV01
from routing_backend.entity_api import mock_embedding
from lineum_core.math import evolve
from lineum_core import math as core_math

def audit():
    translator = TranslatorV01()
    inputs = ["a", "2+2?", "apple"]
    
    print("=== AUDIT 1: Delta Mask Distribution ===")
    for text in inputs:
        embed = mock_embedding(text)
        
        # Raw projection without min/max scaling
        vec = embed / np.linalg.norm(embed)
        vec = vec.reshape(-1, 1, 1)
        raw_mask = np.sum(vec * translator.anchors_base, axis=0)
        
        # Current min/max normalized delta
        delta = translator.text_embedding_to_delta(embed)
        
        print(f"[{text}] Raw Mask -> Min: {raw_mask.min():.4f}, Max: {raw_mask.max():.4f}, Mean: {raw_mask.mean():.4f}")
        print(f"[{text}] Delta Mask -> Min: {delta.min():.4f}, Max: {delta.max():.4f}, Mean: {delta.mean():.4f}")
        
    print("\n=== AUDIT 2 & 3: R Vector before/after Normalization (for 'a') ===")
    
    # Run Eq-4' for 'a'
    psi = np.zeros((100, 100), dtype=np.float32)
    phi = np.full((100, 100), -1.0, dtype=np.float32)
    kappa = np.full((100, 100), 0.5, dtype=np.float32)
    
    embed = mock_embedding("a")
    delta_mask = translator.text_embedding_to_delta(embed)
    
    core_math.DT = 0.1
    for _ in range(50):
        psi, phi = evolve(psi, delta_mask, phi, kappa)
        
    delta_mask.fill(0.0)
    for _ in range(900):
        psi, phi = evolve(psi, delta_mask, phi, kappa)
        
    print(f"End of run max_psi: {np.abs(psi).max():.4f}, mean_phi: {phi.mean():.4f}")
    
    # Pre-normalization values
    step = 100 // 10
    probe_indices = np.arange(step // 2, 100, step)
    
    psi_mag = np.abs(psi)
    phi_abs = np.abs(phi)
    
    raw_readout = []
    norm_readout = []
    
    for y in probe_indices:
        for x in probe_indices:
            raw_p = psi_mag[y, x]
            raw_f = phi_abs[y, x]
            raw_readout.extend([raw_p, raw_f])
            
            p_norm = np.clip(raw_p / 100.0, 0.0, 1.0)
            f_norm = np.clip(raw_f / 10.0, 0.0, 1.0)
            norm_readout.extend([p_norm, f_norm])
            
    raw_readout = np.array(raw_readout)
    norm_readout = np.array(norm_readout)
    
    print(f"Raw R -> Min: {raw_readout.min():.4f}, Max: {raw_readout.max():.4f}, Mean: {raw_readout.mean():.4f}, Std: {raw_readout.std():.4f}")
    print(f"Normalized R -> Min: {norm_readout.min():.4f}, Max: {norm_readout.max():.4f}, Mean: {norm_readout.mean():.4f}")
    print(f"Norm R Vector Sum: {norm_readout.sum():.2f}")

if __name__ == "__main__":
    audit()
