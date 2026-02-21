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
    
    kappa[10:50, 20:25] = 0.0
    kappa[45:50, 25:40] = 0.0
    kappa[10:35, 40:45] = 0.0
    np.random.seed(42)
    for _ in range(15):
        ry = np.random.randint(10, 54)
        rx = np.random.randint(15, 50)
        if rx < 15 or rx > 48: continue
        kappa[ry:ry+4, rx:rx+4] = 0.0
    
    start_y, start_x = 32, 10
    target_y, target_x = 32, 54
    
    phi_frames = []
    
    print("Running Mathematical Route Refinement...")
    for step in tqdm(range(steps)):
        psi[start_y-1:start_y+2, start_x-1:start_x+2] = 10.0
        psi[target_y-2:target_y+3, target_x-2:target_x+3] *= 0.1
        
        psi, phi = evolve(psi, delta, phi, kappa)
        psi *= (kappa > 0.1)
        
        if step % 4 == 0:
            phi_frames.append(phi.copy())

    print("Generating Engineering Route Extractor...")
    fig, ax = plt.subplots(figsize=(8, 6))
    
    # Render the array natively to guarantee 1:1 coordinate alignment between math and visuals
    ax.imshow(kappa, cmap='gray_r', origin='upper', interpolation='nearest')
    
    ax.plot(start_x, start_y, 'go', markersize=12, zorder=12, label="Start")
    ax.plot(target_x, target_y, 'ro', markersize=12, zorder=12, label="Cíl")
    ax.legend(loc="upper left")
    
    # We will compute pseudo-Dijkstra or pure gradient tracking over phi + distance metric 
    # to guarantee it finds the optimal line formed by the physics
    def extract_path(phi_field):
        import heapq
        if np.max(phi_field) < 1e-3:
            return [], []
            
        cost_map = np.zeros((size, size))
        for y in range(size):
            for x in range(size):
                if kappa[y, x] == 0.0:
                    cost_map[y, x] = np.inf
                else:
                    cost_map[y, x] = 1.0 / (phi_field[y, x] + 1e-6)
                    
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
                
                path_x = [start_x] + [p[0] for p in raw_path]
                path_y = [start_y] + [p[1] for p in raw_path]
                return path_x, path_y
                
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = cx + dx, cy + dy
                if 0 <= nx < size and 0 <= ny < size and kappa[ny, nx] > 0:
                    move_cost = cost_map[ny, nx]
                    tentative_g_score = g_score[(cx, cy)] + move_cost
                    
                    if (nx, ny) not in g_score or tentative_g_score < g_score[(nx, ny)]:
                        came_from[(nx, ny)] = (cx, cy)
                        g_score[(nx, ny)] = tentative_g_score
                        f_score = tentative_g_score + np.hypot(start_x - nx, start_y - ny) * 0.1
                        heapq.heappush(pq, (f_score, nx, ny))
                            
        return [], []

    def update(frame_idx):
        f = phi_frames[frame_idx]
        px, py = extract_path(f)
        
        print(f"Frame {frame_idx}: Extracted path length {len(px)}")
        
        # Clear previous path lines (keep start and target dots)
        for line in ax.lines[2:]:
            line.remove()
            
        if len(px) >= 2:
            ax.plot(px, py, 'c-', linewidth=4.0, zorder=10)
        
        ax.set_title(f"Inženýrská analýza Eq-4: Zpřesňování Trasy (Krok {frame_idx * 4})")

    ani = FuncAnimation(fig, update, frames=len(phi_frames), blit=False)
    gif_path = os.path.join(out_dir, "routing_poc.gif")
    ani.save(gif_path, writer='pillow', fps=20)
    print(f"Saved Engineering visualization to {gif_path}")

if __name__ == "__main__":
    run_routing_poc()
