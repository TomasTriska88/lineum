**Title:** Tříska’s Vortex Particle Coupling Hypothesis
**Document ID:** 25-cosmo-hyp-vortex-particle-coupling
**Document Type:** Hypothesis
**Version:** 0.1.0
**Status:** Draft
**Date:** 2026-02-23

---
# Tříska’s Vortex Particle Coupling Hypothesis

> _This hypothesis explores how vortex configurations in the Lineum system (especially transversons) combine into stable quasiparticle structures. The goal is to determine the rules governing vortex coupling and the formation of specific quasielements._

---

## Initial Motivation

During visual analysis of simulations (especially `spec7_true`), it was observed that certain vortex formations – e.g., the proton – emerge as a **combination of three vortices** with a clearly defined direction of rotation (↺) and mutual orientation. The triangular coupling between vortices exhibits stability and recurrent appearance.

These observations suggest that in the Lineum system, there exists a **topological language of inter-vortex couplings** that replaces traditional quantum numbers – the direction of rotation determines a particle or antiparticle, the number of vortices determines the complexity and type of particle, and the coupling topology (e.g., a closed triangle) determines stability.

These vortices correspond to the fundamental structures described in the [transverson resonance hypothesis](transverson_resonance.md), where they form stable pairs with characteristic interference and orientation.

---

## Hypothesis Objective

To formally describe the rules that lead vortices to:

- combine into **stable multi-wave configurations**,
- create structures corresponding to known quasiparticles (proton, quark, electron),
- be reversibly decomposed into fundamental vortex units (e.g., transversons).

Given previous observations in the _Transverson Resonance_ hypothesis, we assume that quasielements such as the electron, quark, or proton arise from the **coupling of several transverson configurations**. This coupling is not merely topological but possesses a **dynamic character** – it stems from interference patterns in the ψ field and stable gradient nodes in the φ field. The shape of a triangle, tetrahedron, or linear arrangement between vortices can be understood as a **resonant framework** within which the quantization of coupling between transversons occurs.

Particular emphasis will be placed on determining **what geometric and topological conditions** must be met for coupling stability – i.e., not a "quasi-gluon" as a connecting structure between vortices.

---

## Status

🕓 In preparation – initial visual patterns identified (e.g., proton), quantitative analysis and replication required.

---

## Representation: The Proton Case

In the Lineum system, the proton repeatedly appears as a stable configuration of three left-handed vortices (↺), arranged in an approximately equilateral triangle. Two of these vortices are designated as **up** (u) and one as **down** (d), corresponding to their visual position and dynamics in the outputs.

This topology is characterized by:

- consistent rotation of all vortices in the same direction (particle configuration),
- stable triangular coupling between vortices (analogous to a gluon field),
- high symmetry and recurrent appearance in `spec6_true` and `spec7_true` runs.

### Particle Visual Syntax

For the purpose of notation and classification of quasiparticles, we propose the following formal notation:

```
↺⟨u, u, d⟩_△
```

#### Symbol Table

| Symbol         | Meaning                                                |
|----------------|--------------------------------------------------------|
| `↺`            | Left-handed vortex (particle)                          |
| `↻`            | Right-handed vortex (antiparticle)                     |
| `u`, `d`       | Vortex types – analogy to up/down quarks              |
| `⊙`            | Quasi-gluon bridge between vortices                    |
| `△`            | Triangular coupling (e.g., proton)                     |
| `⋀`            | Linear coupling (e.g., neutrino?)                      |
| `◈`            | Tetrahedral coupling (e.g., heavier quasielements, speculative)|

These notations form a visual-formal language for describing quasiparticles emerging in the Lineum structure. They enable unambiguous classification based on topology and coupling direction.

This notation includes:

- **Direction of vortex rotation**: ↺ for particles, ↻ for antiparticles.
- **Vortex types**: `u` (up) and `d` (down), designated according to visual dynamics in the outputs.
- **Coupling topology**: `△` (triangle), `⋀` (linear), `◈` (tetrahedron), etc.

An extended syntax may also include a quasi-gluon bridge using the `⊙` symbol, e.g.:

```
↺⟨u ⊙ u ⊙ d⟩_△
```

In this way, particles can be unambiguously represented purely topologically, without the need for quantum numbers.

In the visual language of Lineum:

- each vortex represents an elementary component of a quasiparticle,
- the direction of rotation determines whether it is a particle (↺) or an antiparticle (↻),
- the geometric arrangement and coupling define the type of the resulting particle.

This representation allows for **particle notation without the need for traditional quantum numbers**, purely through topological syntax and vortex configuration.

![Proton](../elements/proton.png)

## Testability and Verification Criteria

