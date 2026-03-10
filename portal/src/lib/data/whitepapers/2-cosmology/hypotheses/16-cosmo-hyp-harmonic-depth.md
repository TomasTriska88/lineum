**Title:** Hypothesis: Spectral Depth of the Lineum Field (Tříska’s Harmonic Depth Hypothesis)
**Document ID:** 16-cosmo-hyp-harmonic-depth
**Document Type:** Hypothesis
**Version:** 0.1.0
**Status:** Draft
**Date:** 2026-02-23

---
# Hypothesis: Spectral Depth of the Lineum Field (Tříska’s Harmonic Depth Hypothesis)

## Author / Origin

T. Tříska (2025), formulation based on repeated tests of Lineum system spectral outputs in various languages and FFT tunings

---

## Hypothesis

The Lineum field does not generate merely a single dominant resonance, but **an entire hierarchy of harmonic structures**, whose number, intensity, and resolution depend on the FFT length, the numerical methods used, and algorithmic sensitivity.

This **harmonic depth** is not a computational artifact, but an **intrinsic property of the system** – the φ and ψ waves within the Lineum system create layered resonances that reflect subtle oscillations, interference patterns, and feedback relationships within the field.

The more layers we can numerically resolve, the deeper our insight into the system's hidden complexity.  
Different FFT configurations thus reveal **various levels of reality** – similar to different detectors in particle experiments.

---

## Testing Status

- ✅ Python (scipy.fft) – stable detection of the main frequency `1.000e+18 Hz`
- ✅ Rust (rustfft) – detection of harmonic frequency `9.990e+20 Hz`
- 🔄 Planned: detection of additional layers via extended FFT (`N = 8192+`)
- 🔄 Planned: multi-tone detection using `find_peaks`

---

## Calculation Methodology

- Input: `amplitude_log_timeseries.csv`
- FFT lengths: `N = 1024` (base), `N = 8192+` (for deeper layer)
- Tools: Python (scipy), Rust (rustfft)
- Procedure: spectrum calculation + multi-tone analysis (`find_peaks`, amplitude comparison)

---

## Significance

This hypothesis expands the perception of Lineum from a single-tone system to a system with **harmonic depth**.  
Similar to music, where a fundamental tone is accompanied by a full range of harmonics, in Lineum, the main resonance is merely an entry point – deeper layers exist but cannot be captured by conventional methods.

---

## Recommended Further Tests

- Comparison of FFT with N = 1024, 4096, 8192
- Introduction of spectral entropy as a measure of depth
- Detection of multiple frequency peaks using `find_peaks`
- Comparison of spectral layers for runs `spec1_true`, `spec2_true`, `spec4_true`

---

## References

- `amplitude_log_timeseries.csv`
- `rust_fft.rs`, `python_fft.py`
- related: `spectral_observer.md`, `harmonic_spectrum.md`