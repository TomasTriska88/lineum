# Lineum Extension — Spectral Structure

**Document ID:** lineum-extension-spectral-structure  
**Version:** 1.0.0  
**Status:** Draft  
**Relates to:** `lineum-core.md` §5.6  
**Compatibility:** core ≥1.0.0,<2.0 ; Eq=4 ; κ static ; 2D periodic  
**Date:** 2025-08-19

---

## 1. Abstract

We consolidate Lineum's spectral phenomena into a single extension covering **Spectral Balance**, **Harmonic Spectrum**, and **Harmonic Depth**. We provide operational definitions, detection algorithms, controls, and reporting standards for reproducible analysis of the dominant tone and its secondary structure under the canonical 2D, periodic-BC regime. The goal is to standardize spectra across runs, seeds, and implementations, enabling independent replication and cross-language checks.

---

## 2. Motivation

The core paper documents a stable dominant frequency with low across-run variance. Multiple hypotheses have noted secondary peaks and layered structure. This extension formalizes the spectral toolkit: how to compute spectra, define peak sets, quantify harmonicity, and evaluate persistence (depth) across time, runs, and parameter sets.

---

## 3. Scope & Assumptions (canonical)

- **Dimensionality:** 2D discrete grid, **periodic BCs**.
- **κ:** static spatial map (no time evolution).
- **Signals:** per-frame fields of ψ (magnitude/phase) and φ; spectra computed from chosen scalar time series (see §4).
- **Out of scope:** dynamic-κ variants, 3D, non-periodic boundaries (treat separately).

---

## 4. Definitions & Notation

