```markdown
**Title:** Hypothesis: Spectral Stability of Lineum
**Document ID: 23-cosmo-hyp-spectral-stability
**Document Type:** Hypothesis
**Version:** 0.1.0
**Status:** Draft
**Date:** 2026-02-23

---
# Hypothesis: Spectral Stability of Lineum

## Author / Origin
T. Tříska (2025)

---

## Hypothesis
The dynamics of the Lineum system lead to the stabilization of a dominant frequency in the amplitude spectrum |ψ| in the central region of the field, specifically:
- independently of initial noise (within specified parameters),
- consistently across runs with identical and different random generator seeds,
- robustly against changes in grid size and run length.

Spectral stability means that, on long-term average, the spectrum exhibits a clear and reproducible dominant peak at the same or a very close frequency.

---

## Testing Status
- ✅ Confirmed in 100% of runs to date under default parameters.
- ✅ Dominant frequency varies by less than ±0.5% between runs with different seeds.
- 🔄 Tested with `LOW_NOISE_MODE` change; results indicate the same frequency with different amplitude.

---

## Calculation Methodology

### Dominant Frequency Detection
1. At each simulation step, record the amplitude |ψ| at the central point or a small central region.
2. After the run concludes, perform a Fast Fourier Transform (FFT) on the amplitude time series.
3. Identify the frequency with the highest amplitude in the FFT spectrum.

### Parameters and Settings
- Run length: ≥ 500 steps for sufficient frequency resolution.
- Sampling frequency: 1 sample per step.
- FFT window: entire run spectrum or selected stationary part.
- Optional: window functions (Hanning, Blackman) for leakage suppression.

### Typical Outputs
- `multi_spectrum_summary.csv` – table of dominant frequencies and amplitudes for multiple runs.
- `central_spectrum.png` – graph of the amplitude spectrum with the dominant frequency marked.
- `central_amplitude.csv` – time series of amplitude for the central point.

---

## Significance
- **Reproducibility**: Confirms that Lineum possesses intrinsic frequency stability independent of random initial conditions.
- **Mode Comparison**: Serves as a fundamental reference value for testing the impact of parameter or environment changes.
- **System Stability Indicator**: Deviations from the typical dominant frequency may signal impending instability or a transition to another mode.

---

## Recommended Further Tests
- Verify stability under significantly higher and lower noise levels.
- Test the influence of grid size and boundary conditions on the frequency.
- Compare results between `true` and `false` runs within the same series.

---

## Conclusion
The Hypothesis of Spectral Stability of Lineum posits that the system possesses an intrinsic eigenfrequency that manifests stably across runs and conditions. Confirmation would demonstrate that Lineum's frequency structure is a fundamental property, not a random artifact of simulation.
```