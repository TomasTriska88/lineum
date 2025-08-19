**Document ID:** lineum-core  
**Version:** 1.0.0  
**Status:** Draft  
**Equation:** Eq-4 (canonical; κ static)  
**Scope:** 2D, periodic BCs  
**Date:** 2025-08-19

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
– phase gradient rotation (spin) around linons,
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

> _For the full development history of this equation, see_ [Appendix A: Equation History](lineum-core-equation-history.md).

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

_Scope note (canonical dimensionality)._ All results in this core paper use a **2D discrete grid with periodic boundary conditions**. Any 3D extensions or non-periodic boundaries are treated as **supplementary variants** and are not part of the canonical Eq. 1.

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
See §3 (Sign convention): the +∇φ term in the ψ-update explicitly defines drift toward increasing φ, hence the observed attraction is an environmental consequence of local gradients rather than an added force law.

## 5.2 Spin Aura

In 100 % of observed stable **linons**, a persistent phase gradient rotation (spin) develops around the linon in ∇ arg ψ.
This effect is robust to noise and persists until particle decay.

**Operational definition.** We define the spin aura as the time- and ensemble-averaged map of `curl(∇ arg ψ)` in a fixed-size neighborhood around detected linon centers. For each detection, the local curl map is centered on the particle and accumulated; the resulting average yields a stable, radially decaying ring-like profile. Presence of this profile is our detection criterion; its amplitude–radius curve is reported in `spin_aura_profile.csv` and the raster in `spin_aura_map.png`. This makes §5.2 falsifiable and reproducible across runs.

## 5.3 Silent Collapse

Under certain φ-damping conditions, **linons** decay without generating large-scale disturbances in ψ.  
The process is characterized by an exponential decrease in |ψ|² amplitude within the particle’s core.

## 5.4 Structural Closure

Following particle decay, residual φ-structures remain localized, maintaining their shape and magnitude over extended timesteps.  
This memory effect demonstrates φ-field stability independent of active ψ excitation.

**Note (Return Echo).** In multiple runs, locations of prior linon decay later act as weak attractors for new linons: trajectories revisit identical or ε-near coordinates after a delay. This **return echo** is distinct from Structural Closure: closure denotes a **static φ remnant** after decay; echo denotes a **behavioral bias** that steers future arrivals back to that remnant via local ∇φ shaping. See also the Return Echo hypothesis and trajectory density maps.

## 5.5 Dimensional Transparency

By applying localized κ variations, regions can be tuned to allow ψ-structures to pass through without interaction, effectively behaving as transparent zones.  
This phenomenon is reproducible for both constant and gradient κ-maps.

**Operational note.** We treat κ as a spatial tuner that gates interaction. A region with κ≈0 behaves as a _transparent_ corridor: ψ-structures neither persist nor imprint φ there, while adjacent κ>0 zones support formation and capture. Quantitatively, transparency is flagged when (i) the local count of |ψ|² maxima drops to baseline within the κ≈0 window, and (ii) φ-curl maps show no persistent imprint across that window, while both signals remain nonzero in the neighboring κ>0 zone. Island-shaped κ maps are the preferred testbed for A/B confirmation.

## 5.6 Spectral Stability

> **Current canonical measurement (example).**  
> With `Δt = 1.0e−21 s` (canonical time step), the dominant frequency measured on a canonical run (`spec6_false`) is  
> **f₀ = 1.00×10¹⁸ Hz**, which implies **E = h f₀ = 6.63×10⁻¹⁶ J ≈ 4.14 keV** and **λ = c / f₀ = 3.00×10⁻¹⁰ m**.

> **Representative run metrics (spec6_false).**  
> Spectral Balance Ratio: **SBR ≈ 2.97** (peak vs. rest, excluding ±2 bins around f₀).  
> Secondary peaks: **not pronounced** (harmonicity is minimal in this run).  
> Topology: global vortex charge stays near neutral — **|net charge| ≤ 1** for ~95% of steps (mean total vortices ≈ 93 per frame).  
> Particle lifetimes: **median 3 steps**, with rare long-lived outliers up to **1000 steps**.  
> _Note._ In this particular run the φ background shows a **faster-than-canonical** relaxation (half-life ≈ **480** steps) prior to calibration; the **canonical target remains ≈ 2000** steps.
> These values are purely unit conversions (no extra fitting) and serve as a stable anchor for replication.

