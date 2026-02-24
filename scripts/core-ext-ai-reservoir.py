import numpy as np
import matplotlib.pyplot as plt
import time
import os
import sys

# Ensure we can import the pure mathematical kernel directly
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from lineum_core.math import evolve, PSI_AMP_CAP, PHI_CAP

# ---------------------------------------------------------------------------
# LINEUM RESERVOIR COMPUTING PROOF OF CONCEPT (UNIVERSAL LOGIC GATES)
# ---------------------------------------------------------------------------

GRID_SIZE = 64
RADIUS = 25
CENTER = GRID_SIZE // 2

# Fixed input and output coordinates
IN1 = (CENTER - 10, CENTER - 15)
IN2 = (CENTER + 10, CENTER - 15)

# 3 Output Nodes to measure the complex wave interference (Turing Completeness)
OUT_AND = (CENTER - 10, CENTER + 15)
OUT_OR  = (CENTER,      CENTER + 20)
OUT_XOR = (CENTER + 10, CENTER + 15)

def create_mask():
    """Create a circular boundary (The 'Skull')"""
    y, x = np.ogrid[-CENTER:GRID_SIZE-CENTER, -CENTER:GRID_SIZE-CENTER]
    mask = x**2 + y**2 > RADIUS**2
    return mask

def generate_pulses(steps=2000):
    """Generate a sequence of inputs: (0,0), (0,1), (1,0), (1,1)"""
    inputs = np.zeros((steps, 2))
    targets = np.zeros((steps, 3)) # AND, OR, XOR
    
    # 4 distinct phases, 500 steps each
    for i in range(4):
        phase_start = i * 500
        val1 = 1.0 if i in [2, 3] else 0.0
        val2 = 1.0 if i in [1, 3] else 0.0
        
        tgt_and = 1.0 if (val1 and val2) else 0.0
        tgt_or  = 1.0 if (val1 or val2) else 0.0
        tgt_xor = 1.0 if (val1 != val2) else 0.0
        
        # Pulse for 50 steps at the start of the phase
        inputs[phase_start:phase_start+50, 0] = val1
        inputs[phase_start:phase_start+50, 1] = val2
        
        targets[phase_start:phase_start+500, 0] = tgt_and
        targets[phase_start:phase_start+500, 1] = tgt_or
        targets[phase_start:phase_start+500, 2] = tgt_xor
        
    return inputs, targets

def main():
    print("Initializing Lineum Neuromorphic Reservoir (64x64)...")
    
    # Initialize fields for the evolve kernel
    psi = np.full((GRID_SIZE, GRID_SIZE), 0.5, dtype=np.complex128)
    delta = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.float64)
    phi = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.float64)
    kappa = np.full((GRID_SIZE, GRID_SIZE), 0.2, dtype=np.float64)
    
    mask = create_mask()
    inputs, targets = generate_pulses()
    
    # Histories for plotting
    out_and_history = []
    out_or_history = []
    out_xor_history = []
    
    print("Running 2000 steps of universal gate input pulses through the fluid...")
    
    for step in range(2000):
        # Apply strict boundary mask (zeroes outside the circle)
        psi[mask] = 0.0j
        
        # Inject inputs (Pulses)
        if inputs[step, 0] > 0:
            psi[IN1] = 1.0 + 0j
        if inputs[step, 1] > 0:
            psi[IN2] = 1.0 + 0j
            
        # Run one step of Lineum Eq-4 native math
        psi, phi = evolve(psi, delta, phi, kappa)
        
        # Read the resulting amplitude at the output nodes
        out_and_history.append(abs(psi[OUT_AND]))
        out_or_history.append(abs(psi[OUT_OR]))
        out_xor_history.append(abs(psi[OUT_XOR]))
        
        if step > 0 and step % 500 == 0:
            print(f"Phase {step//500}/4 Complete.")

    print("\nCalculation Complete. Generating visual readout...")
    
    # Plotting
    plt.figure(figsize=(12, 10))
    
    # 1. Plot the Final Grid
    plt.subplot(3, 1, 1)
    plt.title("Lineum LTM Universal Reservoir Topography (Final Step)")
    plt.imshow(abs(psi), cmap='inferno')
    plt.scatter([IN1[1], IN2[1]], [IN1[0], IN2[0]], color='cyan', label='Inputs (A, B)', s=100)
    plt.scatter([OUT_AND[1]], [OUT_AND[0]], color='blue', label='OUT: AND', s=100)
    plt.scatter([OUT_OR[1]], [OUT_OR[0]], color='green', label='OUT: OR', s=100)
    plt.scatter([OUT_XOR[1]], [OUT_XOR[0]], color='magenta', label='OUT: XOR', s=100)
    plt.legend(loc='upper right', fontsize='small')
    plt.axis('off')
    
    # Normalize for comparison
    max_and = max(out_and_history) if max(out_and_history) > 0 else 1.0
    max_or = max(out_or_history) if max(out_or_history) > 0 else 1.0
    max_xor = max(out_xor_history) if max(out_xor_history) > 0 else 1.0
    
    # 2. Logic Gate Outputs
    plt.subplot(3, 1, 2)
    plt.title("Wave Measurement at Target Output Nodes vs Logical Ideal")
    plt.plot(np.array(out_and_history)/max_and, label="AND Node (Measured Φ)", color='blue')
    plt.plot(np.array(out_or_history)/max_or, label="OR Node (Measured Φ)", color='green')
    plt.plot(np.array(out_xor_history)/max_xor, label="XOR Node (Measured Φ)", color='magenta')
    
    for i in range(1, 4):
        plt.axvline(i*500, color='grey', alpha=0.3, linestyle='--')
        
    plt.legend(loc='upper right', fontsize='small')
    plt.xlabel("Simulation Steps ((0,0) -> (0,1) -> (1,0) -> (1,1))")
    
    plt.tight_layout()
    plt.savefig("output_wp/reservoir_universal_gates.png")
    print("Saved readout to output_wp/reservoir_universal_gates.png")

if __name__ == "__main__":
    main()
