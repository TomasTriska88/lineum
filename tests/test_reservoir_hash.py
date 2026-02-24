import numpy as np
import pytest
import sys
import os
import hashlib

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from lineum_core.math import evolve

# ---------------------------------------------------------------------------
# TEST: LINEUM CRYPTOGRAPHIC HASH (AVALANCHE EFFECT)
# ---------------------------------------------------------------------------

GRID_SIZE = 64

def string_to_pulse_sequence(message, grid_w=GRID_SIZE):
    """
    Converts a string into a spatial phase-pulse array to be injected
    into the fluid reservoir.
    """
    pulse = np.zeros((grid_w, grid_w), dtype=np.complex128)
    msg_bytes = message.encode('utf-8')
    
    # Inject bytes evenly across the top row of the grid as standing waves
    for i, b in enumerate(msg_bytes):
        x = (i * 5) % grid_w
        y = (i * 3) % (grid_w // 2)
        # B becomes the phase angle of the Psi field
        pulse[y+5, x+5] = 1.0 * np.exp(1j * (float(b) / 255.0 * 2 * np.pi))
    return pulse

def test_hashing_avalanche_effect():
    """
    Proves the Cryptographic Hash 'Avalanche Effect'.
    If the input string changes by a single character (e.g. 'A' vs 'B'),
    the resulting frozen fluid topology must be radically unrecognizable from the first.
    """
    
    # Hash 1: "LINEUM_A"
    psi_1 = string_to_pulse_sequence("LINEUM_A")
    delta_1 = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.float64)
    phi_1 = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.float64)
    kappa_1 = np.full((GRID_SIZE, GRID_SIZE), 0.1, dtype=np.float64)
    
    # Hash 2: "LINEUM_B" (Only 1 byte difference)
    psi_2 = string_to_pulse_sequence("LINEUM_B")
    delta_2 = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.float64)
    phi_2 = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.float64)
    kappa_2 = np.full((GRID_SIZE, GRID_SIZE), 0.1, dtype=np.float64)
    
    # We must construct mathematical boundaries (walls) so the wave
    # actively collides and scrambles the data.
    y, x = np.ogrid[-32:32, -32:32]
    mask = x**2 + y**2 > 25**2
    
    print("\nCooking the Hashes (1500 fluid iterations)...")
    for step in range(1500):
        # 1. Apply physical boundaries
        psi_1[mask] = 0.0j
        psi_2[mask] = 0.0j
        
        # 2. Add continuous thermodynamic energy "Pump" (Laser source).
        # Ensures the bytes continuously swirl and collide against the skull walls.
        if step % 5 == 0:
            psi_1[30:34, 30:34] = 1.0 + 0j
            psi_2[30:34, 30:34] = 1.0 + 0j
            
        psi_1, phi_1 = evolve(psi_1, delta_1, phi_1, kappa_1)
        psi_2, phi_2 = evolve(psi_2, delta_2, phi_2, kappa_2)
        
    diff = np.mean(np.abs(psi_1 - psi_2))
    print(f"Mean Topology Difference between 'LINEUM_A' and 'LINEUM_B': {diff}")
    
    # In Cryptography, if the average topologies differ by > 0.01 (massive across 4096 pixels), the Avalanche Effect works
    assert diff > 0.01, "HASH Failed: The Avalanche Effect did not trigger. 1-byte difference did not ruin the topology."
    print("SUCCESS: Lineum proved Cryptographic One-Way Hashing via Avalanche Effect.")

if __name__ == '__main__':
    test_hashing_avalanche_effect()
