"""
# Eq-4' Contract: Physical Saturation vs Numerical Soft Caps

This contract formally replaces arbitrary heuristic bounds (`np.clip` on amplitudes) with Canonical Physical Saturation via Mode-Coupling (Variant M) and Smooth Potentials (Variant P). It also explicitly defines why spatial gradient clipping is a non-negotiable mathematical limit (CFL) rather than a "hack."

## 1. The CFL "Speed of Light" Limit (Why Gradient Clips MUST stay)
In any explicit discrete integration scheme (FTCS), there is a maximum velocity $v_{max}$ at which information can propagate without shattering causality (checkerboarding).

For the Lineum drift and diffusion terms ($D = 0.05$, $\Delta t = 1.0$, $\Delta x = 1$):
- **Diffusion Stability:** $D \frac{\Delta t}{\Delta x^2} = 0.05 \le 0.25$. This is naturally stable.
- **Drift/Flow Stability (The Danger):** The phase flow velocity is $v = c_{drift} \cdot \nabla \Phi$.
If $\Phi$ climbs to `1e6`, the velocity $v \approx 0.004 \times 10^6 \approx 4000$ cells per tick. 
The Courant-Friedrichs-Lewy (CFL) condition requires $v \frac{\Delta t}{\Delta x} \le 1$.
Thus, the wave would attempt to travel 4,000 cells in 1 tick on a grid where adjacent cells only communicate 1 step at a time. The math explodes into `NaN`.

**Conclusion (A):**
`np.clip(grad_x, -GRAD_CAP)` and `np.clip(psi, 0, PSI_AMP_CAP)` are **Mathematical CFL Protections**. They enforce the universal "Speed of Light" of the discrete grid. They are NOT heuristic hacks.

## 2. Replacing Heuristics with Physical Saturation (Missing Physics)
Conversely, clipping local buildup energy (e.g. `np.clip(amp^2, 1e4)` driving $\Phi$) is a heuristic hack. In reality, energy cannot climb infinitely because the wave must expend its own kinetic energy to warp the local geometry.
Currently, $\Psi$ drives $\Phi$ tension via `phi += reaction * |Psi|^2`, but $\Psi$ *keeps its energy*. This violates thermodynamics and creates infinite positive feedback.
**Canonical Solution:** When $\Psi$ warps the grid (creating $\Phi$ tension), $\Psi$ must expend work and lose amplitude.

```python
import numpy as np

def apply_mode_coupling(psi, phi, kappa, dt, work_transfer_strength=0.001):
    \"\"\"
    Variant M: Replaces hard clips on local_input.
    Energy is conserved. The kinetic work exerted by Psi is absorbed by Phi.
    \"\"\"
    # E_psi: The raw kinetic density available to do work.
    e_psi = np.abs(psi)**2
    
    # delta_E: The exact quantum of energy transferred from the moving wave 
    # to the structural grid tension per tick.
    delta_e = work_transfer_strength * e_psi * kappa * dt
    
    # 1. Phi GAINS the energy (creating the localized RAM tension)
    phi += delta_e
    
    # 2. Psi LOSES the kinetic energy it just spent warping the grid.
    # The new amplitude is derived by removing delta_e from e_psi.
    # If delta_e > e_psi, the wave is completely exhausted (drops to 0).
    psi_mag_new = np.sqrt(np.maximum(e_psi - delta_e, 0.0))
    
    # 3. Apply the drained magnitude back to the complex phase
    psi = (psi / (np.sqrt(e_psi) + 1e-12)) * psi_mag_new
    
    return psi, phi
```

## 3. The Smooth Potential Saturation (Variant P)
Replaces hard boundaries with asymptotic physical limits (e.g., biological or fluid binding limits).

```python
def apply_potential_saturation(raw_excitation, v_max=10.0):
    \"\"\"
    Variant P: Replaces `np.clip(raw_excitation, 0, 10.0)`.
    Uses a Michaelis-Menten inspired rational saturation.
    \"\"\"
    return v_max * (raw_excitation / (v_max + np.abs(raw_excitation)))
```

## 4. The Speed of Light vs $\mu$ Runaway
1. **The Eq-4' Speed of Light (CFL Limit):** Information in the grid evaluates via explicit diffusion stencils. The maximum propagation speed is $v_{max} = \frac{\Delta x}{\Delta t}$. Exceeding this shatters causality (numerical checkerboarding). Pure `np.clip(psi)` bounds **must** remain to enforce this universal speed limit.
2. **Does $\mu$ break stability?** The core runaway feedback is $\mu \to \Phi \to \Psi \to \Phi$. Because $\mu$ modulates the Interaction Term strictly *inside* a `tanh()` function, it is mathematically impossible for $\mu$ to violate the boundary. $\mu$ accelerates the system *towards* the saturation limit, but cannot pierce it. Therefore, $\mu$ is structurally safe.
"""
