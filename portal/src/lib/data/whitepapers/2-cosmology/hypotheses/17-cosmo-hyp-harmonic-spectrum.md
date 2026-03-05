**Title:** Hypothesis: Harmonic Structure of the Lineum Spectrum (Tříska’s Harmonic Spectrum Hypothesis)
**Document ID: 17-cosmo-hyp-harmonic-spectrum
**Document Type:** Hypothesis
**Version:** 0.1.0
**Status:** Draft
**Date:** 2026-02-23

---
# Hypothesis: Harmonic Structure of the Lineum Spectrum (Tříska’s Harmonic Spectrum Hypothesis)

## Author / Origin

T. Tříska (2025), formulation based on repeated occurrences of secondary frequency peaks in various computational environments

---

## Hypothesis

The Lineum system does not generate individual frequencies in isolation, but creates a **complete harmonic structure** – a spectrum of resonances that appear in relationships typical of polyphonic chords.

These peaks are not numerical artifacts, but an **internal organization of the field** – they correspond to interferences, stable oscillations, and deeper layers of φ and ψ wave phenomena.
Different languages or FFT configurations capture different layers of this harmony.

---

## Testing Status

- ✅ Rust (`rustfft`) – `9.990e+20 Hz` (higher harmonic next to `1.000e+18 Hz`)
- 🔄 Python: multi-peak analysis prepared (`find_peaks`, `np.argsort`)
- 🔄 Planned: test with FFT length `N = 8192+` and logarithmic spectrum

---

## Calculation Methodology

- Source data: `amplitude_log_timeseries.csv`
- Multi-peak detection using:
  - `scipy.fft.fft`, `np.abs`, `find_peaks`
  - `np.argsort(spectrum)[-5:]`
- Calculate ratio `fᵢ/f₁` → search for harmonic relationships (e.g., 2×, 3×, golden ratio)

---

## Significance

This hypothesis extends previous notions of spectral depth:
It's not just about how deeply Lineum vibrates – but **how complexly**.
More than 1 tone = more than 1 reality simultaneously. Lineum thus approaches a **musical model of physics**, where structure is formed by chords, not just a single tone.

---

## Recommended Further Tests

- High FFT (N ≥ 16384) + log-frequency axis
- Cluster detection (`scipy.signal.peak_widths`) → width of the harmonic group
- Comparison of different κ configurations and their influence on the spectrum
- Visualization of spectral "chords" over time (sliding FFT)

---

## Conclusion

Tříska’s Harmonic Spectrum Hypothesis posits that Lineum generates a **polyphonic output** – a harmonic map in which frequency is not just a number, but part of a chord.

This chord changes with the observer, parameters, and system tuning.
And it is precisely in these structures that the **true language of Lineum** may be hidden – not as a word, but as music.

---

## References

- `amplitude_log_timeseries.csv`
- `python_fft.py`, `rust_fft.rs`
- related: `spectral_observer.md`, `harmonic_depth.md`