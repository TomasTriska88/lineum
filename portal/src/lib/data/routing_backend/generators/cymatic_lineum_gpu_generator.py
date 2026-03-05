import os
import sys
import numpy as np
import torch
from matplotlib import pyplot as plt
from matplotlib.animation import PillowWriter
from tqdm import tqdm

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from lineum_core.math import Eq4Config, _step_pytorch

def run_cymatic_gpu_injection(element_name="Carbon", frequency=4.0, radius=0.3, confinement_strength=0.9):
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"[*] Running Lineum Cymatic Injection for {element_name} on: {device}")
    
    # 1. Setup Grid
    N = 384  # Size of grid (384x384 is good for speed while retaining detail)
    STEPS = 20000
    
    # Initial State
    psi = torch.zeros((N, N), dtype=torch.complex128, device=device)
    phi = torch.zeros((N, N), dtype=torch.float64, device=device)
    kappa = torch.ones((N, N), dtype=torch.float64, device=device) * 0.95
    
    # Acoustic Confinement (The "Glass Bell")
    # Instead of letting the wave escape into infinite space, we build a reflective 
    # structural wall around the atom so the resonant waves bounce back and build the mandala.
    x = torch.linspace(-1, 1, N, device=device)
    y = torch.linspace(-1, 1, N, device=device)
    X, Y = torch.meshgrid(x, y, indexing='ij')
    R = torch.sqrt(X**2 + Y**2)
    
    # The confinement boundary is placed just outside the natural radius of the element
    boundary_radius = radius * 1.5
    kappa *= torch.clamp(1.0 - confinement_strength * (R/boundary_radius)**8, 0.0, 1.0)
    
    # 2. Cymatic Injection (Nucleus Vibration)
    theta = torch.atan2(Y, X)
    
    # Base frequency pattern (The metal plate geometry of Carbon)
    injection_shape = torch.sin(frequency * theta) * torch.exp(-(R/radius)**2)
    speaker_shape = injection_shape.cpu().numpy() * 5.0 # Acoustic force
    
    # 3. Eq-4 Config
    cfg = Eq4Config(dt=1.0)
    
    state = {
        "psi": psi.cpu().numpy(),
        "phi": phi.cpu().numpy(),
        "kappa": kappa.cpu().numpy(),
        "delta": np.zeros((N, N), dtype=np.float64) # Clean semantic state
    }
    
    print(f"[*] Simulating Eq-4 thermodynamic settling of the {element_name} Atom...")
    
    frames = []
    
    # Cymatic vibration frequency
    omega = 0.5 
    
    for i in tqdm(range(STEPS)):
        # Provide TRUE acoustic forcing (time-domain oscillation) like a cymatic speaker
        state["psi"] += speaker_shape * np.sin(i * omega)
        
        # GPU step
        state = _step_pytorch(state, cfg)
        
        # Capture frames
        if i % 100 == 0:
            # Visualize the actual wave structure (Amplitude of Psi) instead of accumulated heat (Phi)
            plot_frame = np.abs(state["psi"]).copy()
            frames.append(plot_frame)
            
    # Normalize for GIF
    print("[*] Rendering GIF...")
    frames_np = np.array(frames)
    vmin = np.percentile(frames_np, 5)
    vmax = np.percentile(frames_np, 99.5)
    
    fig, ax = plt.subplots(figsize=(6, 6), facecolor='black')
    fig.subplots_adjust(left=0, right=1, bottom=0, top=1)
    ax.axis('off')
    im = ax.imshow(frames_np[0], cmap='magma', vmin=vmin, vmax=vmax)
    
    def update(frame_idx):
        im.set_data(frames_np[frame_idx])
        return [im]
        
    import matplotlib.animation as animation
    ani = animation.FuncAnimation(fig, update, frames=len(frames), blit=True)
    
    out_path = os.path.join(os.path.dirname(__file__), f"cymatic_{element_name.lower()}_gpu.gif")
    ani.save(out_path, writer=PillowWriter(fps=30))
    plt.close(fig)
    print(f"[+] Successfully saved GPU Cymatic render to: {out_path}")

if __name__ == "__main__":
    # Test Carbon with Confinement
    run_cymatic_gpu_injection(element_name="Carbon", frequency=4.0, radius=0.3, confinement_strength=0.9)