| Term                             | Meaning                                                                                                  |
| -------------------------------- | -------------------------------------------------------------------------------------------------------- |
| **Sampling step (Δt)**           | Simulation time step per frame.                                                                          |
| **Signal**                       | Scalar observable used for spectrum (e.g., global mean of &#124;ψ&#124;², or spatial FFT energy at k=0). |
| **Dominant frequency (f₀)**      | Frequency of the largest spectral peak of the chosen signal.                                             |
| **Spectral Balance Ratio (SBR)** | `SBR = P(f₀) / P(rest)` where `P(rest)` excludes a ±δf window around f₀.                                 |
| **Harmonic set (H)**             | Detected secondary peaks `{fᵢ}` above a threshold; see §6.2 for rules.                                   |
| **Harmonicity score (HS)**       | Minimum normalized distance of `{fᵢ}` to rational multiples of f₀ within tolerance τ.                    |
| **Harmonic Depth (D)**           | Persistence of the harmonic set across time windows and runs (e.g., mean Jaccard overlap).               |
| **Window**                       | Sliding segment of length `W` frames with hop `H`.                                                       |
| **Spectral leakage guard**       | Window function (e.g., Hann) and zero-padding used to stabilize peak estimation.                         |

> Use one primary signal throughout a study; recommended default: global mean of &#124;ψ&#124;² per frame.

---

## 5. Data Requirements

- Time series: length `T` frames of the chosen scalar signal; record Δt.
- Windowing config: `W`, `H`, window function, zero-padding factor.
- Run metadata: grid size, seeds, κ-map description, noise amplitude, step count, implementation ID (language/build).

---

## 6. Methods

### 6.1 Spectral Balance (SBR)

**Parameters (defaults):**

```
WINDOW_LEN W = 1024          # frames
HOP_LEN H   = 256            # frames
PEAK_GUARD δf = 2 bins       # excluded around f₀ for P(rest)
PEAK_MIN_PROM = 6 dB         # min prominence for f₀
```

**Procedure:**

1. Compute STFT (or windowed FFT of the signal) with Hann window and zero-padding ×2.
2. For each window, locate the dominant peak `f₀` (max power, ≥ PEAK_MIN_PROM).
3. Compute `P(rest)` as total power minus the energy within ±δf bins around `f₀`.
4. Report window-wise `SBR`; aggregate as median and IQR across windows.  
   **Robustness:** Report variance of `f₀` across windows; stable systems should show narrow spread.

### 6.2 Harmonic Spectrum (secondary peaks)

**Parameters (defaults):**

```
PEAK_MIN_PROM_SEC = 3 dB     # min prominence for secondary peaks
MULTIPLES R = {1/2, 2/3, 3/2, 2, 3}   # tested rational relations to f₀
TOL τ = 0.01                  # relative tolerance for |fᵢ - r·f₀| / f₀
MAX_PEAKS = 8
```

**Procedure:**

1. After identifying `f₀`, find local maxima above `PEAK_MIN_PROM_SEC`.
2. Keep at most `MAX_PEAKS` by descending power.
3. For each `{fᵢ}`, compute `min_r |fᵢ - r·f₀| / f₀` over `r ∈ R`; mark _harmonic-consistent_ if `< τ`.
4. Report the set `H` and the **Harmonicity Score (HS)** as the average minimum distance across retained peaks.

**Null controls:** Phase-scramble the signal or shuffle frame order; harmonic consistency should drop toward chance.

### 6.3 Harmonic Depth (persistence across time & runs)

**Parameters (defaults):**

```
DEPTH_WINDOW = 8             # number of consecutive analysis windows
JACCARD_MIN  = 0.5           # threshold for considering two sets 'consistent'
```

**Procedure:**

1. Define peak sets `H_t` per window `t`.
2. Compute pairwise Jaccard similarity `J(H_t, H_{t+1}) = |H_t ∩ H_{t+1}| / |H_t ∪ H_{t+1}|`.
3. Define **Depth D** as the mean Jaccard over a block of `DEPTH_WINDOW` windows and across runs/seeds.
4. Report the distribution of `D` and the fraction of adjacent windows with `J ≥ JACCARD_MIN`.

**Cross-implementation check:** Repeat on two independent implementations; report overlap of `H` and `D`.

---

## 7. Controls & Sensitivity Analyses

- **Nulls:** phase-scramble, time-shuffle, or use AR(1) surrogates with matched power.
- **Window sensitivity:** vary `W ∈ {512, 1024, 2048}` and `H ∈ {128, 256, 512}`.
- **Prominence thresholds:** ±3 dB sweeps for primary/secondary peaks.
- **Zero-padding:** ×1, ×2, ×4; confirm `f₀` stability and harmonic labels.
- **Implementation variance:** repeat analyses across languages/builds; compare `f₀` and `H` overlap.

---

## 8. Expected Results (summary)

> **Canonical anchor (example).**  
> With `Δt = 1.0e−21 s` (canonical time step), a canonical run (`spec6_false`) yields  
> **f₀ = 1.00×10¹⁸ Hz**, **E = h f₀ = 6.63×10⁻¹⁶ J ≈ 4.14 keV**, **λ = c / f₀ = 3.00×10⁻¹⁰ m**.  
> These are direct unit conversions and serve as a replication anchor for all spectral analyses (SBR, harmonicity, depth).

> **Representative metrics (spec6_false).**  
> **SBR ≈ 2.98** with a ±2-bin guard around f₀. Secondary peaks are **not prominent**, i.e., harmonicity is low in this run.  
> The dominant frequency **f₀ = 1.00×10¹⁸ Hz** is **consistent across sampled points** (see multi-point spectrum logs).

- **Stable f₀** with narrow within-run variance and small across-run drift.
- **Consistent secondary structure**: a limited set of peaks harmonic-consistent with `f₀` under τ.
- **Non-trivial depth**: adjacent-window Jaccard above random baseline; persistence across seeds.
- **Nulls collapse harmonicity**: HS approaches chance; `H` overlap drops.

_(Detailed numeric tables belong in validation reports.)_

---

## 9. Limitations & Failure Modes

- Aliasing and leakage can bias peak positions; ensure Δt and zero-padding are reported.
- Short runs (T ≪ W) reduce reliability; prefer `T ≥ 8W`.
- Global signal choice can mask localized dynamics; document the observable used.
- Grid-size resonances may introduce spurious peaks; compare across sizes.

---

## 10. Reproducibility Checklist

- Publish seeds, κ-map, Δt, grid size, noise amplitude, and full parameter dump.
- Provide raw signal time series (CSV) and windowing config.
- Share code to compute STFT/FFT, peak picking, harmonic labeling, and Jaccard depth.
- Include null and sensitivity scripts; report CIs for SBR, HS, and D.

---

## 11. Appendix A — Default Parameters

```
WINDOW_LEN = 1024
HOP_LEN = 256
PEAK_GUARD = 2 bins
PEAK_MIN_PROM = 6 dB
PEAK_MIN_PROM_SEC = 3 dB
R = {1/2, 2/3, 3/2, 2, 3}
TOL = 0.01
DEPTH_WINDOW = 8
JACCARD_MIN = 0.5
```

---

## 12. Appendix B — Minimal Pseudocode

```python
# inputs: signal[t], dt, W, H
windows = sliding_windows(signal, W, hop=H, window='hann', pad=2)
records = []
for win in windows:
    spec = fft_power(win)
    f0 = pick_peak(spec, min_prom_db=6)
    sbr = power_at(f0, guard=2) / power_rest(spec, exclude=f0, guard=2)
    peaks = pick_secondary_peaks(spec, min_prom_db=3, max_peaks=8)
    H = []
    for fi in peaks:
        dmin = min(abs(fi - r*f0)/f0 for r in [0.5, 2/3, 1.5, 2, 3])
        if dmin < 0.01:
            H.append(fi)
    records.append((f0, sbr, H))

# Depth: compute Jaccard(H_t, H_{t+1}) and aggregate
```

---

## 13. Versioning & Changelog

**Policy.** Semantic Versioning applies to this document; compatibility with the core is pinned in the header.  
**1.0.0 — 2025-08-19 (initial)** — consolidated methods and metrics for Spectral Balance, Harmonic Spectrum, and Harmonic Depth; canonical 2D scope.
