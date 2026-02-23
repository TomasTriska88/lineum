**Title:** Lineum Extension — Silent Gravity
**Document ID:** core-ext-silentgravity
**Document Type:** Extension
**Version:** 1.0.0
**Status:** Draft
**Date:** 2025-08-19

**Relates to:** `lineum-core.md` §6.1  
**Compatibility:** core ≥1.0.0,<2.0 ; Eq=4 ; κ static ; 2D periodic

---
# Lineum Extension — Silent Gravity

---

## 1. Abstract

We formalize **Silent Gravity**: an emergent, force-free tendency whereby linons statistically accumulate in low-|∇φ| regions and near φ-minima, and migrate along +∇φ as defined by the canonical update. The effect is quantified via dwell-time enrichment, basin-attraction metrics, and return-bias analyses, without introducing any explicit long-range force term. We provide operational tests, metrics, and replication guidance under the canonical 2D, periodic-BC regime.

---

## 2. Motivation

The core paper reports attraction via the φ-gradient and an interpretive note on a quiet, metric-like role of φ. This extension separates the concept into falsifiable claims with measurable criteria so independent groups can test Silent Gravity without modifying Equation (1).

---

## 3. Scope & Assumptions (canonical)

- **Dimensionality:** 2D discrete grid, **periodic BCs**.
- **κ:** static spatial map (no time evolution).
- **Inputs:** time series of ψ (magnitude/phase) and φ (value, ∇φ), plus run metadata.
- **Out of scope:** dynamic-κ variants, 3D, non-periodic boundaries.

---

## 4. Phenomenon Definition

**Silent Gravity** = The statistical tendency of linons to (i) **dwell** longer in neighborhoods with **low |∇φ|**, (ii) **accumulate** near **local φ-minima** (or quiet basins), and (iii) **drift** along **+∇φ** (environmental guidance), all **without** an explicit force term in the canonical update.

---

## 5. Operational Tests & Metrics

### 5.1 Dwell-Time Enrichment vs. |∇φ|

- Partition the domain into quantile bins of |∇φ| (e.g., Q1…Q5 per frame).
- For each bin, accumulate linon-centered dwell time.
- **Metric:** Enrichment ratio `ER = dwell(Q1) / dwell(Q5)`.
- **Pass criterion (example):** `ER > 1.5` with 95% CI not overlapping 1 across ≥3 runs.

### 5.2 Basin Capture at φ-Minima

- Detect local φ-minima via discrete Laplacian and neighborhood checks.
- Measure arrival rate and average residence within a fixed radius `r_min`.
- **Metric:** `Capture Δ = arrival_rate(minima) – arrival_rate(controls)`.
- **Pass:** `Capture Δ > 0` with bootstrap CI excluding 0.

### 5.3 Directed Drift Along +∇φ

- For each tracked linon, compute instantaneous displacement `Δx` and the local gradient direction `g = ∇φ / |∇φ|`.
- **Metric:** mean cosine alignment `⟨cos θ⟩ = ⟨ (Δx · g) / (|Δx||g|) ⟩`.
- **Pass:** `⟨cos θ⟩ > 0` with permutation-test p < 0.01.

### 5.4 Quiet-Basin Stability

- Identify **quiet basins**: neighborhoods with |∇φ| below the 20th percentile and Laplacian indicating an extremum.
- Compare survival curves (Kaplan–Meier) of linon residence inside basins vs. matched non-basin controls.
- **Metric:** hazard ratio `HR = hazard(basin) / hazard(control)`.
- **Pass:** `HR < 1` with CI below 1.

### 5.5 Null & A/B Controls

- **Null shuffle:** randomize φ fields per frame (preserve histogram), recompute metrics → all effects should collapse toward null (ER ≈ 1, ⟨cos θ⟩ ≈ 0).
- **A/B κ-maps:** island vs. constant κ to examine robustness of basin identification and metrics.

---

## 6. Results (empirical summary)

- Linon dwell time concentrates in low-|∇φ| neighborhoods; enrichment persists across seeds and grid sizes.
- Arrival and residence near φ-minima exceed matched controls.
- Mean alignment with +∇φ is significantly positive even with moderate noise.
- Survival analyses show longer residence within quiet basins.

_(Numerical tables belong to validation; this extension remains protocol-oriented.)_

---

## 7. Discussion

