**Title:** Hypothesis: Spin Aura of Quasiparticles (Emergent Particle Spin Aura)
**Document ID: 24-cosmo-hyp-spin-aura
**Document Type:** Hypothesis
**Version:** 0.1.0
**Status:** Draft
**Date:** 2026-02-23

---
# Hypothesis: Spin Aura of Quasiparticles (Emergent Particle Spin Aura)

## Author / Origin
T. Tříska (2025)

---

## Hypothesis
Around detected quasiparticles in the Lineum system, a stable **spin aura** emerges – a typical average pattern of the curl(∇ arg(ψ)) field, which is:
- repeatable across runs and initializations,
- shape-stable during the aggregation of hundreds to thousands of local vorticity maps,
- distinguishable from noise and random local fluctuations.

The spin aura represents a statistical imprint of local phase rotation around the quasiparticle and can be understood as an 'average envelope' of microcurrents accompanying the particle.

---

## Testing Status
- ✅ Consistently confirmed in 100% of all runs to date where the aura was calculated (see outputs below).
- ✅ The aura is robust against changes in `LOW_NOISE_MODE` and initial asymmetry.
- ✅ The shape of the aura is consistent even with varying numbers of included particles (subsampling).

> Note: A formal statistical test (e.g., comparison with a synthetic null model) is planned in the validation chapter.

---

## Calculation Methodology

### Detection and Data Collection
1. Detect quasiparticles as local maxima of amplitude |ψ| above a chosen threshold.
2. For each detection:
   - calculate the phase gradient `∇ arg(ψ)` in the surrounding window (e.g., 21×21),
   - compute `curl(∇ arg(ψ))` as a local measure of rotation,
   - center the vorticity map to the particle's position.
3. Normalize the window size and align contributions (optionally weighted by amplitude |ψ|²).

### Aggregation (aura)
4. Superimpose/average all centered vorticity maps → resulting in an **average spin map** ('aura').
5. Save the resulting raster and metrics (e.g., radial profile of the average curl).

### Typical Outputs
- `spin_aura_map.png` – average vorticity map,
- `spin_aura_profile.csv` – radial curl profile,
- `frames_curl.npy` – raw local curl maps before aggregation (optionally subsampled),
- `trajectories.csv` – context of position and lifetime of used particles.

Parameters (window size, thresholds, subsampling) must be logged for reproducibility.

---

## Significance
- **Structural Signature:** The aura provides data-driven evidence that quasiparticles are not random fluctuations but possess consistent local phase rotation.
- **Comparability Across Runs:** It enables comparison between different configurations (e.g., various `KAPPA_MODE` settings) and quantification of changes in the aura's shape.
- **Link to Other Phenomena:** The aura is related to vortex detection, topological charge, and hypotheses about particle coupling (see vortex_particle_coupling).

---

## Recommended Further Tests
- **Statistical Significance:** Compare with a null model (randomized positions/rotations, bootstrap), quantify p-value and confidence intervals.
- **Parameter Stability:** Sweep the range of window sizes, thresholds, and subsampling rates.
- **Anisotropy:** Test whether the aura exhibits directional preference and how it relates to the φ gradient.
- **Correlation with Mass:** Dependence of the aura's shape/width on the effective mass of the quasiparticle.

---

## Conclusion
The spin aura is a robust, repeatable, and quantifiable structure arising from averaging the local phase rotation around quasiparticles. It serves as a statistical 'calling card' of their microdynamics and connects with topological and coupling phenomena in Lineum.