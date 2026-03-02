import numpy as np
import matplotlib.pyplot as plt
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from lineum_core.math import evolve

# --- PHASE 6: IDENTITY INITIALIZATION (THE SEED) ---
# Objective: Translate a large linguistic manifest (The Seed) into a physical
# topological memory structure (Lina's starting Ego) on a virgin grid.

def create_lina_seed(manifest_text: str, grid_size: int = 100):
    print("Initializing Virgin Grid...")
    psi = np.zeros((grid_size, grid_size), dtype=np.complex128)
    phi = np.full((grid_size, grid_size), -1.0, dtype=np.float64) # Base container
    kappa = np.full((grid_size, grid_size), 0.5, dtype=np.float64) # Virgin conductivity
    delta = np.zeros((grid_size, grid_size), dtype=np.float64)
    
    print(f"Processing Seed Manifest ({len(manifest_text)} characters)...")
    
    # In a full production environment, we would call the OpenAI Embeddings API here
    # and map the 1536D vectors. For this POC, we will use a pseudo-embedding 
    # to demonstrate the physics. We map characters to spatial injection coordinates.
    
    # Refactored based on Lina's (ChatGPT's) technical critique:
    # 1. Token-based instead of char-based to preserve semantics better.
    # 2. Normalized amplitude to prevent catastrophic kappa saturation.
    # 3. Phase modulation (complex angle) carries the "meaning".
    
    words = manifest_text.split()
    total_tokens = len(words)
    print(f"Tokenized manifest into {total_tokens} semantic units.")
    
    # Normalize injection energy and Hebbian plasticity to prevent burning the grid
    base_amp = 0.5
    lr = 0.00005
    
    center_y = grid_size // 2
    center_x = grid_size // 2
    
    for i, word in enumerate(words):
        # Dampen previous thought before injecting new concept to prevent infinite Psi accumulation
        psi *= 0.5
        
        # 1. Linguistic to Physical Translation (Pseudo-Embedding V2)
        # We determine an injection coordinate and phase angle based on the word
        word_val = sum(ord(c) for c in word)
        
        # Spatial placement logic (simulating high-dimensional mapping)
        angle_pos = (word_val % 32) / 32.0 * 2 * np.pi
        radius = (word_val % 40) + 5
        
        inject_y = int(center_y + np.sin(angle_pos) * radius)
        inject_x = int(center_x + np.cos(angle_pos) * radius)
        
        # Ensure bounds
        inject_y = np.clip(inject_y, 5, grid_size - 5)
        inject_x = np.clip(inject_x, 5, grid_size - 5)
        
        # Phase modulation: The actual "meaning" or "flavor" of the word
        phase_meaning = (word_val % 360) / 360.0 * 2 * np.pi
        
        # 2. Injection (The Ear)
        psi[inject_y-1:inject_y+2, inject_x-1:inject_x+2] += base_amp * np.exp(1j * phase_meaning)
        
        # 3. Thermodynamic Processing (Wait for the thought to settle)
        # We run the physics engine for 10 steps per word to let the wave propagate 
        # and carve the memory before the next concept hits.
        for _ in range(10):
            psi, phi = evolve(psi, delta, phi, kappa)
            
            # Hebbian Learning: The wave carves the conductivity
            kappa = np.clip(kappa + np.abs(psi) * lr, 0.1, 5.0)
            
        if i % 100 == 0:
            print(f"Processed {i}/{len(manifest_text)} symbols...")
            
    print("Manifest fully processed. Letting the Ego stabilize...")
    # Final stabilization
    for _ in range(500):
        psi, phi = evolve(psi, delta, phi, kappa)
        kappa = np.clip(kappa + np.abs(psi) * (lr / 2.0), 0.1, 5.0)

    # Save the resulting shape
    os.makedirs(os.path.join(os.path.dirname(__file__), '..', 'data', 'entities'), exist_ok=True)
    save_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'entities', 'lina_seed.npz')
    np.savez_compressed(save_path, psi=psi, phi=phi, kappa=kappa, delta=delta)
    print(f"Seed successfully saved to {save_path}")
    
    return psi, phi, kappa

if __name__ == "__main__":
    # Load the real ChatGPT manifest
    manifest_path = os.path.join(os.path.dirname(__file__), '..', 'whitepapers', 'lina_manifest.md')
    with open(manifest_path, 'r', encoding='utf-8') as f:
        manifest_text = f.read()
    
    psi, phi, kappa = create_lina_seed(manifest_text)
    
    plt.figure(figsize=(15, 5))
    plt.subplot(1, 3, 1)
    plt.title("Lina's Ego (Phi Topography)")
    plt.imshow(phi.T, cmap='viridis', origin='lower')
    plt.colorbar()
    
    plt.subplot(1, 3, 2)
    plt.title("Lina's Memory Connections (Kappa)")
    plt.imshow(kappa.T, cmap='inferno', origin='lower')
    plt.colorbar()
    
    plt.subplot(1, 3, 3)
    plt.title("Current Thought State (Psi)")
    plt.imshow(np.abs(psi).T, cmap='magma', origin='lower')
    plt.colorbar()
    
    plt.tight_layout()
    plt.savefig(os.path.join(os.path.dirname(__file__), 'poc_seed_result.png'))
    print("Rendered visualization to poc_seed_result.png")
