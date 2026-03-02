import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from tqdm import tqdm
import heapq

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

def run_terrain_poc():
    size = 128
    steps = 1500
    
    out_dir = os.path.join(os.path.dirname(__file__), "..", "output_routing_poc")
    os.makedirs(out_dir, exist_ok=True)
    
    psi = np.zeros((size, size), dtype=np.complex128)
    delta = np.zeros((size, size), dtype=np.float64)
    phi = np.zeros((size, size), dtype=np.float64)
    
    x = np.linspace(0, 5*np.pi, size)
    y = np.linspace(0, 5*np.pi, size)
    X, Y = np.meshgrid(x, y)
    
    terrain = np.sin(X) + np.cos(Y) + 0.5 * np.sin(2.5 * X - Y) + 0.3 * np.cos(X * 3 + Y * 2)
    terrain = (terrain - terrain.min()) / (terrain.max() - terrain.min())
    
    kappa = 0.05 + 0.95 * (1.0 - terrain)
    
    kappa[40:80, 50:70] = 0.0 
    kappa[10:30, 80:100] = 0.0
    kappa[10:110, 30:40] = 0.0 
    kappa[55:65, 30:40] = 0.6 
    
    start1_y, start1_x = 20, 10
    start2_y, start2_x = 60, 10
    start3_y, start3_x = 100, 10
    target_y, target_x = 64, 115
    
    phi_frames = []
    
    print("Running Topographical Swarm Simulation...")
    for step in tqdm(range(steps)):
        
        if step == 700:
            kappa[80:90, 50:70] = 1.0 
            
        psi[start1_y-1:start1_y+2, start1_x-1:start1_x+2] = 10.0
        psi[start2_y-1:start2_y+2, start2_x-1:start2_x+2] = 10.0
        psi[start3_y-1:start3_y+2, start3_x-1:start3_x+2] = 10.0
        
        psi[target_y-2:target_y+3, target_x-2:target_x+3] *= 0.1
        
        psi, phi = evolve(psi, delta, phi, kappa)
        psi *= (kappa > 0.05)
        
        # Save frame drastically less often to speed up rendering (10 instead of 5)
        if step % 15 == 0:
            phi_frames.append((phi.copy(), kappa.copy()))

    print("Generating Engineering Route Extractor...")
    fig, ax = plt.subplots(figsize=(8, 8))
    
    kappa_plot = ax.imshow(phi_frames[0][1], cmap='gray_r', origin='upper', interpolation='bilinear', vmin=0, vmax=1)
    
    ax.plot(start1_x, start1_y, 'o', color='c', markersize=10, zorder=20)
    ax.plot(start2_x, start2_y, 'o', color='lime', markersize=10, zorder=20)
    ax.plot(start3_x, start3_y, 'o', color='m', markersize=10, zorder=20)
    ax.plot(target_x, target_y, 'ro', markersize=15, zorder=20)
    
    def extract_path(phi_field, k_field, s_x, s_y):
        if np.max(phi_field) < 1e-3: return [], []
        
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
            if abs(cx - s_x) <= 2 and abs(cy - s_y) <= 2:
                curr = (cx, cy)
                raw_path = [curr]
                while curr in came_from:
                    curr = came_from[curr]
                    raw_path.append(curr)
                return [s_x] + [p[0] for p in raw_path], [s_y] + [p[1] for p in raw_path]
                
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
                        f_score = tentative_g_score + np.hypot(s_x - nx, s_y - ny) * 0.1
                        heapq.heappush(pq, (f_score, nx, ny))
        return [], []

    history_lines = { 'c': [], 'lime': [], 'm': [] }
    MAX_AGE = 15 # Shorter age since frames represent more steps

    print("Rendering GIF layout...")
    def update(frame_idx):
        f, k = phi_frames[frame_idx]
        kappa_plot.set_data(k)
        
        px1, py1 = extract_path(f, k, start1_x, start1_y)
        px2, py2 = extract_path(f, k, start2_x, start2_y)
        px3, py3 = extract_path(f, k, start3_x, start3_y)
        
        if len(px1) >= 2: history_lines['c'].append((px1, py1, 0))
        if len(px2) >= 2: history_lines['lime'].append((px2, py2, 0))
        if len(px3) >= 2: history_lines['m'].append((px3, py3, 0))
            
        for line in ax.lines[4:]:
            line.remove()
            
        for color, h_list in history_lines.items():
            alive = []
            # Keep history short to avoid memory leaks
            for hx, hy, age in h_list[-MAX_AGE:]:
                alpha = max(0.0, 1.0 - (age / MAX_AGE))
                width = 0.5 + 3.5 * (1.0 - (age / MAX_AGE))
                if alpha > 0.05:
                    ax.plot(hx, hy, color=color, alpha=alpha, linewidth=width, zorder=5 + alpha * 10)
                    alive.append((hx, hy, age + 1))
            history_lines[color] = alive
        
        if len(px1) >= 2: ax.plot(px1, py1, 'c-', linewidth=4.0, zorder=25)
        if len(px2) >= 2: ax.plot(px2, py2, color='lime', linewidth=4.0, zorder=25)
        if len(px3) >= 2: ax.plot(px3, py3, 'm-', linewidth=4.0, zorder=25)
        
        ax.set_title(f"Large Topography (Krok {frame_idx * 15})")
        if frame_idx % 10 == 0:
            print(f"Rendered frame {frame_idx}/{len(phi_frames)}")

    ani = FuncAnimation(fig, update, frames=len(phi_frames), blit=False)
    gif_path = os.path.join(out_dir, "routing_terrain_poc_fast.gif")
    ani.save(gif_path, writer='pillow', fps=10)
    print(f"Saved Terrain POC visualization to {gif_path}")

if __name__ == "__main__":
    run_terrain_poc()