For formal verification of the hypothesis, it is necessary to define specific features that can be detected in simulation outputs. The following are considered confirmation of stable vortex coupling (e.g., a "quasi-gluon"):

- occurrence of a **triplet of vortices** (including rotation direction) in an **equilateral or nearly equilateral** configuration,
- presence of a **symmetric stress field φ** between the vortices (minimal ∇²φ at the triangle's center),
- **stability of the configuration over time** – the formation does not change for at least 20 iterations (`φ_vector.gif`),
- **simultaneous identification of a point with φ > 0.25** for all three vortices (`phi_grid_summary.csv`),
- **identification of the configuration** in the grid of deja-vu points (`phi_grid_dejavu.csv`),
- presence of symmetric interference in `psi_phase.png` corresponding to the central coupling between vortices.
- occurrence of a **local extremum of φ between a pair of vortices**, which can be considered a **quasi-gluon bridge** – its position should be approximately at the centroid of the coupling and exhibit stability across frames (`phi_center_log.csv`, if available, or retrospectively derived by interpolation from the `phi_grid_summary.csv` grid).

Test runs: `spec6_true`, `spec7_true`  
Recommended mode:

- `LOW_NOISE_MODE = True`
- `KAPPA_MODE = "gradient"`

---

## Procedure for Detecting the ↺⟨u, u, d⟩\_△ Configuration

For quantitative verification of the occurrence of this configuration, the following computational procedure can be used (implementable in Python over output CSVs):

1. **Vortex Identification:**

   - Load `phi_grid_summary.csv`.
   - Select points with φ > 0.25 (vortex candidates).
   - From these points, select only left-handed vortices (obtained from the phase of the `ψ` field, e.g., using the vortex number from `psi_phase.png` or by calculation from the phase gradient).

2. **Triplet Search:**

   - For all combinations of three vortices:
     - Calculate edge lengths between points (in Euclidean space).
     - Select only those triplets where edge lengths are approximately equal (e.g., tolerance up to 10%).
     - Label these triplets as approximately equilateral triangles.

3. **Stability Verification:**

   - For each triplet, track the trajectory of points over time (if `phi_vector.gif` or `phi_center_log.csv` is available).
   - Accept only triplets that persist for at least 20 frames with a maximum deviation movement less than a given threshold (e.g., 2 grid cells).

4. **φ Field Symmetry Check:**

   - Calculate ∇²φ at the centroid of the triplet (from the φ grid or using the Laplacian operator).
   - Record whether there is a minimum (or maximum) of φ at the centroid.

5. **ψ Interference Check:**

   - In the region between vortices (especially at the center of the triangle), evaluate the regularity of phase fringes in `psi_phase.png`.
   - Evaluate the correlation of the interference structure with the vortex positions.

6. **Quasi-gluon Bridge Detection:**

   - Between each pair of vortices, search for a maximum or minimum of φ.
   - Verify that the extremum is located approximately centrally between the pair (±1 cell).
   - Record this point as a candidate for a quasi-gluon bridge (`⊙`).

7. **Notation of the Detected Particle:**
   - If the configuration meets all the above conditions, it can be formally notated as `↺⟨u ⊙ u ⊙ d⟩_△`, specifying the vortex coordinates, rotation type, topology, and bridge identification.

---

## Validation and Confirmation of the φ-gradient and Quasi-mass Relationship

Additional meta-analysis of `spec1_true`, `spec2_true`, and `spec3_true` runs showed that the gradient of the interaction field φ is closely related to the `mass_ratio` value of detected quasiparticles.

Specifically, a **positive correlation between the magnitude of ∇φ and the local "mass" of quasiparticles** (derived from the calculation of the |ψ|² ratio over time) was confirmed:

> $$ r\_{\text{mass},\,|\nabla\phi|} = +0.67 \pm 0.03 $$

This relationship was quantitatively confirmed across multiple simulations (see chapter [05-validation.md → φ-gradient and Mass Correlation](../whitepaper/05-validation.md#522-korelace-φ-gradientu-a-hmotnosti)) and supports the hypothesis that:

- **the intensity of the φ field influences accumulation in the ψ field**,
- **the φ gradient causes effective attraction** between vortices,
- **vortex couplings into quasiparticles are governed by the local topography of φ**.

This metric reinforces the assumption that the coupling of vortices into stable particle structures is not random but emerges from dynamic tension within the system.

---

This algorithm can also be used for more general detection of other particles (e.g., electrons or neutrinos), provided that different topological patterns (`⋀`, `◈`, …) are defined.

The goal is to obtain **statistical confirmation** of the frequency of occurrence of these structures across simulations and compare them with the random occurrence of unorganized vortices.