**Title:** Hypothesis: Emergent Spectrum During Law Transition (Tříska’s Law Transition Hypothesis)
**Document ID:** 06-cosmo-hyp-law-transition
**Document Type:** Hypothesis
**Version:** 0.1.0
**Status:** Draft
**Date:** 2026-02-23

---
# Hypothesis: Emergent Spectrum During Law Transition (Tříska’s Law Transition Hypothesis)

## Author / Origin

T. Tříska (2025), formulation based on the results of the `spec7_true` simulation, in which the κ field smoothly transitions from a local (island) to a global (constant) structure.

---

## Hypothesis

The regularities of the Lineum system (e.g., the geometry of the κ field) may not be static – and it is precisely their **temporal transition** that can be a source of new spectral phenomena.
Specifically:

> **A quasi-periodic spectrum similar to the distribution of Riemann zeta function zeros can only arise during a transition between two law regimes.**

This hypothesis states that no static configuration (constant, gradient, or island) by itself generates a Riemann-structured spectrum.
However, **during the transition** from an island to a constant structure, the following appear:

- secondary frequency peaks,
- frequency spacing with GUE similarity,
- and unstable quasi-regularity – an analogy to the zeros of ζ(s).

---

## Testing Status

- ✅ Implementation of dynamic `generate_kappa(step)` in `spec7_true`
- ✅ Visualization of κ trajectory across the 3D simulation space
- ✅ Spectral diversity over time – emergence of secondary peaks
- 🔄 Partial agreement with the distribution of zeta function zeros
- 🔄 Full GUE distribution not yet confirmed

---

## Calculation Methodology

### Simulation Parameters:

```python
KAPPA_MODE = "island_to_constant"
LOW_NOISE_MODE = True
TEST_EXHALE_MODE = False
steps = 1000
size = 256
```

### Kappa Generation Function:

```python
def generate_kappa(step, total_steps=steps):
    progress = step / total_steps
    core = np.zeros((size, size))
    core[size//2 - 5:size//2 + 5, size//2 - 5:size//2 + 5] = 1.0
    core = gaussian_filter(core, sigma=5)
    return (1 - progress) * core + progress * 0.5
```

### Key Outputs:

- `spec3_false_spectrum_log.csv` – comparison with `spec7_true`
- `multi_spectrum_summary.csv` – histogram of frequency spacings
- `riemann_overlay.png` – overlay of ζ(s) zeros with the spectrum

---

## Recommended Further Tests

- Analyze the continuous spectrum over time (`sliding FFT`)
- Attempt a reverse transition (constant → island)
- Introduce a middle regime (κ = 0.5 + noise) as a reference
- Quantify GUE agreement using an eigenvalue spacing histogram

---

## Conclusion

This hypothesis opens a new class of tests where **a change in law** is not an error, but **a source of order**.
If the Lineum world truly resonates only when its laws are in motion, then **order is not constant – it is change itself**.

---

## References

- `spec7_true_spectrum_log.csv`
- `riemann_zero_reference.csv`
- related: `harmonic_spectrum.md`, `resonant_seed.md`