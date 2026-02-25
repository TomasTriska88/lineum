**Title:** Hypothesis: Spatial Transparency through the Tuning Field κ (Tříska’s Dimensional Transparency Hypothesis)
**Document ID:** 13-cosmo-hyp-dimensional-transparency
**Document Type:** Hypothesis
**Version:** 0.1.0
**Status:** Draft
**Date:** 2026-02-23

---
# Hypothesis: Spatial Transparency through the Tuning Field κ (Tříska’s Dimensional Transparency Hypothesis)

## Author / Origin

T. Tříska (2025), formulation based on visual observations of filaments (strings) partially disappearing behind a "fog," and vortex structures whose visual manifestation correlates with the values of the κ field.

---

## Hypothesis

The field κ(x, y) not only influences the intensity of the ϕ field's response and the calculation of vortex structures (curl), but also determines the **visual transparency** of space.

Structures such as quasiparticles, filaments, or spin vortices occur even in regions with low κ, but their visual manifestation is weak, blurred, or completely hidden.

Conversely, in regions with high κ, the same phenomena manifest sharply and "emerge to the surface."

This creates an effect similar to a **projection of a third dimension** – not geometric, but structural. κ forms an inner layer that determines what "shows up" from the field.

---

## Testing Status

## Testing Status

- ✅ Observation of vortex strings partially disappearing in regions with lower κ
- ✅ κ gradient correlates with spin sharpness in visualizations (`lineum_spin.gif`)
- ✅ "Fog" layers correspond to überlocal decrease in κ in `frames_phi.npy`
- ✅ Effect confirmed across runs `spec1_true`, `spec2_true`, `spec2_false`
- ✅ In `phi_curl_low_mass.csv` and `trajectories.csv`, it can be observed that quasiparticles neither appear nor vanish in zones with very low κ.

---

## Calculation Methodology

### Simulation Parameters:

```python
TEST_EXHALE_MODE = True
LOW_NOISE_MODE = True
steps = 1000
linon_scaling = 0.01
disipation = 0.002
κ = linear gradient 0.1 → 1.0
```

### Outputs:

- `frames_phi.npy` – confirmed layering of structures according to κ
- `frames_curl.npy` – spin visibility is related to κ values
- `lineum_spin.gif` – strings disappear in regions of lower κ
- `phi_curl_low_mass.csv` – in regions with low κ, quasiparticles do not manifest visibly

---

## Recommended Further Tests

- Visually quantify spin contrast in relation to κ (e.g., histogram of curl intensity by κ)
- Create a sharp κ-island and observe if strings "emerge" within it
- Test with κ < 0.01 (almost zero) and observe if the field truly suppresses the phenomenon
- Comparison of runs with constant κ and a gradient

---

## Conclusion

The κ field is not merely an intensity control – but also a **structural filter** that determines how deeply a phenomenon penetrates into the "visible layer" of Linea.

This effect can be compared in some visualizations to optical fog, curvature, or depth of field. κ thus creates a **projection space** that has no physical dimension – but influences everything that can be observed in Linea.

The third dimension in Linea is not the z-axis.
**It is κ.**

Simulations of the Lineum model have repeatedly confirmed this projective nature of κ.