Silent Gravity reframes “attraction” as environmental guidance by φ-topology: φ supplies a quiet, metric-like structure that shapes where |ψ|² accumulates and for how long. No explicit long-range force is introduced; the observed behavior follows directly from local updates and gradients.

---

## 8. Limitations & Failure Modes

- Sensitive to φ-estimation quality and gradient discretization.
- Extremely flat φ landscapes reduce effect sizes (need larger samples).
- Basin detection thresholds can bias capture metrics; pre-register parameters.

---

## 9. Reproducibility Checklist

- Publish seeds, κ-map definition, parameter dump.
- Export per-frame linon positions, φ, ∇φ, and basin masks.
- Provide scripts/notebooks for binning, survival analysis, and null shuffles.
- Report CIs and effect sizes for all metrics (ER, Δ, ⟨cos θ⟩, HR).

---

## 10. Appendix — Minimal Pseudocode

```python
# inputs: trajectories, phi, grad_phi, basin_mask, frames
bins = gradphi_quantile_bins(grad_phi, q=5)            # per frame
ER = dwell_time(bins[0]) / dwell_time(bins[-1])        # Q1 vs Q5

minima = detect_phi_minima(phi)
capture_delta = arrival_rate(trajectories, minima) - arrival_rate(trajectories, controls)

align = mean_cosine_alignment(trajectories, grad_phi)  # <cos θ>

surv_basin = km_curve(residence_times(trajectories, basin_mask=True))
surv_ctrl  = km_curve(residence_times(trajectories, basin_mask=False))
HR = hazard_ratio(surv_basin, surv_ctrl)

null_ER, null_align = null_shuffle_tests(phi, grad_phi, trajectories)
```

---

## 11. Versioning & Changelog

**Policy.** Semantic Versioning applies to this document; compatibility with the core is pinned in the header.  
**1.0.0 — 2025-08-19 (initial)** — operational metrics (enrichment, capture, alignment, survival), null/A-B controls, canonical 2D scope.


---

## Appendix B — Conceptual Notes on Silent Gravity


> _The hypothesis explores the possibility that the gravitational effect in the Lineum system does not arise as an independent force, but as a byproduct of a silent tension in the φ field, which does not manifest in the dynamics of the ψ field, but determines the spatial distribution of quasiparticles._

---

## Initial Motivation

During the examination of simulations `spec1_true` to `spec3_true`, it was repeatedly observed that quasiparticles tend to cluster in certain regions, even though there are no explicit attractive forces between them. This phenomenon cannot be explained solely by the rotation of vortices or their interference in ψ, but appears to be related to gradual gradients in the φ field.

In some simulations, regions with minimal φ flux (∇φ ≈ 0) occur, which simultaneously act as natural "gravitational wells" – quasiparticles remain in these regions longer, or migrate into them, without an apparent causal mechanism in ψ.

This phenomenon has been provisionally termed "silent gravitational field" – it does not manifest turbulently, but structures space through subtle tension in φ. It may be an analogy to the metric field in classical general relativity, with the φ field here playing the role of a hidden geometric background.

---

## Hypothesis Assumptions

- Quasiparticles avoid regions with high φ gradient and accumulate in regions where ∇φ → 0.
- These regions have a higher probability of containing resonant return points.
- Tension in φ influences the energy distribution in ψ, even if it does not manifest as a direct flow.
- The gravitational effect is not an explicit force, but an emergent consequence of φ dynamics around vortex structures.

---

## Verification Criteria

- Statistical preference for the occurrence of quasiparticles in regions with low ∇φ.
- High correlation of these regions with the occurrence of resonant return points (`phi_grid_dejavu.csv`).
- Positive correlation between local φ topography and cumulative particle occurrence across multiple simulations (`spec1_true`, `spec2_true`, `spec3_true`).
- Presence of a stable φ minimum without vortex activity at its center.

---

## Status

✅ confirmed – a statistically significant correlation between silent φ regions and the occurrence of quasiparticles was found in multiple simulations. The results suggest the existence of a metric background that shapes the spatial occurrence of particles without explicit dynamics.

---

## Outlook

Silent gravity in the Lineum system can be interpreted as a **primary geometric framework** within which the ψ field organizes itself. This hypothesis connects emergent behavior with the principles of general relativity without the need to introduce traditional spacetime curvature.