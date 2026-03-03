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
    inputs = ["a", "apple", "This longer sentence should demonstrate how massive text begins filling the vector capacity."]
    
    with open("clean_audit.txt", "w", encoding="utf-8") as f:
        f.write("=== TranslatorSpec v0.2 Calibration Report ===\n\n")
        f.write("=== AUDIT 1: Delta Mask Distribution ===\n")
        for text in inputs:
            embed = mock_embedding(text)
            
            # Raw projection
            vec = embed.reshape(-1, 1, 1)
            raw_mask = np.sum(vec * translator.anchors_base, axis=0)
            
            delta = translator.text_embedding_to_delta(embed)
            
            f.write(f"[{text[:15]}...] Delta Mask -> Min: {delta.min():.4f}, Max: {delta.max():.4f}, Mean: {delta.mean():.4f}\n")
            
        f.write("\n=== AUDIT 2: R Vector Readout Distribution (Pre-Norm vs Norm) ===\n")
        
        for text in inputs:
            # Emulate a Long Running State (10k pressure, 1k tension)
            psi = np.random.randn(100, 100).astype(np.float32) * 500.0 + 1000.0
            phi = np.full((100, 100), 10000.0, dtype=np.float32)
            kappa = np.full((100, 100), 0.5, dtype=np.float32)
            
            embed = mock_embedding(text)
            delta_mask = translator.text_embedding_to_delta(embed)
            
            core_math.DT = 0.1
            for _ in range(50):
                psi, phi = evolve(psi, delta_mask, phi, kappa)
                
            delta_mask.fill(0.0)
            for _ in range(900):
                psi, phi = evolve(psi, delta_mask, phi, kappa)
                
            step = 100 // 10
            probe_indices = np.arange(step // 2, 100, step)
            
            psi_mag = np.abs(psi)
            phi_abs = np.abs(phi)
            
            norm_readout = []
            
            for y in probe_indices:
                for x in probe_indices:
                    raw_p = psi_mag[y, x]
                    raw_f = phi_abs[y, x]
                    
                    p_norm = np.clip(raw_p / 3000.0, 0.0, 1.0)
                    f_norm = np.clip(raw_f / 12000.0, 0.0, 1.0)
                    norm_readout.extend([p_norm, f_norm])
                    
            norm_readout = np.array(norm_readout)
            
            f.write(f"[{text[:15]}...] R Vector: Min: {norm_readout.min():.4f}, Max: {norm_readout.max():.4f}, Mean: {norm_readout.mean():.4f} -> SUM: {norm_readout.sum():.2f}/200.00\n")
        
if __name__ == "__main__":
    audit()