Fourier analysis of long-duration runs shows that dominant oscillation frequencies remain stable over time, even with particle creation and annihilation events.  
Typical dominant frequency: ≈ 1.0×10¹⁸ Hz with <1 % variation across runs.

**Implementation robustness.** The dominant peak stays within ±0.5% across different random seeds, grid sizes, and run durations; see `multi_spectrum_summary.csv` for aggregated runs.
_See also (Harmonic Spectrum)._ Secondary harmonics co-appear with the dominant tone (e.g., 9.990×10^20 Hz); methods and cross-language checks are summarized in `hypotheses/harmonic_spectrum.md`.

# 6. Interpretation

The confirmed phenomena suggest that local field interactions in Lineum can spontaneously produce structures and behaviors typically associated with physical particles and forces.

The attraction between **linons** via φ-gradient resembles gravitational or potential-well interactions, yet arises without any explicit long-range force law. This supports the view that such interactions may emerge from environmental field tendencies rather than being fundamental inputs.

The persistence of φ-structures after particle decay (Structural Closure) indicates that the interaction field can store and maintain spatial information independently of active excitations. This property could serve as a basis for long-lived memory or boundary conditions in emergent systems.

The ability to create transparent regions through κ variation (Dimensional Transparency) demonstrates controllable interaction tuning, potentially analogous to refractive or transmissive media in optics.

Spin Aura and Spectral Stability show that once formed, linon excitations (particle-like) in the model exhibit consistent internal dynamics, maintaining stable oscillatory behavior over extended periods.

## 6.1 Silent Gravity (interpretive note)

Simulations indicate that the φ-field acts as a quiet geometric background: linons statistically prefer regions with low |∇φ| and dwell near φ-minima, while drift along +∇φ (Section 5.1) organizes their migration. This **silent gravity** is not an explicit force term, but an emergent tendency of the environment: the topology of φ shapes where density accumulates and for how long. In this view, φ provides metric-like structure without prescribing a spacetime geometry; attraction arises from local gradients and quiet basins (∇φ → 0) rather than from imposed long-range laws.

## 6.2 Vortex–Particle Coupling (interpretive note)

Stable linons frequently co-occur with small sets of phase vortices. Empirically, triads of co-rotating vortices (↺↺↺) form long-lived, near-equilateral configurations with a symmetric φ basin between the cores; we interpret these as **vortex-coupled quasi-particles**. In this picture, rotation sense acts as a particle/antiparticle tag (↺/↻), while the binding topology (e.g., triangle vs. chain) encodes species. The core paper does not fix a taxonomy; it only records that vortex triads correlate with (i) persistent interferential structure in `arg ψ`, (ii) a low-∇φ region at the triangle centroid, and (iii) ≥20-step spatial stability. Quantitative detection rules and symbols are described in the supplementary Vortex–Particle Coupling note.

## 6.3 Law Transition (interpretive note)

_Scope._ This note refers to **experimental variants** where κ changes over time (non-canonical to Eq. 1). When κ follows a slow, coherent trajectory (e.g., `island_to_constant`), the system passes through **effective regimes** without losing linon stability: interaction patterns reorganize while macroscopic order persists. We observe **spectral restructuring** (secondary peaks, spacing shifts) concurrent with the κ-trajectory, suggesting an emergent **principle of law transition**: order can remain intact while the “rules” drift smoothly.

_Evidence._ Runs with dynamic `generate_kappa(step)` show time-resolved spectral changes (see `multi_spectrum_summary.csv`, `*_spectrum_log.csv`; sliding-FFT recommended). Exploratory overlays with Riemann ζ zeros are noted but not claimed as established. See the dedicated hypothesis file for parameters and logs.

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

# 9. Versioning & Changelog

**Policy.** Semantic Versioning (MAJOR.MINOR.PATCH).

- **MAJOR**: changes to the canonical equation or scope (e.g., 3D instead of 2D).
- **MINOR**: new sections/notes, validation expansions; no breaking changes.
- **PATCH**: wording, typos, figures, formatting.

**1.0.0 — 2025-08-19 (initial canonical)**

- Pins Eq-4 (κ static), 2D + periodic BCs.
- Validation §§5.1–5.6 (incl. operational §5.2, robustness note in §5.6, operational note in §5.5).
- Interpretation: 6.1 Silent Gravity, 6.2 Vortex–Particle Coupling, 6.3 Law Transition.
- §3: explicit scope note for 2D/periodic; sign convention for +∇φ.
