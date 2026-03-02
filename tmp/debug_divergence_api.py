import numpy as np
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from lineum_core.math import evolve
from lineum_core import math as core_math
from routing_backend.translator import TranslatorV01

def debug_divergence():
    translator = TranslatorV01()
    
    seed_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'entities', 'lina_seed.npz')
    data = np.load(seed_path)
    psi = data['psi'].copy()
    phi = data['phi'].copy()
    kappa = data['kappa'].copy()
    delta = np.zeros_like(data['delta'])
    
    embed = np.random.randn(1536)
    delta_mask = translator.text_embedding_to_delta(embed)
    
    delta = delta_mask
    core_math.DT = 0.1
    
    print(f"Pre-evolve Types: PSI={psi.dtype}, PHI={phi.dtype}, DELTA={delta.dtype}, KAPPA={kappa.dtype}")
    print(f"Max PSI={np.abs(psi).max()}, Max PHI={phi.max()}, Max DELTA={delta.max()}, Max KAPPA={kappa.max()}")
    
    try:
        for i in range(50):
            psi, phi = evolve(psi, delta, phi, kappa)
            m_psi = np.abs(psi).max()
            if np.isnan(m_psi) or m_psi > 990000:
                print(f"CRASH AT STEP {i}: Max PSI={m_psi}")
                break
    except Exception as e:
        print(f"Exception at step {i}: {e}")
        
    print("Test finished.")

if __name__ == "__main__":
    debug_divergence()
