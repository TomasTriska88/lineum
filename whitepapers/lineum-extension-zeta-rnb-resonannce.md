# Lineum Extension — Zeta–RNB Resonance

**Document ID:** lineum-extension-zeta-rnb-resonance  
**Version:** 1.0.0  
**Status:** Draft  
**Relates to:** `lineum-core.md` §5.4 (RNB), §5.6 (spectral stability)  
**Compatibility:** core ≥1.0.0,<2.0 ; Eq=4 ; κ static ; 2D periodic  
**Date:** 2025-08-19

---

## 1. Abstract

We investigate a putative resonance between **Resonant Return Points (RNB)** detected in Lineum and the imaginary parts of the **nontrivial zeros of the Riemann zeta function** on the critical line. Using a normalized axis for comparison, preliminary analyses show a strong distributional similarity (e.g., Pearson correlation ≈ 0.9842 in one canonical family of runs), despite the fact that no zeta-related mathematics is encoded in the model. This extension formalizes the datasets, metrics, and controls required to reproduce or refute the observation under the canonical 2D, periodic-BC regime.

---

## 2. Motivation

RNBs are repeatedly visited coordinates that arise from the system’s own dynamics; they were previously nicknamed “deja‑vu points” but have been standardized as **Resonant Return Points (RNB)**. If RNB distributions echo the spacing of zeta zeros, that would suggest a surprising numerical structure emergent from purely local update rules, without explicit number theory in the code base.

---

## 3. Scope & Assumptions (canonical)

- **Dimensionality:** 2D discrete grid, **periodic BCs**.
- **κ:** static spatial map (no time evolution) in the canonical scope of this extension.
- **Signals:** RNB positions measured along a normalized axis; reference set of zeta zeros’ imaginary parts `{t_n}` on Re(s)=1/2, normalized to [0,1].
- **Evidence to date:** initial strong matches were observed on specific runs including _spec7_true_; some experiments used a κ trajectory (e.g., `island_to_constant`), which is **non‑canonical**. We separate canonical from non‑canonical evidence in reporting.

---

## 4. Data Requirements

- **RNB dataset:** per‑run CSV with normalized positions (e.g., `rnb_positions.csv`), including run ID, frame bounds, normalization method.
- **Zeta zeros:** list of the first _N_ imaginary parts `{t_n}` of zeros on Re(s)=1/2, normalized to [0,1].
- **Metadata:** grid size, Δt, seeds, κ map description (and κ trajectory if used), noise level, detection parameters.
- **Optional:** occupancy maps around RNBs, echo/closure flags, spectrum logs for cross‑checks.

---

## 5. Definitions

- **RNB (Resonant Return Point):** a coordinate (or small neighborhood) that is revisited by _distinct_ linons after prior decay at the same site, beyond a minimal delay window; RNBs are **behavioral** (not merely structural fossils).
- **Normalized axis:** affine map of the comparison coordinate to [0,1]; the same mapping must be used for both RNBs and `{t_n}`.
- **Distributional match:** similarity of empirical CDFs, histograms, or kernel density estimates under the chosen normalization.

---

## 6. Methods

### 6.1 Preprocessing

1. Build the **RNB set** for a run: detect decays, define an echo window, record revisits within ε of prior decay locations; deduplicate to unique sites.
2. Normalize coordinates to [0,1] along the chosen axis (report axis and mapping).
3. Load the first _N_ zeta zeros `{t_n}` and normalize to [0,1].

### 6.2 Comparison Metrics

- **Pearson correlation** between binned densities of RNBs and normalized `{t_n}`.
- **Euclidean distance** between normalized histogram vectors.
- **KS statistic** between empirical CDFs.
- **Peak‑alignment error:** absolute differences between leading modes of the two distributions.

### 6.3 Controls

- **Null shuffles (position):** randomize RNB positions or bootstrap with replacement; correlations should collapse toward chance.
- **Null surrogates (spacing):** compare to Poisson or Wigner surrogates with matched counts.
- **Sensitivity:** sweep bin counts, bandwidths, and _N_ (e.g., 25, 49, 75) to test stability.
- **Cross‑runs:** replicate across seeds, κ maps (constant vs island), and grid sizes.

### 6.4 Reporting

- Always report normalization, binning/bandwidth, _N_, and confidence intervals from bootstrap.
- Separate **canonical** (κ static) from **non‑canonical** (κ trajectory) results.

---

## 7. Expected Results (illustrative)

- High Pearson correlation and low Euclidean distance for canonical runs showing RNB structure.
- Robustness of the match across reasonable binning/bandwidth choices.
- Nulls reduce correlation and increase distances toward baseline.
- Some high‑index deviations (phase offset) are plausible and should be discussed.

---

## 8. Limitations & Caveats

- **Normalization bias:** different axis choices can alter apparent similarity; pre‑register mapping.
- **Finite‑sample effects:** small _N_ and sparse RNBs inflate variance; aggregate across runs.
- **Non‑canonical confounders:** κ trajectories can restructure spectra; report separately.
- **Multiple comparisons:** control for tuning of _N_, binning, and bandwidth (e.g., hold‑out or pre‑registration).

---

## 9. Reproducibility Checklist

- Publish RNB CSVs, zeros list, code for normalization and metrics.
- Share seeds, κ config, Δt, and all detection parameters (ε, τ windows).
- Provide null/surrogate scripts and cross‑run aggregation notebooks.
- Include plots of histograms, CDFs, and peak alignments with CIs.

---

## 10. Appendix — Minimal Pseudocode

```python
# inputs: rnb_positions[], zeta_zeros[]
x = normalize_to_unit_interval(rnb_positions)
t = normalize_to_unit_interval(zeta_zeros)
h_x = histogram(x, bins=B, density=True)
h_t = histogram(t, bins=B, density=True)
pearson = corr(h_x, h_t)
edist = l2_norm(h_x - h_t)
ks = ks_statistic(ecdf(x), ecdf(t))
```

---

## 11. Versioning & Changelog

**Policy.** Semantic Versioning applies to this document; compatibility with the core is pinned in the header.  
**1.0.0 — 2025-08-19 (initial)** — datasets, metrics (Pearson, Euclidean, KS), null/surrogate controls, canonical vs non‑canonical reporting, reproducibility checklist.
