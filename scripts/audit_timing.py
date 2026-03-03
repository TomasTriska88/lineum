import numpy as np
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from routing_backend.translator import TranslatorV01
from routing_backend.entity_api import mock_embedding
from lineum_core.math import evolve
from lineum_core import math as core_math

def measure_r(psi, phi, translator):
    # Same logic as in the translator (but we just want to extract the norm_readout to get stats)
    # We do a direct extraction here to avoid modifying translator currently, but actually calling translator is best
    readout = translator.read_grid_to_vector(psi, phi)
    return readout

def audit_timing():
    translator = TranslatorV01()
    inputs = ["a", "This longer sentence should demonstrate how massive text begins filling the vector capacity."]
    
    with open("timing_audit.txt", "w", encoding="utf-8") as f:
        f.write("=== AUDIT 3: R Vector Temporal Dissipation ===\n\n")
        
        for text in inputs:
            f.write(f"--- Input: '{text[:20]}...' ---\n")
            
            # Start from running state
            psi = np.random.randn(100, 100).astype(np.float32) * 500.0 + 1000.0
            phi = np.full((100, 100), 10000.0, dtype=np.float32)
            kappa = np.full((100, 100), 0.5, dtype=np.float32)
            
            embed = mock_embedding(text)
            delta_mask = translator.text_embedding_to_delta(embed)
            
            core_math.DT = 0.1
            total_ticks = 0
            
            # Helper to evolve and record
            def tick_and_record(ticks_to_evolve, record_at_tick, use_delta):
                nonlocal psi, phi, total_ticks
                d_mask = delta_mask if use_delta else np.zeros_like(delta_mask)
                
                for _ in range(ticks_to_evolve):
                    psi, phi = evolve(psi, d_mask, phi, kappa)
                    total_ticks += 1
                
                if total_ticks == record_at_tick:
                    r = measure_r(psi, phi, translator)
                    f.write(f"  [Tick {total_ticks:3d}] Max Psi: {np.max(np.abs(psi)):.1f}, R_Sum: {np.sum(r):.2f}, R_Max: {np.max(r):.4f}, R_Mean: {np.mean(r):.4f}\n")

            # Injection phase: 50 ticks (record at 5, 50)
            tick_and_record(5, 5, True)
            tick_and_record(45, 50, True)
            
            # Relaxation phase: 950 ticks (record at 200, 950)
            # 200 tick mark is 150 ticks into relaxation
            tick_and_record(150, 200, False)
            # 950 tick mark is 750 more ticks into relaxation
            tick_and_record(750, 950, False)
            
            f.write("\n")

if __name__ == "__main__":
    audit_timing()
