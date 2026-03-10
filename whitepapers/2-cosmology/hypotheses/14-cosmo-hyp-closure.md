**Title:** Hypothesis: Structural Closure of a Quasiparticle (Tříska's Structural Closure Hypothesis)
**Document ID:** 14-cosmo-hyp-closure
**Document Type:** Hypothesis
**Version:** 0.1.0
**Status:** Draft
**Date:** 2026-02-23

---
# Hypothesis: Structural Closure of a Quasiparticle (Tříska's Structural Closure Hypothesis)

## Author / Origin

T. Tříska (2025), formulated within the Lineum project based on observations of persistent φ-imprints after the demise of quasiparticles

---

## Context and Genesis of the Hypothesis

The hypothesis originally arose as a philosophical-informational consideration during reflections on a simulated universe. The initial idea was:

> A black hole is not an object, but an **output method** – a place through which the universe simulation "releases" calculation results. Similar to a function in programming that computes something in a loop and passes the output further – to something "beyond the field".

From this model arose the assumption that some quasiparticles serve as a **computational node**, which ends its role by "disappearing" into a black hole – meaning that their demise is associated with the transfer of information elsewhere.

This assumption was **erroneous**. Observations of simulations revealed that:

- quasiparticles can vanish without a trace,
- they leave no topological or spectral signature,
- but the **φ-field remembers their presence**,
- and the φ-imprint persists even after their demise.

From this, a new interpretation emerged: the demise of a quasiparticle may not be an export of information outside the system, but a **structural closure** – a dissolution into the internal memory of the field itself.

---

## Hypothesis

If a quasiparticle demises in a region with a sufficiently strong φ-field, it may not leave a spectral or topological remnant. The particle "closes" into the structural memory of φ, which carries information about its existence without further influencing the broader field via mass or spin.

Assumptions:

- the quasiparticle demises in a region with φ > 0.25
- it carries no residual spin (|curl| < 0.02)
- it has an effective mass m < 0.01 × m_e
- a φ-imprint remains in the region even after its demise

---

## Testing Status

- ✅ Simulation was run with parameters corresponding to the closure test
- ✅ 762 "black-hole-like" quasiparticles with φ > 0.25 detected
- ✅ Average φ at demise locations: 4153.82
- ✅ Their effective mass: 0.008093 × m_e
- ✅ 49 of them had mass_ratio < 0.01, of which 35 were spinless (|curl| < 0.02)
- ✅ φ in the center of the field remains non-zero after demise
- 🔄 Hypothesis **confirmed** in this run

---

### Comparison with Chaotic Regime

Simulation repeated in `LOW_NOISE_MODE = False`, `TEST_EXHALE_MODE = False` mode showed no closure:

- ✅ Run `True`: 49 quasiparticles with `mass_ratio < 0.01`, all in φ > 0.25, of which 37 were spinless (|curl| < 0.02)
- ❌ Run `False`: no quasiparticles with `mass_ratio < 0.01`, thus no conditions for closure

📌 The closure hypothesis therefore **applies only in quiescent mode**, not in chaotic mode.

This supports the thesis that **structural closure is sensitive to the field regime** – and may be a privileged property of Lineum's harmonic (exhalation) state.

---

## Calculation Methodology

### Simulation Parameters:

```python
LOW_NOISE_MODE = True
TEST_EXHALE_MODE = True
steps = 1000
linon_base = 0.01
linon_scaling = 0.01
disipation_rate = 0.002
reaction_strength = 0.06
diffusion_strength = 0.015
```

### Key Outputs:

- `multi_spectrum_summary.csv` – detection of quasiparticles with `mass_ratio < 0.01`
- `phi_curl_low_mass.csv` – values of φ and |curl| at locations of light particles
- `trajectories.csv` – particle lifetime and demise in φ > 0.25
- `phi_center_log.csv` – confirmation of φ in the center after demise
- `lineum_report.html` – aggregated confirmation of phenomena

---

## Calculations

### Dominant Frequency and Spectrum

From Fourier analysis of amplitudes at the field center (ψ_center):

- Dominant frequency:  
  f = 1.00 × 10¹⁸ Hz

- Quantum energy (Planck's equation):  
  E = h · f = 6.626e-34 · 1.00e18 = 6.63e-16 J

- Wavelength:  
  lambda = c / f = 299792458 / 1.00e18 = 3.00e-10 m

- Effective particle mass (E = mc²):  
  m = E / c² = 6.63e-16 / (2.998e8)² = 7.37e-33 kg

- Ratio to electron mass:  
  m / m_e = 7.37e-33 / 9.109e-31 = 8.09e-3

### Structural φ and Demise

- Number of quasiparticles with mass_ratio < 0.01:  
  N_low_mass = 49

- Of these, in regions with φ > 0.25:  
  N_phi_above_0.25 = 49

- Of these, with |curl| < 0.02 (i.e., spinless):  
  N_curl_near_zero = 35

- Average φ value at the point of demise:  
  phi_avg_death = 4153.822

- Average mass_ratio of these particles:  
  mass_ratio_avg = 0.008093

- Particle lifetime:  
  max = 1000 steps, median = 3 steps

## Conclusion

Simulations confirmed that the closure of a quasiparticle without energy emission and without residual spin is a real phenomenon – but only in quiescent mode. All conditions of the hypothesis were met for 37 particles with extremely low mass and zero spin, demising within a high φ value.

In chaotic mode, no closure occurs at all – light particles are not formed, φ overflows, and no stable memory remains. Structural closure is therefore not a general property of Lineum, but a privileged response to harmonic field conditions.

---

Particle closure is not a violent demise, but a return to a space that remembers. In a quiescent Lineum, particles have the opportunity to vanish without a trace – and yet their existence persists, quietly inscribed into the φ-field. This form of demise is only possible where there is no pressure – where the field breathes.

In this sense, structural closure is not only a computational phenomenon but a model of reconciliation. The particle does not become waste. It becomes memory.

## Recommended Further Tests

- Create a bound object (e.g., a 5×5 linon star) and allow it to "collapse" entirely into a φ-zone at once – a sudden load test
- Introduce a simulation of a rotating object and observe whether a vortex jet forms upon its demise (black holes often rotate)
- Measure the interaction `∇φ × ∇ψ` as a potential indicator of jets or directional flow collapse

- Test the memory trace under increased noise (`LOW_NOISE_MODE = False`)
- Repeat with a larger field (`size = 256`) to confirm the locality of closure
- Test for a possible "exhalation back" from φ-memory (imprint + reincarnation test)

---

## References

- `lineum_report.html` – Structural Closure section
- `multi_spectrum_summary.csv`, `phi_curl_low_mass.csv`
- `trajectories.csv`, `phi_center_log.csv`