import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from tqdm import tqdm

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from lineum_core.math import evolve
from lineum_core import math as core_math

core_math.TEST_EXHALE_MODE = False
core_math.NOISE_STRENGTH = 0.0
core_math.PHI_INTERACTION_CAP = 100.0
core_math.PSI_AMP_CAP = 10.0
core_math.DRIFT_STRENGTH = 0.01
core_math.DISSIPATION_RATE = 0.05
core_math.PSI_DIFFUSION = 0.15
core_math.REACTION_STRENGTH = 0.1
core_math.PHI_DIFFUSION = 0.01

def run_fading_poc():
    size = 64
    steps = 1500
    
    out_dir = os.path.join(os.path.dirname(__file__), "..", "output_routing_poc")
    os.makedirs(out_dir, exist_ok=True)
    
    psi = np.zeros((size, size), dtype=np.complex128)
    delta = np.zeros((size, size), dtype=np.float64)
    phi = np.zeros((size, size), dtype=np.float64)
    kappa = np.ones((size, size), dtype=np.float64)
    
    # Translated comment (original removed due to English-only policy)
    kappa[10:50, 20:25] = 0.0
    kappa[45:50, 25:40] = 0.0
    kappa[10:20, 40:45] = 0.0 # Translated comment (original removed due to English-only policy)
    kappa[30:50, 40:45] = 0.0 # Translated comment (original removed due to English-only policy)
    # Mezera je mezi Y=20 a Y=30 (x=40:45)
    
    start_y, start_x = 32, 10
    target_y, target_x = 25, 54
    
    phi_frames = []
    kappa_frames = []
    
    print("Running Weather & Ghost Trails simulation...")
    for step in tqdm(range(steps)):
        
        # Translated comment (original removed due to English-only policy)
        if step == 700:
            kappa[20:30, 40:45] = 0.0
            
        psi[start_y-1:start_y+2, start_x-1:start_x+2] = 10.0
        psi[target_y-2:target_y+3, target_x-2:target_x+3] *= 0.1
        
        psi, phi = evolve(psi, delta, phi, kappa)
        psi *= (kappa > 0.1)
        
        if step % 5 == 0:
            phi_frames.append(phi.copy())
            kappa_frames.append(kappa.copy())

    print("Generating Visual Engine with Fading History...")
    fig, ax = plt.subplots(figsize=(8, 6))
    
    kappa_plot = ax.imshow(kappa_frames[0], cmap='gray_r', origin='upper', interpolation='nearest', vmin=0, vmax=1)
    
    ax.plot(start_x, start_y, 'go', markersize=12, zorder=20, label="Agent")
    ax.plot(target_x, target_y, 'ro', markersize=12, zorder=20, label="Target")
    ax.legend(loc="upper left")
    
    def extract_path(phi_field, k_field):
        import heapq
        if np.max(phi_field) < 1e-3:
            return [], []
            
        cost_map = np.zeros((size, size))
        for y in range(size):
            for x in range(size):
                if k_field[y, x] <= 0.01:
                    cost_map[y, x] = np.inf
                else:
                    cost_map[y, x] = (1.0 / (phi_field[y, x] + 1e-6)) * (1.0 / k_field[y, x])
                    
        pq = [(0, target_x, target_y)]
        came_from = {}
        g_score = {(target_x, target_y): 0}
        
        while pq:
            current_cost, cx, cy = heapq.heappop(pq)
            if abs(cx - start_x) <= 2 and abs(cy - start_y) <= 2:
                curr = (cx, cy)
                raw_path = [curr]
                while curr in came_from:
                    curr = came_from[curr]
                    raw_path.append(curr)
                return [start_x] + [p[0] for p in raw_path], [start_y] + [p[1] for p in raw_path]
                
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, 1), (-1, 1), (1, -1)]:
                nx, ny = cx + dx, cy + dy
                if 0 <= nx < size and 0 <= ny < size and k_field[ny, nx] > 0.0:
                    if dx != 0 and dy != 0:
                        if k_field[cy, nx] == 0.0 and k_field[ny, cx] == 0.0:
                            continue
                    
                    move_cost = cost_map[ny, nx] * (1.414 if dx != 0 and dy != 0 else 1.0)
                    tentative_g_score = g_score[(cx, cy)] + move_cost
                    if (nx, ny) not in g_score or tentative_g_score < g_score[(nx, ny)]:
                        came_from[(nx, ny)] = (cx, cy)
                        g_score[(nx, ny)] = tentative_g_score
                        f_score = tentative_g_score + np.hypot(start_x - nx, start_y - ny) * 0.1
                        heapq.heappush(pq, (f_score, nx, ny))
        return [], []

    # Translated comment (original removed due to English-only policy)
    history_lines = [] # Format: [(path_x, path_y, age), ...]
    MAX_AGE = 50 # Translated comment (original removed due to English-only policy)

    def update(frame_idx):
        f = phi_frames[frame_idx]
        k = kappa_frames[frame_idx]
        
        # Translated comment (original removed due to English-only policy)
        kappa_plot.set_data(k)
        
        px, py = extract_path(f, k)
        
        # Translated comment (original removed due to English-only policy)
        if len(px) >= 2:
            history_lines.append((px, py, 0))
            
        # Clear previous path lines
        for line in ax.lines[2:]:
            line.remove()
            
        # Translated comment (original removed due to English-only policy)
        alive_history = []
        for hx, hy, age in history_lines:
            alpha = max(0.0, 1.0 - (age / MAX_AGE))
            if alpha > 0.01:
                # Translated comment (original removed due to English-only policy)
                ax.plot(hx, hy, color=(0.5, 0.0, 0.5, alpha), linewidth=6.0, zorder=5 + (alpha*5))
                alive_history.append((hx, hy, age + 1)) # Translated comment (original removed due to English-only policy)
                
        history_lines[:] = alive_history
        
        # Translated comment (original removed due to English-only policy)
        if len(px) >= 2:
            ax.plot(px, py, 'c-', linewidth=4.0, zorder=12)
        
        ax.set_title(f"Dynamic Weather & Ghost Trails (Krok {frame_idx * 5})")

    ani = FuncAnimation(fig, update, frames=len(phi_frames), blit=False)
    gif_path = os.path.join(out_dir, "routing_fading_poc.gif")
    ani.save(gif_path, writer='pillow', fps=20)
    print(f"Saved Fading POC visualization to {gif_path}")

if __name__ == "__main__":
    run_fading_poc()
