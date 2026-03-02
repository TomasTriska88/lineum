import numpy as np
import matplotlib.pyplot as plt
import os
import sys

# Add repo root to path so we can import lineum_core
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from lineum_core.math import evolve

# --- PHASE 2: HIGH-DIMENSIONAL SIGNAL INJECTION (THE EAR) ---
# Objective: Prove that a complex, high-dimensional vector (simulating a concept embedding
# from an LLM, e.g., representing a piece of the user's ChatGPT history) can be translated 
# into a spatial Topography of Psi kinetics without destroying the structural equilibrium of the grid.

def get_simulated_embedding(concept: str, dimensions: int = 64) -> np.ndarray:
    """Simulates an LLM grabbing the semantic meaning of a word as a dense vector."""
    # We use a fixed random seed derived from the string to get a deterministic "embedding"
    seed = sum(ord(c) for c in concept)
    np.random.seed(seed)
    # LLM embeddings are typically normalized floats between -1 and 1
    return np.random.uniform(-1.0, 1.0, dimensions)

def vector_to_spatial_injection(vector: np.ndarray, grid_size: int) -> np.ndarray:
    """Translates the high-dimensional mathematical vector into a 2D spatial Lineum injection (The Ear)."""
    psi_injection = np.zeros((grid_size, grid_size), dtype=np.float32)
    
    # Let's map a 64D vector into an 8x8 spatial arrangement in the center of the grid.
    # We will scale the vector amplitude so it hits the water hard enough to cause ripples.
    amplitude_multiplier = 40.0 
    
    side_length = int(np.sqrt(len(vector))) # 8 for a 64D vector
    
    start_x = (grid_size // 2) - (side_length // 2)
    start_y = (grid_size // 2) - (side_length // 2)
    
    idx = 0
    for i in range(side_length):
        for j in range(side_length):
            # We inject the value as a small 2x2 "footprint" to ensure the wave propagates well
            x = start_x + (i * 2)
            y = start_y + (j * 2)
            psi_injection[x:x+2, y:y+2] = vector[idx] * amplitude_multiplier
            idx += 1
            
    return psi_injection

def run_phase_2():
    print("--- Phase 2: High-Dimensional Concept Injection (Lina's Ear) ---")
    grid_size = 100
    steps = 400
    
    # We will test two highly distinct "concepts" to see if they carve different macroscopic shapes
    concepts = [
        "Concept A: A deeply philosophical discussion about the nature of consciousness.",
        "Concept B: A fast-paced, chaotic debugging session for a Python backend."
    ]
    
    plt.figure(figsize=(15, 6))
    
    for idx, concept_text in enumerate(concepts):
        print(f"\nProcessing Concept [{idx+1}]: {concept_text[:40]}...")
        
        # 1. Initialize empty Lineum Core
        psi = np.zeros((grid_size, grid_size), dtype=np.float32)
        phi = np.zeros((grid_size, grid_size), dtype=np.float32)
        kappa = np.full((grid_size, grid_size), 0.5, dtype=np.float32)
        delta = np.zeros((grid_size, grid_size), dtype=np.float32)

        # Basic environmental constraints (Brain shape)
        phi[10:90, 10:90] = -2.0 # Mild general processing container
        
        # 2. Get LLM Vector and Translate to Physical Space
        embedding = get_simulated_embedding(concept_text, dimensions=64)
        spatial_injection = vector_to_spatial_injection(embedding, grid_size)
        
        # Apply the injection
        psi += spatial_injection
        initial_psi = psi.copy()

        # 3. Eq-4 Reservoir Processing
        # We allow the complex 64-point impact to ripple, interfere, and find equilibrium.
        energy_history = []
        for t in range(steps):
            psi, phi = evolve(psi, phi, kappa, delta)
            
            # Record global energy to prove it doesn't explode (Vacuum Decay)
            energy = np.sum(np.abs(psi))
            energy_history.append(float(energy))
            
            # Mild Hebbian structural adaptation (Memory Formation)
            kappa = np.clip(kappa + np.abs(psi) * 0.005, 0.5, 5.0)

        # 4. Visualization
        col_offset = idx * 2
        
        plt.subplot(2, 4, col_offset + 1)
        plt.title(f"Injection footprint [{idx+1}]")
        plt.imshow(np.abs(initial_psi).T, cmap='magma', origin='lower')
        
        plt.subplot(2, 4, col_offset + 2)
        plt.title(f"Stabilized Topology [{idx+1}]")
        plt.imshow(np.abs(psi).T, cmap='magma', origin='lower', vmax=10.0)
        
        plt.subplot(2, 4, col_offset + 5)
        plt.title(f"Carved Memory (Kappa) [{idx+1}]")
        plt.imshow(kappa.T, cmap='viridis', origin='lower')
        
        plt.subplot(2, 4, col_offset + 6)
        plt.title(f"Thermodynamic Energy [{idx+1}]")
        plt.plot(energy_history, color='orange')
        plt.xlabel("Steps")
        
    plt.tight_layout()
    output_png = os.path.join(os.path.dirname(__file__), "poc_phase_2_result.png")
    plt.savefig(output_png)
    print(f"\nSaved visualization to {output_png}")
    print("--- Phase 2 Complete ---")

if __name__ == "__main__":
    run_phase_2()
