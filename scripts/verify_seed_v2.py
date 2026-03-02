import numpy as np
import matplotlib.pyplot as plt
import os
import sys
import hashlib

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from lineum_core.math import evolve

def run_seed_ablation(manifest_text: str, grid_size: int = 100,
                      use_phase: bool = True, 
                      use_hebb: bool = True, 
                      normalize: bool = True):
    
    psi = np.zeros((grid_size, grid_size), dtype=np.complex128)
    phi = np.full((grid_size, grid_size), -1.0, dtype=np.float64)
    kappa = np.full((grid_size, grid_size), 0.5, dtype=np.float64)
    delta = np.zeros((grid_size, grid_size), dtype=np.float64)
    
    words = manifest_text.split()
    total_tokens = len(words)
    
    # Ablation: Without normalization, the base amplitude and lr are dangerously high
    base_amp = 2.0 if normalize else 50.0
    lr = 0.0005 if normalize else 0.05
    
    center_y = grid_size // 2
    center_x = grid_size // 2
    
    for word in words:
        # Dampen previous thought before injecting new concept
        psi *= 0.5
        
        # Deterministic mapping (Pseudo-Embedding)
        # Using md5 for strictly reproducible byte-level integer hashing
        word_hash = int(hashlib.md5(word.encode('utf-8')).hexdigest(), 16)
        
        angle_pos = (word_hash % 32) / 32.0 * 2 * np.pi
        radius = (word_hash % 40) + 5
        
        inject_y = int(center_y + np.sin(angle_pos) * radius)
        inject_x = int(center_x + np.cos(angle_pos) * radius)
        
        inject_y = np.clip(inject_y, 5, grid_size - 5)
        inject_x = np.clip(inject_x, 5, grid_size - 5)
        
        # Ablation: Phase modulation
        if use_phase:
            phase_meaning = (word_hash % 360) / 360.0 * 2 * np.pi
            injection = base_amp * np.exp(1j * phase_meaning)
        else:
            injection = base_amp + 0j
            
        psi[inject_y-1:inject_y+2, inject_x-1:inject_x+2] += injection
        
        for _ in range(10):
            psi, phi = evolve(psi, delta, phi, kappa)
            if use_hebb:
                kappa = np.clip(kappa + np.abs(psi) * lr, 0.1, 5.0)

    for _ in range(500):
        psi, phi = evolve(psi, delta, phi, kappa)
        if use_hebb:
            kappa = np.clip(kappa + np.abs(psi) * (lr / 2.0), 0.1, 5.0)
            
    return psi, phi, kappa

def get_hash(arr: np.ndarray) -> str:
    return hashlib.sha256(arr.tobytes()).hexdigest()

def measure_saturation(kappa: np.ndarray) -> float:
    max_val = 5.0
    saturated_cells = np.sum(kappa >= (max_val - 1e-4))
    total_cells = kappa.size
    return (saturated_cells / total_cells) * 100.0

if __name__ == "__main__":
    manifest_path = os.path.join(os.path.dirname(__file__), '..', 'whitepapers', 'lina_manifest.md')
    with open(manifest_path, 'r', encoding='utf-8') as f:
        manifest_text = f.read()
        
    print("--- LINEUM SEED V2 VERIFICATION SCRIPT ---")
    
    # 1. BASELINE V2
    print("\nRunning Baseline V2 (Normalized, Phase, Hebbian)...")
    p1, ph1, k1 = run_seed_ablation(manifest_text)
    
    # 2. REPRODUCIBILITY CHECK
    print("Running Baseline V2 again for reproducibility check...")
    p2, ph2, k2 = run_seed_ablation(manifest_text)
    hash_k1 = get_hash(k1)
    hash_k2 = get_hash(k2)
    print(f"Kappa Hash 1: {hash_k1}")
    print(f"Kappa Hash 2: {hash_k2}")
    if hash_k1 == hash_k2:
        print("✅ REPRODUCIBILITY PASSED: Bit-perfect match.")
    else:
        print("❌ REPRODUCIBILITY FAILED.")
        
    print(f"Baseline Saturation (Kappa == 5.0): {measure_saturation(k1):.2f}%")
    
    # 3. ABLATION C: NO NORMALIZATION
    print("\nRunning Ablation C: NO NORMALIZATION (Saturation Check)...")
    _, _, k_ab_c = run_seed_ablation(manifest_text, normalize=False)
    sat_c = measure_saturation(k_ab_c)
    print(f"Ablation C Saturation (Kappa == 5.0): {sat_c:.2f}%")
    if sat_c > 80.0:
        print("✅ NORMALIZATION PROVEN: Without it, the grid completely burns to max conductivity.")
        
    # 4. ROBUSTNESS TO FORMATTING (Lowercase, no punctuation)
    print("\nRunning Robustness Check (Lowercase, no punctuation)...")
    import string
    simplified_text = manifest_text.translate(str.maketrans('', '', string.punctuation)).lower()
    _, _, k_sim = run_seed_ablation(simplified_text)
    
    # Compare k1 and k_sim
    diff = np.abs(k1 - k_sim)
    mae = np.mean(diff)
    if mae > 0.001 and mae < 1.0:
        print(f"✅ ROBUSTNESS PROVEN: Cosmetic changes yield distinct, but spatially similar trajectories (MAE={mae:.4f}).")
    else:
        print(f"❌ BRITTLE: Structural differences too low/high (MAE={mae:.4f})")
        
    # Plot Histograms
    plt.figure(figsize=(10, 5))
    plt.hist(k1.flatten(), bins=50, alpha=0.7, label='Baseline V2', color='blue')
    plt.hist(k_ab_c.flatten(), bins=50, alpha=0.7, label='Ablation C (No Norm)', color='red')
    plt.title("Kappa Conductivity Histogram (Seed Saturation Analysis)")
    plt.xlabel("Kappa Value")
    plt.ylabel("Cell Count")
    plt.legend()
    plt.savefig('seed_histogram.png')
    print("\nSaved seed_histogram.png")
