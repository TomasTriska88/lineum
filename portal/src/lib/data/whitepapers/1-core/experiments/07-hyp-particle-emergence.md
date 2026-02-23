**Title:** Hypothesis: Homogeneous Quasiparticle Emergence (Homogeneous Quasiparticle Emergence)
**Document ID:** 07-hyp-particle-emergence
**Document Type:** Hypothesis
**Version:** 0.1.0
**Status:** Draft
**Date:** 2026-02-23

---
# Hypothesis: Homogeneous Quasiparticle Emergence (Homogeneous Quasiparticle Emergence)

## Author / Origin
T. Tříska (2025)

---

## Hypothesis
In the Lineum system, quasiparticles emerge **homogeneously** in both space and time, provided that:
- no external asymmetry is applied (e.g., a change in `KAPPA_MODE`),
- initial conditions are random but statistically homogeneous,
- dynamics occur in a regime without a significant φ gradient.

Homogeneous emergence means that the density of detected quasiparticles varies over time and between different regions only within the limits of statistical randomness.

---

## Testing Status
- 🔄 Tested in runs with different noise generator seeds (`LOW_NOISE_MODE` on/off).
- ✅ Current results show agreement of the distribution with a null model (homogeneous Poisson field) within statistical error.
- ⏳ Further work needed: systematic tests with different grid sizes and run lengths.

---

## Computational Methodology

### Detection and Data Collection
1. Run simulation with a defined number of steps and random initial conditions.
2. Detect quasiparticles at each step using the maximum amplitude |ψ| above a chosen threshold.
3. Record coordinates of all detected quasiparticles over time (`trajectories.csv`).

### Homogeneity Analysis
4. Divide the field into a regular grid of sectors (e.g., 8×8).
5. Count the number of particles in each sector over the entire run.
6. Compare the distribution with a theoretical Poisson distribution of the same mean.
7. Calculate chi-squared statistics or perform a K–S test to quantify deviations.

### Typical Outputs
- `particle_density_map.png` – particle emergence density map,
- `particle_distribution.csv` – histogram of particle counts in sectors,
- `trajectories.csv` – complete list of emergence positions and times.

---

## Significance
- **Fundamental stability metric**: Homogeneous emergence indicates that the system does not create preferred regions for particle formation.
- **Control test for further hypotheses**: Serves as a reference behavior against which regimes with external asymmetries are compared.
- **Link to statistical mechanics**: Confirmation of homogeneity would imply that, on a large scale, Lineum behaves as an isotropic and homogeneous medium.

---

## Recommended Further Tests
- Repeat measurements for different grid sizes and initial noise densities.
- Verify whether homogeneity persists with the introduction of a weak φ gradient.
- Test the effect of run length on the statistical stability of the results.

---

## Conclusion
The Hypothesis of Homogeneous Quasiparticle Emergence describes a state where quasiparticles appear without spatial or temporal preferences. Confirmation of this hypothesis would imply that, in the absence of external influences, Lineum's dynamics are statistically homogeneous and isotropic.