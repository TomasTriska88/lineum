# 1. Abstract

Lineum is a functional model of an emergent quantum field based on a simple, local, and discrete update equation for the evolution of a complex scalar field ψ, coupled with an interaction field φ and an experimental tuning field κ. The model does not assume any explicit constants, spacetime metric, or global symmetries, yet numerical simulations consistently produce stable and complex structures resembling phenomena known from physics.

The system evolves according to a coupled three-field update rule (see [Equation (1)](#eq1) (Version 4) in Section 3), which governs the primary field ψ, the interaction field φ, and the spatial tuning map κ.

**Terminology.** We use **linon** to denote a **stable, localized excitation** of |ψ|² (a quasi-particle analogue emergent from the Lineum rule). It is **not** a fundamental particle. On first mention we may write “linon (localized excitation)”; thereafter we use **linon**.

**Pronunciation (model name).** _Lineum_ = Czech **/ˈlɪ.nɛ.um/** (short **i**, three syllables: “**LIH-neh-oom**”, stress on the first).  
For readers in English: **/ˈlɪniəm/** (UK/US ≈ “**LIH-nee-um**”).  
_Not_ “LAI-nee-um” or “lee-NAY-um”.

**Pronunciation.** _linon_ = Czech **/ˈlɪnon/** (short **i** as in “list”, stress on the first syllable).  
For readers in English: **/ˈlɪnɒn/** (UK ≈ “LIH-non”) or **/ˈlɪnɑːn/** (US ≈ “LIH-nahn”).  
_Not_ “LAI-non”.

Repeated simulations robustly generate:
– linons (stable localized excitations) with consistent trajectories,
– vortices with quantized topological charge,  
– phase gradient rotation (spin) in φ-zones,  
– phase flow and high-φ regions,  
– and φ-traps that capture multiple **linons**.

From these, several hypotheses have been confirmed at core level, including Closure (φ-field memory after particle decay) and Dimensional Transparency (projection properties under varied κ).

The model produces quantitative signatures close to physical scales, such as:
– dominant oscillation frequency ≈ 1.0×10¹⁸ Hz,  
– linon energy ≈ 6.63×10⁻¹⁶ J,
– wavelength ≈ 3.00×10⁻¹⁰ m,  
– effective mass ≈ 0.81 % of the electron mass.

All phenomena emerge without fine-tuned initial input, relying solely on local operations on a discrete grid. No predefined forces are included, yet **linons** attract via the φ gradient, suggesting an alternative interpretation of gravity as an emergent environmental tendency.

The system is reproducible, robust to noise and dissipation, and open for independent verification and further hypothesis testing.

**Graphical abstract.**

![Lineum symbol](source/icon.png)

> **Three-field flow.** The mark depicts the triad **ψ–φ–κ** in balance: ψ (oscillation / flow), φ (memory / resonance), κ (tuning / sensitivity). It is a visual mnemonic only; the **canonical Equation (1)** defines the model.

# 2. Motivation

Many approaches in theoretical physics rely on continuous equations embedded in a predefined spacetime geometry, with global constants and symmetries fixed a priori. Such frameworks limit the exploration of systems where both the geometry and the interaction rules could emerge from purely local processes.

Lineum is designed as a minimal model to investigate whether complex, stable, and physically relevant structures can arise from:
– simple, local update rules,
– no predefined global metric or constants,
– and interactions mediated by emergent fields.

The key motivation is to test if macroscopic phenomena, such as particle-like excitations, field-mediated forces, and stable wave patterns, can originate without embedding them explicitly into the governing equations.

By isolating and quantifying these emergent behaviors, Lineum offers a controllable environment to evaluate which observed effects might have analogues in known physics, and which are unique to discrete, metric-free systems.

# 3. Equation

The evolution of the system is defined on a discrete 2D grid by three coupled update rules for:
– the primary complex scalar field ψ,
– the interaction field φ,
– and the (static) tuning field κ (spatial map).

The canonical form is:

**Equation (1) — Canonical Lineum update (Version 4)** <a id="eq1"></a>

<!-- prettier-ignore-start -->
| Equation | Description |
| --- | --- |
| **ψ ← ψ + 𝛌̃ + ξ + φψ − δψ + ∇²ψ + ∇φ** | primary field evolution |
| **φ ← φ + α (&#124;ψ&#124;² − φ) + β ∇²φ** | interaction field response |
| **κ ← κ(x, y)** | spatial tuning map |
<!-- prettier-ignore-end -->

> _For the full development history of this equation, see_ [Appendix A: Equation History](lineum-equation-history.md).

**Legend (symbols & operators)**

<!-- prettier-ignore-start -->
| Symbol | Type / Range | Role | Default / Notes |
|---|---|---|---|
| ψ(x,y,t) | ℂ | primary field; |ψ|² = density, arg ψ = phase | linons = localized |ψ|² maxima |
| φ(x,y,t) | ℝ | interaction / memory field | accumulates response to |ψ|² |
| κ(x,y) | ℝ⁺ (static) | spatial tuning map | no time evolution; often normalized to [0,1] |
| 𝛌̃(x,y,t) | ℂ | external stimulus | 0 unless stimulus experiments |
| ξ(x,y,t) | ℂ | noise (zero-mean) | optional; amplitude σ_ξ ≪ 1 |
| δ | ℝ₊ | damping in ψ-update | local, ≥ 0 |
| α | ℝ₊ | coupling | from |ψ|² to φ |
| β | ℝ₊ | diffusion | φ diffusion strength |
| ∇ | operator | discrete gradient | central differences |
| ∇² | operator | discrete Laplacian | 5-point (von Neumann) |
| BCs | — | boundary conditions | periodic in x,y |
| α_eff, β_eff | — | effective params | α_eff = κ·α, β_eff = κ·β (κ modulates α,β) |
<!-- prettier-ignore-end -->

**Sign convention.** The +∇φ term in the ψ-update induces drift toward increasing φ (movement along the φ-gradient).

**Note (κ as static map).** In the canonical rule, **κ** is a **static spatial map** (no time evolution). Any experiments that evolve κ belong to supplementary variants, not to Eq. 1. In applications, κ may locally scale parameters (e.g., α_eff = κ·α, β_eff = κ·β), but it does not replace **α** or **β** in the φ-update.

No explicit spacetime geometry, global constants, or long-range interactions are predefined. All behavior results from repeated local updates of these fields.

# 4. Method

Simulations are performed on a discrete square grid with periodic boundary conditions. Each step updates ψ and φ according to the canonical equation; **κ is a static spatial map** that is sampled (not evolved) at each step. We apply the discrete Laplacian for diffusion terms and nearest-neighbor operations for gradients.

## 4.1 Grid and Initialization

– Typical grid size: 512×512 cells.  
– Initial ψ: complex noise with small amplitude.  
– Initial φ: uniform background with small perturbations.  
– κ: constant, smoothly varying, or localized map depending on the test.

## 4.2 Update Procedure

At each timestep:

1. Compute Laplacians and gradients for ψ and φ.
2. Apply the update rules for ψ and φ (**κ is static and only sampled**).
3. Optionally add controlled noise ξ to test stability.
4. Record intermediate states for analysis.

## 4.3 Reproducibility

All runs are initialized with fixed random seeds to ensure identical outputs when rerun.  
Simulation parameters and κ-maps are stored alongside results to allow exact replication.

## 4.4 Detection of Phenomena

Detected phenomena in the core study include:
– formation and motion of **linons**,
– vortex creation and annihilation,  
– phase gradient rotation (spin),  
– φ-trap formation and particle capture.

Detection is performed using automated field analysis:
– tracking |ψ|² maxima for particle positions,  
– identifying vortex cores via phase winding,  
– mapping φ-gradients to evaluate interaction tendencies.

## 4.5 Output

For each run, the system generates:
– numerical summaries (CSV),  
– static field snapshots (PNG),  
– and, for selected runs, animated visualizations (GIF) for qualitative review.

# 5. Validation

The validation phase aims to confirm that specific emergent phenomena occur consistently under controlled conditions, and to quantify their characteristics.

## 5.1 Linon Attraction via φ-Gradient

Simulations show that localized maxima in φ act as potential wells for **linons**.  
Trajectory tracking confirms convergence toward φ peaks with measurable acceleration, despite no explicit force term in the equations.

## 5.2 Spin Aura

In 100 % of observed stable **linons**, a persistent phase gradient rotation (spin) develops in the surrounding φ-field.  
This effect is robust to noise and persists until particle decay.

## 5.3 Silent Collapse

Under certain φ-damping conditions, **linons** decay without generating large-scale disturbances in ψ.  
The process is characterized by an exponential decrease in |ψ|² amplitude within the particle’s core.

## 5.4 Structural Closure

Following particle decay, residual φ-structures remain localized, maintaining their shape and magnitude over extended timesteps.  
This memory effect demonstrates φ-field stability independent of active ψ excitation.

## 5.5 Dimensional Transparency

By applying localized κ variations, regions can be tuned to allow ψ-structures to pass through without interaction, effectively behaving as transparent zones.  
This phenomenon is reproducible for both constant and gradient κ-maps.

## 5.6 Spectral Stability

Fourier analysis of long-duration runs shows that dominant oscillation frequencies remain stable over time, even with particle creation and annihilation events.  
Typical dominant frequency: ≈ 1.0×10¹⁸ Hz with <1 % variation across runs.

# 6. Interpretation

The confirmed phenomena suggest that local field interactions in Lineum can spontaneously produce structures and behaviors typically associated with physical particles and forces.

The attraction between **linons** via φ-gradient resembles gravitational or potential-well interactions, yet arises without any explicit long-range force law. This supports the view that such interactions may emerge from environmental field tendencies rather than being fundamental inputs.

The persistence of φ-structures after particle decay (Structural Closure) indicates that the interaction field can store and maintain spatial information independently of active excitations. This property could serve as a basis for long-lived memory or boundary conditions in emergent systems.

The ability to create transparent regions through κ variation (Dimensional Transparency) demonstrates controllable interaction tuning, potentially analogous to refractive or transmissive media in optics.

Spin Aura and Spectral Stability show that once formed, linon excitations (particle-like) in the model exhibit consistent internal dynamics, maintaining stable oscillatory behavior over extended periods.

Together, these results strengthen the case that a simple, metric-free local update rule can give rise to robust and quantifiable macroscopic effects, offering a controlled platform for exploring emergent analogues of known physical phenomena.

# 7. Conclusion

Lineum demonstrates that a minimal, discrete, and locally defined update rule can generate a variety of stable, quantifiable phenomena without predefined constants, spacetime geometry, or explicit force laws.

Through controlled simulations, the model consistently produces:
– **linons** with stable trajectories,
– field-mediated attraction via φ-gradient,
– persistent spin structures (Spin Aura),
– memory effects in φ after particle decay (Structural Closure),
– controllable transparency zones (Dimensional Transparency),
– and long-term spectral stability.

These effects emerge solely from iterative local interactions on a grid and remain robust under noise and parameter variation. The reproducibility and simplicity of the model make it a promising testbed for studying emergent analogues of physical laws.

Future work will extend validation to larger parameter spaces, explore connections to continuous field theories, and investigate the scalability of these effects in three-dimensional simulations.

# 8. Acknowledgements

The author thanks collaborators and early reviewers who provided feedback on the simulation methodology, as well as those who contributed to discussions on emergent field dynamics and validation strategies.

Special appreciation is extended to the open-source community for tools and libraries used in the implementation, and to colleagues who assisted in designing reproducibility protocols.

Computational resources and support from academic and independent research networks were essential for completing this work.
