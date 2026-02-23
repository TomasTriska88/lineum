import os
import sys
import numpy as np
from pathlib import Path
from scipy.ndimage import gaussian_filter

repo_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(repo_root))

GRID_SIZE = 128
NOISE_AMP = 1e-4
PSI_DIFFUSION = 0.5
PHI_DIFFUSION = 0.1
REACTION_STRENGTH = 1.0
DISSIPATION_RATE = 0.01

def get_spec6_kappa():
    return np.ones((GRID_SIZE, GRID_SIZE), dtype=np.float64) * 0.5

def detect_vortices(phase: np.ndarray) -> np.ndarray:
    p00 = phase[:-1, :-1]
    p01 = phase[:-1, 1:]
    p11 = phase[1:, 1:]
    p10 = phase[1:, :-1]
    d1 = np.angle(np.exp(1j * (p01 - p00)))
    d2 = np.angle(np.exp(1j * (p11 - p01)))
    d3 = np.angle(np.exp(1j * (p10 - p11)))
    d4 = np.angle(np.exp(1j * (p00 - p10)))
    winding = (d1 + d2 + d3 + d4) / (2 * np.pi)
    vortices = np.zeros_like(phase, dtype=int)
    block = vortices[:-1, :-1]
    block[winding > 0.5] = 1
    block[winding < -0.5] = -1
    return vortices

def run_sim(seed, steps):
    np.random.seed(seed)
    N = GRID_SIZE
    phases = np.random.uniform(0, 2*np.pi, (N, N))
    noise_amp = np.random.uniform(0, NOISE_AMP, (N, N))
    psi = (1.0 + noise_amp) * np.exp(1j * phases)
    phi = np.zeros((N, N), dtype=np.float64)
    kappa = get_spec6_kappa()
    dt = 0.01
    for _ in range(steps):
        laplace_psi = (np.roll(psi, 1, axis=0) + np.roll(psi, -1, axis=0) +
                       np.roll(psi, 1, axis=1) + np.roll(psi, -1, axis=1) - 4 * psi)
        laplace_phi = (np.roll(phi, 1, axis=0) + np.roll(phi, -1, axis=0) +
                       np.roll(phi, 1, axis=1) + np.roll(phi, -1, axis=1) - 4 * phi)
        amp_sq = np.abs(psi)**2
        reaction = (1.0 - amp_sq) * psi
        coupling = -1j * phi * psi
        dpsi_dt = kappa * (PSI_DIFFUSION * laplace_psi + REACTION_STRENGTH * reaction + coupling)
        psi += dpsi_dt * dt
        source = amp_sq - 1.0
        dphi_dt = PHI_DIFFUSION * laplace_phi + source - DISSIPATION_RATE * phi
        phi += dphi_dt * dt
    return psi, phi

print('Running minimal universe generation to isolate a Linon...')
psi, phi = run_sim(42, 2000)
phase = np.angle(psi)
vort = detect_vortices(phase)

# Find an isolated vortex
coords = np.argwhere(vort != 0)
if len(coords) == 0:
    print('No vortices found.')
    sys.exit()

import math
best_vortex = None
max_min_dist = -1
for c in coords:
    y, x = c
    min_dist = 999
    for other in coords:
        if (other == c).all(): continue
        oy, ox = other
        dist = math.hypot(y - oy, x - ox)
        if dist < min_dist: min_dist = dist
    if min_dist > max_min_dist:
        max_min_dist = min_dist
        best_vortex = c

print(f'Most isolated Linon found at y={best_vortex[0]}, x={best_vortex[1]} (distance to nearest neighbor: {max_min_dist:.1f})')

# Extract cross section [-10 to +10]
slice_radius = 10
res_phi = []
res_amp = []
x_vals = range(-slice_radius, slice_radius + 1)
ctr_y, ctr_x = best_vortex
for dx in x_vals:
    ny = (ctr_y) % GRID_SIZE
    nx = (ctr_x + dx) % GRID_SIZE
    res_phi.append(phi[ny, nx])
    res_amp.append(np.abs(psi[ny, nx]))

print('\nCROSS-SECTIONAL PROFILE OF A STABLE LINON (x-axis distance from core):')
print('dist |  Abs(Psi)  |     Phi')
print('-------------------------------')
for i, dx in enumerate(x_vals):
    print(f'{dx:4d} | {res_amp[i]:.6f} | {res_phi[i]:.6f}')

print('\nAnalysis of Core:')
print(f'Core Amplitude (Abs(Psi)): {res_amp[slice_radius]:.6f}')
print(f'Core Phi Depth: {res_phi[slice_radius]:.6f}')
print(f'Boundary Amplitude (dist=10): {res_amp[0]:.6f}')
print(f'Boundary Phi: {res_phi[0]:.6f}')
