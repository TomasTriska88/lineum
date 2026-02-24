import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from scipy.ndimage import gaussian_filter
import warnings

warnings.filterwarnings('ignore')
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + '/..'))

import lineum_core.math as lmath
lmath.USE_PYTORCH = False  # Force CPU to preserve exact numpy seed determinism

def run_and_animate(seed):
    print(f"\n--- [ Generating Phi animation for Seed: {seed} ] ---")
    
    np.random.seed(seed)
    steps_total = 500
    size = 128
    
    # 1. Delta (Structured Noise)
    noise = np.random.normal(0.0, 1.0, (size, size))
    blurred = gaussian_filter(noise, sigma=10)
    delta = blurred / np.max(np.abs(blurred)) * 0.05
    
    # 2. Psi (Complex scalar field)
    amp = np.random.normal(0.0, 0.1, (size, size))
    phase = np.random.uniform(0, 2*np.pi, (size, size))
    amp[size//2, size//2] += 1.0  # Asymmetry at center
    psi = amp * np.exp(1j * phase)
    
    # 3. Phi (Interaction field)
    phi = np.zeros((size, size), dtype=np.float64)
    
    # 4. Kappa
    kappa = np.ones((size, size), dtype=np.float64) * 0.5

    phi_history = []
    
    print(f"Evolving {steps_total} steps...")
    for step in range(steps_total):
        psi, phi = lmath.evolve(psi, delta, phi, kappa)
        if step % 5 == 0:  # Save every 5 frames for the animation
            phi_history.append(phi.copy())
            
    print(f"Max phi at center: {phi[64, 64]:.2f}")
    
    # Setup rendering
    print("Rendering 3D animation...")
    fig = plt.figure(figsize=(10, 8))
    fig.patch.set_facecolor('#0f172a') # Dark slate background for premium look
    ax = fig.add_subplot(111, projection='3d')
    ax.set_facecolor('#0f172a')
    
    X, Y = np.meshgrid(np.arange(size), np.arange(size))
    
    max_phi = max([np.max(p) for p in phi_history])
    z_limit = max_phi * 1.2 if max_phi > 0 else 1.0

    # Prepare the initial frame
    surf = ax.plot_surface(X, Y, phi_history[0], cmap='magma', edgecolor='none', vmin=0, vmax=z_limit)
    ax.set_zlim(0, z_limit)
    ax.set_title(f"Extreme $\\varphi$ Spike - Seed {seed}", color='white', fontsize=16, pad=20)
    
    # Style the axes
    ax.xaxis.pane.fill = False
    ax.yaxis.pane.fill = False
    ax.zaxis.pane.fill = False
    [t.set_color('white') for t in ax.xaxis.get_ticklabels()]
    [t.set_color('white') for t in ax.yaxis.get_ticklabels()]
    [t.set_color('white') for t in ax.zaxis.get_ticklabels()]
    ax.xaxis.label.set_color('white')
    ax.yaxis.label.set_color('white')
    ax.zaxis.label.set_color('white')
    ax.grid(color='#334155', linestyle='--', linewidth=0.5)
    
    def update(frame):
        ax.clear()
        ax.set_zlim(0, z_limit)
        ax.set_facecolor('#0f172a')
        ax.set_title(f"Extreme $\\varphi$ Spike - Seed {seed} (Step {frame*5})", color='white', fontsize=16, pad=20)
        
        # Style the axes again (ax.clear clears styles)
        ax.xaxis.pane.fill = False
        ax.yaxis.pane.fill = False
        ax.zaxis.pane.fill = False
        [t.set_color('white') for t in ax.xaxis.get_ticklabels()]
        [t.set_color('white') for t in ax.yaxis.get_ticklabels()]
        [t.set_color('white') for t in ax.zaxis.get_ticklabels()]
        ax.grid(color='#334155', linestyle='-', linewidth=0.2)
        
        Z = phi_history[frame]
        surf = ax.plot_surface(X, Y, Z, cmap='magma', edgecolor='none', vmin=0, vmax=z_limit)
        return surf,
        
    anim = FuncAnimation(fig, update, frames=len(phi_history), interval=100, blit=False)
    
    os.makedirs('output', exist_ok=True)
    out_file = f"output/seed_{seed}_extreme_phi.gif"
    print(f"Saving to {out_file}...")
    anim.save(out_file, writer='pillow', fps=15)
    print("Done!")

if __name__ == "__main__":
    run_and_animate(9)
    run_and_animate(35)
