import numpy as np
from PIL import Image
import os

def create_cad_file():
    GRID_SIZE = 64
    # Create black canvas (open fluid)
    img_array = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.uint8)
    
    # Draw White Walls (Masked regions)
    # 1. Outer Box
    img_array[0:2, :] = 255
    img_array[-2:, :] = 255
    img_array[:, 0:2] = 255
    img_array[:, -2:] = 255
    
    # 2. Add an internal acoustic lens (v-shape baffle)
    for i in range(15, 30):
        img_array[i, i + 5] = 255
        img_array[i, 64 - i - 5] = 255
        img_array[i+1, i + 5] = 255
        img_array[i+1, 64 - i - 5] = 255
        
    # 3. Add a central pillar
    img_array[40:45, 30:35] = 255
    
    # Filter to make walls strictly white (255) and open fluid black (0)
    img = Image.fromarray(img_array, mode='L')
    
    output_path = "scripts/reservoir_cad.png"
    img.save(output_path)
    print(f"Generated LPL CAD file at: {output_path}")

if __name__ == "__main__":
    create_cad_file()
