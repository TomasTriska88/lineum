import numpy as np
import matplotlib.pyplot as plt
import os
import sys

# Add repo root to path so we can import lineum_core
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from lineum_core.math import evolve

# --- PHASE 1: POLARIZED STRUCTURAL MEMORY ---
# Objective: Prove that the Lineum grid can be "trained" to route two distinct signals
# (Input A -> Output X, Input B -> Output Y) and conceptually retain this routing via physical Topographical Memory (carved channels).

def run_phase_1():
    print("--- Phase 1: Polarized Structural Memory ---")
    grid_size = 100
    
    psi = np.zeros((grid_size, grid_size), dtype=np.float32)
    phi = np.zeros((grid_size, grid_size), dtype=np.float32)
    kappa = np.full((grid_size, grid_size), 0.5, dtype=np.float32)
    delta = np.zeros((grid_size, grid_size), dtype=np.float32)
    
    # Define IO blocks (Coordinates in X, Y format)
    # Moving them closer (40 units apart) to prevent total signal attenuation
    input_A = (30, 30)  # Top Left
    input_B = (70, 30)  # Bottom Left
    output_X = (30, 70) # Top Right
    output_Y = (70, 70) # Bottom Right
    
    def inject_signal(p, coord, amplitude=15.0):
        noise = np.random.uniform(-amplitude, amplitude, size=(5, 5))
        p[coord[0]-2:coord[0]+3, coord[1]-2:coord[1]+3] += noise
        
    def measure_output(p, coord):
        return np.sum(np.abs(p[coord[0]-5:coord[0]+6, coord[1]-5:coord[1]+6]))

    # --- 1. TRAINING PHASE ---
    # According to the hypothesis, the universe learns by cooling (lowering entropy).
    # We simulate this by continuously lowering Kappa (increasing conductivity) wherever wave tension passes through.
    # To force the learning, we artificially place a deep Phi trap (the "reward/sink") at the desired output.
    
    print("\n1. Training Route: Input A -> Output X")
    for step in range(300):
        inject_signal(psi, input_A)
        # The Chiller (Artificial Sink): Force a deep phi trap at Output X to draw the signal
        phi[output_X[0]-5:output_X[0]+6, output_X[1]-5:output_X[1]+6] = -20.0
        
        psi, phi = evolve(psi, phi, kappa, delta)
        
        # Plasticity Module: Carve the kappa landscape based on energy flow (Hebbian thermodynamic cooling)
        energy = np.abs(psi)
        kappa = np.clip(kappa + energy * 0.05, 0.5, 10.0) # Higher kappa = higher conductivity (channel forms)
        
    print("   Training Route: Input B -> Output Y")
    # Reset Psi to clear residual noise, but KEEP kappa (the memory)
    psi.fill(0)
    # Reset phi to clear the previous artificial chiller
    phi.fill(0)
    
    for step in range(300):
        inject_signal(psi, input_B)
        # The Chiller (Artificial Sink): Force a deep phi trap at Output Y
        phi[output_Y[0]-5:output_Y[0]+6, output_Y[1]-5:output_Y[1]+6] = -20.0
        
        psi, phi = evolve(psi, phi, kappa, delta)
        
        # Plasticity Module
        energy = np.abs(psi)
        kappa = np.clip(kappa + energy * 0.05, 0.5, 10.0)
        
    trained_kappa = kappa.copy()

    # --- 2. TESTING PHASE ---
    print("\n2. Testing Memory (Chillers Disabled)")
    
    # We remove all artificial training chillers (-10.0).
    # However, to measure flow, we leave a mild, generic baseline "cognitive drain" (-2.0)
    # at BOTH outputs equally. The carved Kappa channels must decide where the water flows.
    phi.fill(0) 
    phi[output_X[0]-5:output_X[0]+6, output_X[1]-5:output_X[1]+6] = -2.0
    phi[output_Y[0]-5:output_Y[0]+6, output_Y[1]-5:output_Y[1]+6] = -2.0
    
    # Test A
    print("   Testing Input A...")
    psi.fill(0)
    for step in range(300):
        inject_signal(psi, input_A)
        psi, phi = evolve(psi, phi, trained_kappa, delta)
        
    out_X_for_A = measure_output(psi, output_X)
    out_Y_for_A = measure_output(psi, output_Y)
    print(f"   Response to A -> Output X: {out_X_for_A:.2f} | Output Y: {out_Y_for_A:.2f}")
    result_A = psi.copy()

    # Test B
    print("   Testing Input B...")
    psi.fill(0)
    phi.fill(0)
    for step in range(300):
        inject_signal(psi, input_B)
        psi, phi = evolve(psi, phi, trained_kappa, delta)
        
    out_X_for_B = measure_output(psi, output_X)
    out_Y_for_B = measure_output(psi, output_Y)
    print(f"   Response to B -> Output X: {out_X_for_B:.2f} | Output Y: {out_Y_for_B:.2f}")
    result_B = psi.copy()

    # --- 3. VISUALIZATION ---
    print("\n3. Rendering Phase 1 Results...")
    plt.figure(figsize=(15, 5))
    
    plt.subplot(1, 3, 1)
    plt.title("Carved Kappa Landscape\n(The Structural Memory)")
    # We display trained_kappa
    plt.imshow(trained_kappa.T, cmap='viridis', origin='lower')
    plt.colorbar(label='Carved Conductivity (k)')
    
    plt.subplot(1, 3, 2)
    plt.title(f"Test A Result (No Chillers)\nX:{out_X_for_A:.0f} | Y:{out_Y_for_A:.0f}")
    plt.imshow(np.abs(result_A).T, cmap='magma', origin='lower', vmax=50.0)
    # Mark IO regions
    plt.scatter([input_A[0], output_X[0]], [input_A[1], output_X[1]], color='white', marker='x')
    plt.colorbar(label='Psi Amplitude')
    
    plt.subplot(1, 3, 3)
    plt.title(f"Test B Result (No Chillers)\nX:{out_X_for_B:.0f} | Y:{out_Y_for_B:.0f}")
    plt.imshow(np.abs(result_B).T, cmap='magma', origin='lower', vmax=50.0)
    plt.scatter([input_B[0], output_Y[0]], [input_B[1], output_Y[1]], color='white', marker='x')
    plt.colorbar(label='Psi Amplitude')
    
    plt.tight_layout()
    output_png = os.path.join(os.path.dirname(__file__), "poc_phase_1_result.png")
    plt.savefig(output_png)
    print(f"Saved visualization to {output_png}")
    print("--- Phase 1 Complete ---")

if __name__ == "__main__":
    run_phase_1()
