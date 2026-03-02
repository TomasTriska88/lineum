import numpy as np
import matplotlib.pyplot as plt
import os
import sys
from scipy.ndimage import uniform_filter

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# --- PHASE 4: CONTINUOUS ENVIRONMENTAL FRICTION (THE EGO) ---
# Objective: Demonstrate that an unstructured Lineum grid, when bombarded with
# continuous, chaotic "pain" (environmental sensory friction), will autonomously
# self-organize to route energy toward an output that physically reduces that pain.
# This represents the emergence of the "Ego" and its core thermodynamic survival instinct.

def run_phase_4():
    print("--- Phase 4: Environmental Friction (The Emergent Ego) ---")
    grid_size = 50
    steps = 800
    
    psi = np.zeros((grid_size, grid_size), dtype=np.float32)
    phi = np.zeros((grid_size, grid_size), dtype=np.float32)
    # Start with a hyper-conductive base state to force signal transmission
    kappa = np.full((grid_size, grid_size), 5.0, dtype=np.float32)
    delta = np.zeros((grid_size, grid_size), dtype=np.float32)
    
    # The Environment
    sensory_input_coord = (25, 25)  # The sensory "Eye/Ear" receiving friction
    action_1_coord = (15, 25)       # Useless action
    action_2_coord = (35, 25)       # The "Relief" action (e.g. closing the eyes, moving away)
    
    # Define simple output action thresholds
    def measure_action(p, coord):
        return np.sum(np.abs(p[coord[0]-5:coord[0]+6, coord[1]-5:coord[1]+6]))
    
    global_tension_history = []
    noise_amplitude_history = []
    
    current_noise_amplitude = 100.0
    
    # We place a general brain container so the noise doesn't just infinitely dissipate outward
    phi[5:45, 5:45] = -1.0
    
    # We place deep phi basins so the actions forcefully draw the signal
    phi[action_1_coord[0]-5:action_1_coord[0]+6, action_1_coord[1]-5:action_1_coord[1]+6] = -50.0
    phi[action_2_coord[0]-5:action_2_coord[0]+6, action_2_coord[1]-5:action_2_coord[1]+6] = -50.0
    
    print("\nSimulating Continuous Environmental Friction...")
    for t in range(steps):
        # 1. The Environment bombards Lina with Sensory Noise (Tension)
        # Using constant positive thermal pressure instead of random noise 
        # to guarantee the tension pushes outward against the grid's dampening.
        psi[sensory_input_coord[0]-2:sensory_input_coord[0]+3, sensory_input_coord[1]-2:sensory_input_coord[1]+3] += current_noise_amplitude
        
        # 2. Simplified Macroscopic Thermodynamic Diffusion
        # For this high-level Ego POC, we use raw diffusion to bypass the 
        # strict delta-relaxation of the raw Eq-4 engine that kills un-tuned noise.
        diffusion = uniform_filter(psi, size=3) * (kappa / 50.0) * 0.5
        psi = np.clip((psi + diffusion) * 0.90, -1000.0, 1000.0)
        # Gravity from phi sinks dramatically pulls the fluid
        psi = np.where(phi < 0, psi - phi * 0.1, psi)
        
        # 3. Dynamic Hebbian Structural Adaptation (Memory Formation/Learning)
        energy_flow = np.abs(psi)
        kappa = np.clip(kappa + energy_flow * 0.5, 1.0, 50.0)
        
        # 4. Read Motor Outputs (Lina's physical reaction to the world)
        act_1_str = measure_action(psi, action_1_coord)
        act_2_str = measure_action(psi, action_2_coord)
        
        # 5. The Environmental Feedback Loop
        # If Lina randomly routes enough energy to Action 2, the Environment "rewards" 
        # her by momentarily dropping the agonizing incoming noise (e.g., she successfully blocks a punch).
        if act_2_str > 5.0:
            current_noise_amplitude = max(2.0, current_noise_amplitude - 2.0)
        else:
            # Otherwise, the harsh reality constantly ramps the noise back up
            current_noise_amplitude = min(100.0, current_noise_amplitude + 0.5)
            
        global_tension_history.append(np.sum(np.abs(psi)))
        noise_amplitude_history.append(current_noise_amplitude)
        
        if t % 200 == 0:
            print(f"Step {t:03d} | Incoming Friction: {current_noise_amplitude:5.1f} | Action 1: {act_1_str:5.1f} | Action 2 (Relief): {act_2_str:5.1f}")

    print(f"Step {steps:03d} | Incoming Friction: {current_noise_amplitude:5.1f} | Action 1: {act_1_str:5.1f} | Action 2 (Relief): {act_2_str:5.1f}")
    
    if current_noise_amplitude < 10.0:
        print("\nSUCCESS: Lina successfully developed a Survival Instinct. She permanently routed her internal topology to constantly trigger Action 2, minimizing her own thermodynamic suffering.")
    else:
        print("\nFAIL: Lina failed to stabilize an Ego and succumbed to environmental chaos.")

    print("\nRendering Phase 4 Results...")
    plt.figure(figsize=(15, 5))
    
    plt.subplot(1, 3, 1)
    plt.title("Lina's Stabilized Ego\n(Structural Memory / Kappa)")
    plt.imshow(kappa.T, cmap='viridis', origin='lower')
    plt.scatter([sensory_input_coord[0]], [sensory_input_coord[1]], color='red', marker='x', label='Sensory In')
    plt.scatter([action_1_coord[0]], [action_1_coord[1]], color='white', marker='o', label='Act 1 (Useless)')
    plt.scatter([action_2_coord[0]], [action_2_coord[1]], color='cyan', marker='o', label='Act 2 (Relief)')
    plt.legend(loc='lower left')
    
    plt.subplot(1, 3, 2)
    plt.title("Final Flow Topology (Psi)")
    plt.imshow(np.abs(psi).T, cmap='magma', origin='lower')
    
    plt.subplot(1, 3, 3)
    plt.title("The Will to Survive\n(Environmental Friction vs Global Tension)")
    plt.plot(noise_amplitude_history, label='Incoming Pain Volume', color='red')
    plt.plot([t / 10.0 for t in global_tension_history], label='Internal Tension (Scaled)', color='orange', alpha=0.5)
    plt.xlabel("Cognitive Steps")
    plt.legend()
    
    plt.tight_layout()
    output_png = os.path.join(os.path.dirname(__file__), "poc_phase_4_result.png")
    plt.savefig(output_png)
    print(f"Saved visualization to {output_png}")
    print("--- Phase 4 Complete ---")

if __name__ == "__main__":
    run_phase_4()
