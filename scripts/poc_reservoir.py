import numpy as np
import matplotlib.pyplot as plt
import os
import sys

# Add repo root to path so we can import lineum_core
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from lineum_core.math import evolve

# --- HYPOTHESIS: NATIVE RESERVOIR FLOW POC ---
# Objective: Demonstrate signal routing purely via thermodynamic tension,
# without artificial backpropagation or feedback loops.

def run_reservoir_poc():
    print("--- Running Native Reservoir POC ---")
    
    # 1. Initialize empty Lineum Grid (using raw numpy arrays like the engine does)
    print("1. Initializing Lineum core matrices...")
    grid_size = 100
    
    psi = np.zeros((grid_size, grid_size), dtype=np.float32)
    phi = np.zeros((grid_size, grid_size), dtype=np.float32)
    
    # By default, kappa is high (vacuum). We want a chaotic medium.
    # A value of 0.5 is a decent starting point for the baseline matrix.
    kappa = np.full((grid_size, grid_size), 0.5, dtype=np.float32)
    delta = np.zeros((grid_size, grid_size), dtype=np.float32)

    # 2. Sculpt the Topography (The Hardware)
    print("2. Sculpting Kappa/Phi landscape...")
    
    # --- The Source (A) ---
    source_x, source_y = 10, 50
    
    # --- The Sink (B) ---
    sink_x, sink_y = 90, 50
    # Sculpting a deep Phi-trap (gravity well) at the sink to absorb tension
    phi[sink_x-5:sink_x+5, sink_y-5:sink_y+5] = -10.0
    
    # Sculpting a high Kappa (conductive) corridor to encourage flow, 
    # but leaving it up to the Psi nodes to find it natively.
    kappa[20:80, 45:55] = 2.0  
    
    # 3. Inject continuous noise (thermal kinetic energy) at Source A
    print("3. Injecting continuous chaotic signal at Source A...")
    intensity = 5.0
    steps = 500
    
    # Track the tension over time
    tension_history = []
    
    for t in range(steps):
        # Inject kinetic energy (perturbation)
        psi[source_x, source_y] += np.random.uniform(-intensity, intensity)
        
        # Advance the Lineum equations using the C++ extension / core math
        psi, phi = evolve(psi, phi, kappa, delta)
        
        # Measure tension (how chaotic the grid is) using absolute values for complex compatibility
        current_tension = np.sum(np.abs(np.diff(psi))) 
        tension_history.append(float(current_tension))
        
        if t % 100 == 0:
            print(f"Step {t}, Global Tension: {current_tension:.2f}")
            
    # 4. Visualization
    print("4. Rendering results...")
    plt.figure(figsize=(12, 5))
    
    plt.subplot(1, 2, 1)
    plt.title("Final Psi State (Absolute Magnitude)")
    # Psi becomes complex during evolution, so we need to plot its magnitude
    plt.imshow(np.abs(psi).T, cmap='magma', origin='lower')
    plt.colorbar()
    
    plt.subplot(1, 2, 2)
    plt.title("Global Thermodynamic Tension")
    plt.plot(tension_history)
    plt.xlabel("Step")
    plt.ylabel("Tension (Abs Diff)")
    
    plt.tight_layout()
    output_png = os.path.join(os.path.dirname(__file__), "poc_reservoir_result.png")
    plt.savefig(output_png)
    print(f"Saved visualization to {output_png}")
    print("--- POC Complete ---")

if __name__ == "__main__":
    run_reservoir_poc()
