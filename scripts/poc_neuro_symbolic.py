import numpy as np
import matplotlib.pyplot as plt
import os
import sys

# Add repo root to path so we can import lineum_core
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from lineum_core.math import evolve

# --- HYPOTHESIS: NEURO-SYMBOLIC INTERFACE (THE MOUTH & EARS) ---
# Objective: Demonstrate encoding discrete text into continuous thermodynamic waves
# and decoding the resulting stabilized topological state back into discrete text.

def text_to_wave_injection(text: str, grid_size: int) -> np.ndarray:
    """The 'Ears': Encodes a simple string into a geometric pattern of kinetic Psi energy."""
    psi_injection = np.zeros((grid_size, grid_size), dtype=np.float32)
    
    # Very simple POC Hash: Convert chars to ASCII and map them to physical coordinates.
    # In a real system, this would be an LLM embedding vector projecting into the 2D grid.
    margin = 10
    total_length = len(text)
    if total_length == 0:
        return psi_injection
        
    spacing = (grid_size - 2 * margin) // total_length
    
    for i, char in enumerate(text):
        ascii_val = ord(char)
        # Map ascii (e.g. 65-122) to a Y coordinate (amplitude spatialization)
        # Normalize roughly between margin and grid_size-margin
        normalized_y = int(margin + (ascii_val - 60) / 65.0 * (grid_size - 2 * margin))
        # Clamp to grid bounds just in case
        normalized_y = max(margin, min(grid_size - margin, normalized_y))
        
        x_coord = margin + i * spacing
        
        # Inject a massive spike of energy (the "word" hitting the water)
        # We make it a small 3x3 splash
        psi_injection[x_coord-1:x_coord+2, normalized_y-1:normalized_y+2] = 50.0 
        
    return psi_injection


def wave_to_text_readout(psi: np.ndarray) -> str:
    """The 'Mouth': Decodes the stabilized topological landscape back into semantic meaning."""
    grid_size = psi.shape[0]
    
    # For this POC, we look at the right edge of the board (where waves wash up)
    # We divide the right edge into 'Top', 'Middle', 'Bottom' bands.
    right_edge = np.abs(psi[grid_size - 10:, :])
    
    top_band = np.sum(right_edge[:, grid_size//2 + 10:])
    bottom_band = np.sum(right_edge[:, :grid_size//2 - 10])
    
    # The physical topology (tension distribution) translates to a binary semantic answer
    if top_band > bottom_band:
        return "YES (Top-heavy tension)"
    elif bottom_band > top_band:
        return "NO (Bottom-heavy tension)"
    else:
        return "NEUTRAL (Balanced tension)"


def run_neuro_symbolic_poc():
    print("--- Running Neuro-Symbolic Interface POC ---")
    grid_size = 100
    
    # 1. Initialize empty Lineum Core
    print("1. Initializing Lineum core...")
    psi = np.zeros((grid_size, grid_size), dtype=np.float32)
    phi = np.zeros((grid_size, grid_size), dtype=np.float32)
    kappa = np.full((grid_size, grid_size), 0.5, dtype=np.float32)
    delta = np.zeros((grid_size, grid_size), dtype=np.float32)

    # Sculpt a basic "Brain" environment (a few phi traps to cause interference)
    phi[40:60, 40:60] = -5.0 # Central processing pit
    
    # 2. ENCODING (The Ears)
    input_word = "LINEUM"
    print(f"2. Translating semantic word '{input_word}' to wave kinetic injection...")
    injection = text_to_wave_injection(input_word, grid_size)
    psi += injection
    
    # Save a copy of the injection for visualization
    initial_psi = psi.copy()

    # 3. PROCESSING (The Brain)
    print("3. Allowing the reservoir to structurally process the concept (Eq-4 Evolve)...")
    steps = 300
    for t in range(steps):
        psi, phi = evolve(psi, phi, kappa, delta)
        
    # 4. DECODING (The Mouth)
    print("4. Reading stable topology and translating back to semantic text...")
    output_meaning = wave_to_text_readout(psi)
    print(f"\n>>> THE RESERVOIR ANSWERS: {output_meaning}\n")

    # 5. Visualization
    print("5. Rendering results...")
    plt.figure(figsize=(12, 5))
    
    plt.subplot(1, 2, 1)
    plt.title(f"Initial Semantic Injection: '{input_word}'")
    plt.imshow(np.abs(initial_psi).T, cmap='magma', origin='lower')
    plt.colorbar()
    
    plt.subplot(1, 2, 2)
    plt.title(f"Processed Stable Topology\nDecoded Output: {output_meaning}")
    plt.imshow(np.abs(psi).T, cmap='magma', origin='lower')
    plt.colorbar()
    
    plt.tight_layout()
    output_png = os.path.join(os.path.dirname(__file__), "poc_neuro_symbolic_result.png")
    plt.savefig(output_png)
    print(f"Saved visualization to {output_png}")
    print("--- POC Complete ---")

if __name__ == "__main__":
    run_neuro_symbolic_poc()
