import os
import sys
import time
import numpy as np

# Adjust path to find lineum_core
sys.path.insert(0, os.path.abspath('.'))
from lineum_core.math import evolve

def run_zeta_trng_benchmark():
    print("=== Zeta TRNG (Quantum Chaos) Benchmark ===")
    
    # 1. Setup concentrated/aggressive initialization
    size = 128
    steps = 500
    
    # Aggressive parameters to induce rapid collision/breakdown
    alpha = 7.0e-4
    beta = 1.5e-2
    delta = 4.62e-3
    dt = 0.01
    
    # "Island" kappa map to force interactions in the center
    kappa = np.zeros((size, size), dtype=np.float64)
    cy, cx = size // 2, size // 2
    r_island = size // 4
    y, x = np.ogrid[-cy:size-cy, -cx:size-cx]
    mask = x**2 + y**2 <= r_island**2
    kappa[mask] = 1.0
    # Soften edges slightly
    import scipy.ndimage
    kappa = scipy.ndimage.gaussian_filter(kappa, sigma=2.0)
    
    # Initialize fields
    np.random.seed(42)
    # Give it a strong, noisy localized initial state to force early "fracture"
    psi = (np.random.randn(size, size) + 1j * np.random.randn(size, size)) * 0.1
    psi *= mask
    phi = np.zeros((size, size), dtype=np.float64)
    stimulus = np.zeros((size, size), dtype=np.complex128)
    
    noise_amp = 5.0e-3
    
    # Tracking for RNBs (Return Nodes / Zeta points proxy)
    zeta_candidates = []
    
    # Simple peak tracking across frames to detect "decays" and "revisits"
    import scipy.ndimage.filters as filters
    def get_peaks(amp_field, threshold=0.01):
        data_max = filters.maximum_filter(amp_field, 3)
        maxima_mask = (amp_field == data_max) & (amp_field > threshold)
        y, x = np.where(maxima_mask)
        return list(zip(x, y))

    print(f"Initializing simulation grid: {size}x{size}")
    print(f"Target steps (simulated time): {steps}")
    print("Executing 'collision' generation...")
    
    start_time = time.time()
    
    previous_peaks = set()
    historical_decay_sites = set()
    
    # 2. Hot Loop
    for step in range(steps):
        # Prepare the random stimulus (the equivalent of what `lineum.py` puts in the `delta` argument)
        noise = (np.random.randn(size, size) + 1j * np.random.randn(size, size)) * noise_amp
        # We pass the noise array into the 'delta' parameter
        psi, phi = evolve(psi, noise, phi, kappa)
        
        # Every N steps, look for structural collapse (decay) or revisit (echo/zeta point)
        if step % 5 == 0:
            amp_field = np.abs(psi)
            current_peaks = set(get_peaks(amp_field))
            
            # Decays: peaks that existed last time but are gone now
            decays = previous_peaks - current_peaks
            for d in decays:
                historical_decay_sites.add(d)
                
            # Revisits (Zeta points): new peaks that appear on historical decay sites
            news = current_peaks - previous_peaks
            for n in news:
                # Look for exact or epsilon-near (radius 1 or 2) hits
                for h in historical_decay_sites:
                    dx, dy = n[0]-h[0], n[1]-h[1]
                    dist_sq = dx*dx + dy*dy
                    if 0 < dist_sq <= 4:  # Echo!
                        zeta_candidates.append({
                            'step': step,
                            'x': n[0], 'y': n[1],
                            'val': float(phi[n[1], n[0]])  # Extract entropy from the underlying memory field
                        })
                        break
            
            previous_peaks = current_peaks

    end_time = time.time()
    duration = end_time - start_time
    
    print("\n--- Benchmark Results ---")
    print(f"Total time: {duration:.4f} seconds")
    print(f"Total steps: {steps}")
    print(f"Steps per second: {steps / duration:.2f}")
    
    # 3. Assess throughput
    num_zeta = len(zeta_candidates)
    print(f"\nZeta-entropy points generated: {num_zeta}")
    if duration > 0:
        print(f"Zeta generation throughput: {num_zeta / duration:.2f} points / second")
        
    print("\nSample of generated entropy values (first 5):")
    for z in zeta_candidates[:5]:
        # Hash the value with coordinates to simulate the TRNG extraction step
        raw_val = f"{z['val']:.15f}_{z['x']}_{z['y']}_{z['step']}"
        import hashlib
        entropy_hex = hashlib.sha256(raw_val.encode('utf-8')).hexdigest()[:16]
        print(f"  Step {z['step']:03d} at ({z['x']:03d},{z['y']:03d}) -> Raw phi: {z['val']:.6f} -> TRNG Block: {entropy_hex}")

if __name__ == "__main__":
    run_zeta_trng_benchmark()
