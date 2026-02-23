import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import argparse
import time

"""
Brane Multiverse Prototype (C-COSMO)
=====================================
This script simulates N independent Lineum Universes stacked as parallel 'Branes'.
They DO NOT interact physically (Psi-Psi collisions).
They DO NOT share short-term RAM memory (Phi-Phi).
However, they all share ONE SINGLE 'HDD' Foundation (Mu).
The Mu foundation historically tracks where matter from ANY universe has been,
carving a probability 'trench' that subtly pulls on the particles of all Branes.

Layers:
1. Psi (Matter): Local to each Brane.
2. Phi (RAM): Local to each Brane (short-term gravitational elasticity).
3. Mu (HDD): Global to the entire Multiverse stack (long-term Karma/Probability floor).
"""

def laplacian_2d(field):
    """Calculates the 2D Laplacian using central finite differences with periodic boundaries."""
    return (
        np.roll(field, 1, axis=0) +
        np.roll(field, -1, axis=0) +
        np.roll(field, 1, axis=1) +
        np.roll(field, -1, axis=1) -
        4.0 * field
    )

def simulate_brane_multiverse(N_branes=10, grid_size=128, steps=1000, karma_pull=0.01):
    print(f"Initializing a Brane Multiverse with {N_branes} stacked parallel universes...")
    
    # 1. Matter Layers (Psi): One for each Brane
    psi_stack = np.random.randn(N_branes, grid_size, grid_size).astype(np.float32) * 0.1
    
    # 2. Short-Term Memory Layers (Phi): One for each Brane
    phi_stack = np.zeros((N_branes, grid_size, grid_size), dtype=np.float32)
    
    # 3. Long-Term Memory Floor (Mu): Only ONE for the entire Multiverse
    mu_floor = np.zeros((grid_size, grid_size), dtype=np.float32)

    # Simulation Constants (Simplified Eq-4 parameters for POC)
    c2 = 1.0     # Wave speed squared
    alpha = 0.5  # Nonlinear coupling
    beta = 0.1   # Dissipation
    mu_memory_rate = 0.005 # How fast matter carves into the HDD

    # Velocity arrays for 2nd order PDE integration
    psi_v_stack = np.zeros_like(psi_stack)
    phi_v_stack = np.zeros_like(phi_stack)

    print("Beginning Multiverse Evolution...")
    start_time = time.time()

    # Track metrics for visualization
    history_mu = []

    for step in range(steps):
        # Calculate Laplacians for all Branes simultaneously using vectorization
        lap_psi = np.array([laplacian_2d(p) for p in psi_stack])
        lap_phi = np.array([laplacian_2d(p) for p in phi_stack])

        # Eq-4 Updates for all Branes
        # 1. Update RAM (Phi) based ONLY on local Brane matter
        phi_acc = c2 * lap_phi - alpha * np.abs(psi_stack)**2 - beta * phi_v_stack
        phi_v_stack += phi_acc * 0.1
        phi_stack += phi_v_stack * 0.1

        # 2. Update Matter (Psi) based on local Phi AND the GLOBAL Mu HDD
        # The 'karma_pull' represents the Dark Matter gravity bleeding up from the HDD floor
        psi_acc = c2 * lap_psi + alpha * phi_stack * psi_stack - beta * psi_v_stack
        
        # Apply the Multiverse Karma (HDD Pull)
        # All universes feel the topological gravity of the shared floor
        psi_acc += karma_pull * (mu_floor * psi_stack) 

        psi_v_stack += psi_acc * 0.1
        psi_stack += psi_v_stack * 0.1

        # 3. Update the Global HDD (Mu)
        # The HDD accumulates the density patterns of ALL Universes
        total_multiverse_mass = np.sum(np.abs(psi_stack)**2, axis=0)
        mu_floor += (total_multiverse_mass * mu_memory_rate)
        
        # Optional: Slow healing/decay of the HDD to prevent infinite divergence
        mu_floor *= 0.999 

        if step % 50 == 0:
            history_mu.append(mu_floor.copy())
            if step % 250 == 0:
                print(f"  Step {step}/{steps} - Multiverse Max HDD Depth: {np.max(mu_floor):.4f}")

    calc_time = time.time() - start_time
    print(f"Simulation Complete in {calc_time:.2f} seconds.")
    print(f"Generating Probability Map (Mu) Visualizations...")
    
    return history_mu

def render_hdd_evolution(history_mu, outfile="multiverse_hdd_evolution.gif"):
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.set_title("Evolution of the Multiverse Probability Floor (\u03bc)")
    ax.axis('off')
    
    img = ax.imshow(history_mu[0], cmap='magma', interpolation='nearest')
    
    def update(frame):
        img.set_data(history_mu[frame])
        img.set_clim(vmin=0, vmax=np.max(history_mu[frame]))
        ax.set_title(f"Multiverse Probability Floor (\u03bc) - Iter {frame * 50}")
        return [img]
        
    ani = FuncAnimation(fig, update, frames=len(history_mu), blit=True)
    ani.save(outfile, fps=15)
    plt.close()
    print(f"Saved Akashic Record visualization to {outfile}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simulate a Brane Multiverse sharing a \u03bc memory floor.")
    parser.add_argument("--branes", type=int, default=10, help="Number of parallel universes to stack")
    parser.add_argument("--steps", type=int, default=1500, help="Number of simulation steps")
    parser.add_argument("--karma", type=float, default=0.02, help="Strength of the HDD pull on the Branes")
    args = parser.parse_args()
    
    mu_history = simulate_brane_multiverse(N_branes=args.branes, steps=args.steps, karma_pull=args.karma)
    render_hdd_evolution(mu_history)
