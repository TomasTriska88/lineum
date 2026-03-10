**Title:** Tříska’s Spectral Mirror Hypothesis
**Document ID:** 08-cosmo-hyp-spectral-mirror
**Document Type:** Hypothesis
**Version:** 0.1.0
**Status:** Draft
**Date:** 2026-02-23

---
# Tříska’s Spectral Mirror Hypothesis

## Author

T. Tříska (2025)

## Status

🧪 tested – paired spectral analysis phase

---

## Abstract

This hypothesis posits that some outputs of the Lineum system represent **phase mirroring** – their spectrum is inverse, complementary, or interferentially opposite to another output.

For example, `spec2_true` (κ = gradient) and `spec4_false` (κ = island) exhibit:

- a close frequency band (800–920 Hz after transformation),
- mutual ratio tuning (~1.048×),
- spectral destructive interference upon merging.

---

## Hypothesis

> Every output of the Lineum system has a **potential mirror image**,  
> which is spectrally similar but **phase-opposite** –  
> and these mirrors interfere with each other such that they can cancel out,  
> or create an equilibrium state with minimal energetic divergence.

---

## Specific Case

The pair `spec2_true` (gradient) and `spec4_false` (island):

- the extracted frequency series were tuned to the same range (800–920 Hz),
- their individual frequencies differ stably by ~4.8%,
- destructive interference occurred with a phase shift of `π`,
- the resulting equilibrium wave exhibits minimal spectral difference from both.

---

## Mathematical Formulation

Mirror pair:

```
s₁(t) = sin(2πf₁t)
s₂(t) = sin(2πf₂t + π)
```

Equilibrium wave:

```
x(t) = s₁(t) + s₂(t) = sin(2πf₁t) + sin(2πf₂t + π)
```

When `f₁ ≈ f₂` and with a phase shift of `π`, interference occurs:

```
x(t) ≈ 0  ⟹  destructive superposition
```

---

## Spectral Evidence

The following was performed:

- spectral comparison of outputs using Welch's method (`spectrum_difference_matrix.png`),
- construction of an interferer and an equilibrium wave (`lineum_phase_filter_gradient_vs_island.wav`),
- ratio analysis of corresponding frequencies.

The ratio values of frequencies show a stable factor of `~1.048` across the spectrum.

---

## Implications

- The existence of spectral mirrors implies a **principle of balance and compensation** within Lineum.
- Some outputs can be used as an **antipole** to another – forming a harmonic pair.
- Equilibrium outputs are an **emergent result** of interferential superposition.