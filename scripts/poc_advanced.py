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

def run_routing_poc():
    size = 64
    steps = 1000
    
    out_dir = os.path.join(os.path.dirname(__file__), "..", "output_routing_poc")
    os.makedirs(out_dir, exist_ok=True)
    
    psi = np.zeros((size, size), dtype=np.complex128)
    delta = np.zeros((size, size), dtype=np.float64)
    phi = np.zeros((size, size), dtype=np.float64)
    kappa = np.ones((size, size), dtype=np.float64)
    
    # Translated comment (original removed due to English-only policy)
    kappa[10:50, 20:25] = 0.0
    kappa[45:50, 25:40] = 0.0
    kappa[10:35, 40:45] = 0.0
    
    # Translated comment (original removed due to English-only policy)
    kappa[15:35, 27:38] = 0.2
    
    np.random.seed(42)
    for _ in range(15):
        ry = np.random.randint(10, 54)
        rx = np.random.randint(15, 50)
        if rx < 15 or rx > 48: continue
        kappa[ry:ry+4, rx:rx+4] = 0.0
    
    # Translated comment (original removed due to English-only policy)
    start_y, start_x = 32, 10
    # Translated comment (original removed due to English-only policy)
    start2_y, start2_x = 55, 30
    
    target_y, target_x = 32, 54
    
    phi_frames = []
    
    print("Running Mathematical Route Refinement...")
    for step in tqdm(range(steps)):
        # Translated comment (original removed due to English-only policy)
        psi[start_y-1:start_y+2, start_x-1:start_x+2] = 10.0
        psi[start2_y-1:start2_y+2, start2_x-1:start2_x+2] = 10.0
        
        psi[target_y-2:target_y+3, target_x-2:target_x+3] *= 0.1
        
        psi, phi = evolve(psi, delta, phi, kappa)
        psi *= (kappa > 0.1)
        
        if step % 4 == 0:
            phi_frames.append(phi.copy())

    print("Generating Engineering Route Extractor...")
    fig, ax = plt.subplots(figsize=(8, 6))
    
    # Rastr mapy
    ax.imshow(kappa, cmap='gray_r', origin='upper', interpolation='nearest', vmin=0, vmax=1)
    
    # Translated comment (original removed due to English-only policy)
    phi_plot = ax.imshow(np.zeros((size, size)), cmap='plasma', origin='upper', alpha=0.5, interpolation='bilinear', vmin=0, vmax=25)
    
    ax.plot(start_x, start_y, 'go', markersize=12, zorder=12, label="Agent A")
    ax.plot(start2_x, start2_y, 'yo', markersize=12, zorder=12, label="Agent B")
    ax.plot(target_x, target_y, 'ro', markersize=12, zorder=12, label="Target")
    ax.legend(loc="upper left")
    
    def extract_path(phi_field, s_x, s_y):
        import heapq
        if np.max(phi_field) < 1e-3:
            return [], []
            
        cost_map = np.zeros((size, size))
        for y in range(size):
            for x in range(size):
                if kappa[y, x] <= 0.01:
                    cost_map[y, x] = np.inf
                else:
                    # Translated comment (original removed due to English-only policy)
                    # Translated comment (original removed due to English-only policy)
                    cost_map[y, x] = (1.0 / (phi_field[y, x] + 1e-6)) * (1.0 / kappa[y, x])
                    
        pq = [(0, target_x, target_y)]
        came_from = {}
        g_score = {(target_x, target_y): 0}
        
        while pq:
            current_cost, cx, cy = heapq.heappop(pq)
            
            if abs(cx - s_x) <= 2 and abs(cy - s_y) <= 2:
                curr = (cx, cy)
                raw_path = [curr]
                while curr in came_from:
                    curr = came_from[curr]
                    raw_path.append(curr)
                
                path_x = [s_x] + [p[0] for p in raw_path]
                path_y = [s_y] + [p[1] for p in raw_path]
                return path_x, path_y
                
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    if dx == 0 and dy == 0: continue
                    nx, ny = cx + dx, cy + dy
                    if 0 <= nx < size and 0 <= ny < size and kappa[ny, nx] > 0.0:
                        # Translated comment (original removed due to English-only policy)
                        if dx != 0 and dy != 0:
                            # Translated comment (original removed due to English-only policy)
                            # Translated comment (original removed due to English-only policy)
                            if kappa[cy, nx] == 0.0 and kappa[ny, cx] == 0.0:
                                continue
                        
                        move_cost = cost_map[ny, nx] * (1.414 if dx != 0 and dy != 0 else 1.0)
                        tentative_g_score = g_score[(cx, cy)] + move_cost
                        
                        if (nx, ny) not in g_score or tentative_g_score < g_score[(nx, ny)]:
                            came_from[(nx, ny)] = (cx, cy)
                            g_score[(nx, ny)] = tentative_g_score
                            f_score = tentative_g_score + np.hypot(s_x - nx, s_y - ny) * 0.1
                            heapq.heappush(pq, (f_score, nx, ny))
                            
        return [], []

    def update(frame_idx):
        f = phi_frames[frame_idx]
        
        # Translated comment (original removed due to English-only policy)
        max_f = np.max(f)
        if max_f > 0:
            phi_plot.set_data(f / max_f * 25) # Normalizace pro barvy
        
        px1, py1 = extract_path(f, start_x, start_y)
        px2, py2 = extract_path(f, start2_x, start2_y)
        
        # Clear previous path lines (keep start, start2, target dots)
        for line in ax.lines[3:]:
            line.remove()
            
        if len(px1) >= 2:
            ax.plot(px1, py1, 'c-', linewidth=4.0, zorder=10)
        if len(px2) >= 2:
            ax.plot(px2, py2, 'm-', linewidth=4.0, zorder=10) # Magenta pro B
        
        ax.set_title(f"Lineum Visualization: Two Sources, Swamp and Forgetting (Krok {frame_idx * 4})")

    ani = FuncAnimation(fig, update, frames=len(phi_frames), blit=False)
    import time
    gif_path = os.path.join(out_dir, f"routing_advanced.gif")
    ani.save(gif_path, writer='pillow', fps=20)
    print(f"Saved Advanced visualization to {gif_path}")

if __name__ == "__main__":
    run_routing_poc()
