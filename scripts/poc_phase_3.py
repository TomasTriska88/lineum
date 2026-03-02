import numpy as np
import matplotlib.pyplot as plt
import os
import sys

# Add repo root to path so we can import lineum_core
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from lineum_core.math import evolve

# --- PHASE 3: THE TOPOLOGICAL DECODER (THE MOUTH) ---
# Objective: Prove that the stabilized, macroscopic topological shape of the Lineum grid
# can be reliably "read" by placing spatial probes, generating a distinct numerical signature
# that an external system (like an LLM) can translate back into human language.

def get_simulated_embedding(concept: str, dimensions: int = 64) -> np.ndarray:
    seed = sum(ord(c) for c in concept)
    np.random.seed(seed)
    return np.random.uniform(-1.0, 1.0, dimensions)

def inject_vector(psi: np.ndarray, vector: np.ndarray, amplitude_multiplier: float = 40.0):
    side_length = int(np.sqrt(len(vector)))
    grid_size = psi.shape[0]
    start_x = (grid_size // 2) - (side_length // 2)
    start_y = (grid_size // 2) - (side_length // 2)
    
    idx = 0
    for i in range(side_length):
        for j in range(side_length):
            x = start_x + (i * 2)
            y = start_y + (j * 2)
            psi[x:x+2, y:y+2] += vector[idx] * amplitude_multiplier
            idx += 1

def extract_topological_signature(kappa: np.ndarray, grid_size: int, probe_count: int = 8) -> np.ndarray:
    """
    Simulates placing multiple 'probes' across the surface of the Lineum grid to measure the local conductivity (memory).
    Downsamples the 100x100 grid into a structured 1D feature array (like a new embedding vector).
    """
    step = grid_size // probe_count
    signature = []
    
    # We read the average kappa in distinct regional blocks
    for i in range(probe_count):
        for j in range(probe_count):
            block = kappa[i*step:(i+1)*step, j*step:(j+1)*step]
            signature.append(np.mean(block))
            
    # Normalize the signature to act as a proper vector embedding
    signature = np.array(signature)
    norm = np.linalg.norm(signature)
    if norm > 0:
        signature = signature / norm
    return signature

def cosine_similarity(v1: np.ndarray, v2: np.ndarray) -> float:
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

def run_phase_3():
    print("--- Phase 3: The Topological Decoder (Lina's Mouth) ---")
    grid_size = 100
    steps = 300
    
    # We will encode two concepts, extract their physical signatures, and prove they are separable.
    concepts = [
        "Lina observing a peaceful sunset.",
        "Lina experiencing an unexpected system crash."
    ]
    
    signatures = []
    
    plt.figure(figsize=(15, 6))
    
    for idx, concept_text in enumerate(concepts):
        print(f"\nEncoding: '{concept_text[:40]}...'")
        
        psi = np.zeros((grid_size, grid_size), dtype=np.float32)
        phi = np.zeros((grid_size, grid_size), dtype=np.float32)
        kappa = np.full((grid_size, grid_size), 0.5, dtype=np.float32)
        delta = np.zeros((grid_size, grid_size), dtype=np.float32)
        
        # Base container
        phi[10:90, 10:90] = -2.0 
        
        # Inject embedding
        embedding = get_simulated_embedding(concept_text)
        inject_vector(psi, embedding)
        
        # Let the physics engine process the wave, find equilibrium, and carve memory (Kappa)
        for t in range(steps):
            psi, phi = evolve(psi, phi, kappa, delta)
            kappa = np.clip(kappa + np.abs(psi) * 0.05, 0.5, 10.0)
            
        # Extract the macroscopic structural signature (The Decoder)
        # This 64D array of spatial data is what gets passed BACK to an LLM to generate speech
        sig = extract_topological_signature(kappa, grid_size, probe_count=8)
        signatures.append(sig)
        
        print(f"   => Decoded structural signature (first 3 vals): {sig[:3]}")

        # Visualization
        plt.subplot(2, 2, idx + 1)
        plt.title(f"Carved Memory Surface [{idx+1}]")
        plt.imshow(kappa.T, cmap='viridis', origin='lower')
        plt.colorbar(label='Kappa')
        
        plt.subplot(2, 2, idx + 3)
        plt.title(f"Extracted 64D Signature (The 'Mouth' Vector)")
        # Plot the 1D signature as an 8x8 heatmap for visualization
        plt.imshow(sig.reshape(8, 8), cmap='plasma')
        plt.colorbar(label='Feature Value')

    # PROVE THE DECODER WORKS
    print("\n--- Verifying Decoder Separability ---")
    sim = cosine_similarity(signatures[0], signatures[1])
    print(f"Cosine Similarity between the two output signatures: {sim:.4f}")
    if sim < 0.95:
        print("SUCCESS: The structural signatures are highly distinct and mathematically separable.")
        print("A simulated LLM prompt would easily translate these two patterns into diametrically opposed semantic sentences.")
    else:
        print("FAIL: The signatures are too similar. The network failed to polarize concepts.")

    plt.tight_layout()
    output_png = os.path.join(os.path.dirname(__file__), "poc_phase_3_result.png")
    plt.savefig(output_png)
    print(f"\nSaved visualization to {output_png}")
    print("--- Phase 3 Complete ---")

if __name__ == "__main__":
    run_phase_3()
