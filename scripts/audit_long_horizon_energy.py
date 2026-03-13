import numpy as np
import scipy.ndimage
import matplotlib.pyplot as plt
import os
import sys

# Secure pathing
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import lineum_core.math as lmath

# --- Config ---
GRID_SIZE = 64
TICKS_PER_RUN = 3000   # 10x longer horizon
DT = 1.0

def generate_terrain(seed, size):
    np.random.seed(seed)
    kappa = np.random.rand(size, size) * 0.5 + 0.1
    kappa = scipy.ndimage.gaussian_filter(kappa, sigma=2.0)
    return kappa

def run_long_horizon(seed, dt=1.0, mode="C", coupling_strength=0.001):
    lmath.DT = dt
    lmath.USE_MODE_COUPLING = True
    lmath.MODE_COUPLING_STRENGTH = coupling_strength
    
    use_mu = (mode == "C")
        
    kappa = generate_terrain(seed, GRID_SIZE)
    psi = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.complex128)
    psi[GRID_SIZE//2-2:GRID_SIZE//2+3, GRID_SIZE//2-2:GRID_SIZE//2+3] += 10.0
    
    phi = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.float64)
    mu = np.full((GRID_SIZE, GRID_SIZE), 0.1, dtype=np.float64) if use_mu else None
    delta = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.float64)
    
    log_t = []
    log_E_psi = []
    log_E_phi = []
    log_E_mu = []
    
    for t in range(int(TICKS_PER_RUN / dt)):
        if use_mu:
           delta = 1.0 + mu
           
        psi, phi = lmath.evolve(psi, delta, phi, kappa)
        
        if use_mu:
            # Consistent to the identity tracking layer
            psi_mag_sq = np.abs(psi)**2
            mu += (0.005 * psi_mag_sq - 0.0001 * (mu - 0.1)) * lmath.DT
            mu = np.clip(mu, 0.001, 10.0)
            
        # Semantic Injection (Pulse every 100 ticks to test return-to-basin)
        if t % int(100/dt) == 0:
            psi[GRID_SIZE//2-2:GRID_SIZE//2+3, GRID_SIZE//2-2:GRID_SIZE//2+3] += 5.0

        if t % max(1, int(10 / dt)) == 0:
            log_t.append(t * dt)
            log_E_psi.append(float(np.sum(np.abs(psi)**2)))
            log_E_phi.append(float(np.sum(np.abs(phi))))
            if use_mu:
                log_E_mu.append(float(np.sum(np.abs(mu))))
                
    return log_t, log_E_psi, log_E_phi, log_E_mu

def main():
    print("Running Long-Horizon Thermodynamic Audit (3000 ticks)...")
    
    print("Simulating Mode B (Physics Only)...")
    tB, E_psi_B, E_phi_B, _ = run_long_horizon(seed=42, mode="B")
    
    print("Simulating Mode C (Physics + Mu)...")
    tC, E_psi_C, E_phi_C, E_mu_C = run_long_horizon(seed=42, mode="C")
    
    # Plotting E_psi
    plt.figure(figsize=(12, 12))
    
    plt.subplot(3, 1, 1)
    plt.title("Thermodynamic Kinetic Energy: $\sum |\Psi|^2$")
    plt.plot(tB, E_psi_B, label="Mode B (No $\mu$)", color="blue", alpha=0.7)
    plt.plot(tC, E_psi_C, label="Mode C (With $\mu$)", color="red", alpha=0.7)
    plt.ylabel("Kinetic Energy")
    plt.legend()
    plt.grid(True)
    
    plt.subplot(3, 1, 2)
    plt.title("Thermodynamic Substrate Pressure: $\sum \Phi$")
    plt.plot(tB, E_phi_B, label="Mode B (No $\mu$)", color="blue", alpha=0.7)
    plt.plot(tC, E_phi_C, label="Mode C (With $\mu$)", color="red", alpha=0.7)
    plt.ylabel("Structural Tension")
    plt.legend()
    plt.grid(True)
    
    plt.subplot(3, 1, 3)
    plt.title("Long-Term Historical Trace: $\sum \mu$")
    plt.plot(tC, E_mu_C, color="purple", label="$\mu$ Baseline Shift")
    plt.xlabel("Ticks")
    plt.ylabel("Historical Mass")
    plt.legend()
    plt.grid(True)
    
    plt.tight_layout()
    plt.savefig("audit_long_horizon_energy.png")
    print("Saved plot to artifact directory: audit_long_horizon_energy.png")

if __name__ == "__main__":
    main()
