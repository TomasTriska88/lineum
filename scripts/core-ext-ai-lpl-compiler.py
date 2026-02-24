import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from lineum_core.math import evolve, PSI_AMP_CAP, PHI_CAP

# ---------------------------------------------------------------------------
# LINEUM POLYGON LANGUAGE (LPL) COMPILER
# ---------------------------------------------------------------------------
# This tool reads a black-and-white PNG "CAD" drawing, converts it into a rigid 
# 2D topological mask for the Lineum fluid, and runs the simulation to test the shape.
# ---------------------------------------------------------------------------

GRID_SIZE = 64
CAD_FILE = "scripts/reservoir_cad.png"

def load_cad_mask(filepath):
    """
    Loads a PNG image and converts it into a boolean mask.
    White pixels (intensity > 128) become the 'Skull' / Walls where Psi is killed.
    Black pixels become the open fluid reservoir.
    """
    if not os.path.exists(filepath):
        print(f"Error: {filepath} not found. Please draw an LPL CAD file first.")
        # Fallback to a basic circle if the image is missing
        y, x = np.ogrid[-32:32, -32:32]
        return x**2 + y**2 > 25**2
        
    img = Image.open(filepath).convert('L') # Convert to grayscale
    img = img.resize((GRID_SIZE, GRID_SIZE), Image.Resampling.NEAREST)
    
    img_array = np.array(img)
    # White walls = True (Masked/Killed), Black fluid = False (Open)
    mask = img_array > 128 
    return mask

def main():
    print("Initializing Lineum Polygon Language compiler...")
    
    mask = load_cad_mask(CAD_FILE)
    
    psi = np.full((GRID_SIZE, GRID_SIZE), 0.5, dtype=np.complex128)
    delta = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.float64)
    phi = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.float64)
    kappa = np.full((GRID_SIZE, GRID_SIZE), 0.2, dtype=np.float64)
    
    print("\nSimulating Fluid Dynamics over the LPL Geometry...")
    
    for step in range(100):
        # 1. Apply the rigid geometry (Kill waves hitting the skull)
        psi[mask] = 0.0j
        
        # 2. Inject continuous noise/data into the center (The 'Voice' of the instrument)
        if step % 5 == 0:
            psi[GRID_SIZE // 2, GRID_SIZE // 2] = 1.0 + 0j
            
        # Run physics
        psi, phi = evolve(psi, delta, phi, kappa)
        
    print("Simulation complete. Rendering Output...")
    
    plt.figure(figsize=(12, 5))
    
    plt.subplot(1, 2, 1)
    plt.title("LPL CAD Blueprint (The Hardware Mask)")
    # Render True as White walls, False as Black fluid
    plt.imshow(mask, cmap='gray')
    plt.axis('off')
    
    plt.subplot(1, 2, 2)
    plt.title("Computed Standing Waves (The Software Output)")
    plt.imshow(abs(psi), cmap='inferno')
    plt.axis('off')
    
    plt.tight_layout()
    output_path = "output_wp/lpl_compile_result.png"
    plt.savefig(output_path)
    print(f"Rendered to {output_path}")

if __name__ == "__main__":
    main()
