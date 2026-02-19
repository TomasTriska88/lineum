# Lineum Extension — Return Echo

**Document ID:** lineum-extension-return-echo  
**Version:** 1.0.0  
**Status:** Draft  
**Relates to:** `lineum-core.md` §5.4  
**Compatibility:** core ≥1.0.0,<2.0 ; Eq=4 ; κ static ; 2D periodic  
**Date:** 2025-08-19

---

## 1. Abstract

We formalize **Return Echo**: a behavioral bias where future linon trajectories revisit the ε-neighborhood of prior decay locations after a delay, distinct from **Structural Closure**. Closure denotes a static φ remnant after decay; echo denotes **later arrivals** steered by local ∇φ shaping toward the old site. This document provides operational detection, metrics, controls, and validation guidance under the canonical 2D, periodic-BC scope of the core paper.

---

## 2. Motivation

The core interprets closure as a field memory independent of active ψ, and notes a separate echo phenomenon in which new linons return to prior decay coordinates. A dedicated extension is required to (i) disambiguate echo from closure, (ii) define falsifiable tests and controls, and (iii) standardize outputs for replication across runs.

---

## 3. Scope & Assumptions (canonical)

- **Dimensionality:** 2D discrete grid, periodic BCs.
- **κ map:** static spatial tuner (no temporal variation).
- **Inputs:** time series of linon detections/decays, φ and ∇φ fields (or summaries), run metadata.
- **Out of scope:** dynamic-κ variants, 3D, non-periodic boundaries.

---

## 4. Definitions

- **Decay event:** time `t0` and location `L` where a tracked linon drops below persistence criteria.
- **Echo window:** a time interval `[t0 + τ_min, t0 + τ_max]` during which revisits are checked.
- **ε-neighborhood:** set of coordinates within distance `ε` from `L`.
- **Revisit:** detection of a new (distinct) linon whose center enters the ε-neighborhood in the echo window.
- **Matched control sites:** K locations per decay matched on φ and |∇φ| quantiles but unrelated to any decay; used to estimate baseline revisit rates.
- **Null-shuffle:** randomized per-frame positions of candidate targets or time-shuffled trajectories to estimate chance revisits.

---

## 5. Operational Detection

### 5.1 Parameters (defaults)

```
EPSILON = 2                 # cells (radius)
TAU_MIN = 5                 # steps after decay (avoid immediate, trivial proximity)
TAU_MAX = 500               # steps after decay
K_CONTROLS = 10             # matched control sites per decay (φ, |∇φ| ±10% quantiles)
MAX_ID_GAP = 1              # frames tolerated between detections in tracking
PHI_MATCH_TOL = 0.10        # matching tolerance for φ and |∇φ| quantiles
```

> Tune `TAU_MAX` to your run length; report chosen values in metadata.

### 5.2 Procedure

1. Detect and log all **decay events** `(L, t0)`.
2. For each decay, construct **K** matched control sites (same frame `t0`, similar φ, |∇φ| quantiles, not overlapping any decay).
3. Scan frames `t ∈ [t0 + τ_min, t0 + τ_max]` for **revisits**: new linon centers entering `B(L, ε)`.
4. Compute **echo metrics** (below) and repeat for all decays; aggregate across runs.

### 5.3 Metrics

- **Echo Rate (ER):** `ER = P(revisit | decay) / P(revisit | control)`; report 95% CIs (bootstrap).
- **Delay Distribution:** histogram / KDE of `(t - t0)` for revisits.
- **Offset Distribution:** distances from `L` at revisit time, to assess ε sensitivity.
- **Approach Alignment:** mean `⟨cos θ⟩` of approach vector vs local `∇φ` near entry into `B(L, ε)`.
- **Occupancy Surplus:** revisit density map vs. control density map around `L`.

### 5.4 Controls

- **Null-shuffle:** randomize candidate positions or time indices; ER should → 1, alignment → 0.
- **A/B κ-maps:** `island` vs `constant` κ; echo should persist if driven by φ topology rather than κ edges alone.
- **ε/τ Sensitivity:** sweep `ε ∈ {1,2,3,4}` and `τ_max ∈ {250,500,1000}`; report ER stability.

### 5.5 Disambiguation from Closure

- **Closure check:** flag whether a **static φ remnant** (persistent imprint) exists at `L` post-decay (e.g., low-|∇φ| pocket or Laplacian extremum persisting ≥ M steps).
- **Independence test:** compute ER separately for decays **with** and **without** detected φ remnants. An echo effect that remains >1 in both strata supports a behavioral interpretation.
- **Co-occurrence report:** report fraction of echoes that occur at sites with closure vs. without closure.

---

## 6. Expected Results (summary)

- ER > 1 across seeds and κ-maps, with a unimodal delay distribution.
- Positive approach alignment (`⟨cos θ⟩ > 0`) indicating guidance by local ∇φ near re-entry.
- Occupancy surplus localized around prior decay sites; null-shuffles collapse ER → 1.

_(Full numerical tables belong in validation reports.)_

---

## 7. Limitations & Failure Modes

- Echo detection is sensitive to tracking quality (ID switches).
- Very flat φ landscapes reduce alignment signal; larger samples may be needed.
- Poor matching of control sites can bias ER; pre-register matching rules.

---

## 8. Reproducibility Checklist

- Publish seeds, κ-map, parameter dump.
- Export per-decay logs, control-site selection, revisit events, and φ/∇φ fields at relevant frames.
- Provide scripts for ER bootstrap, alignment calculations, and null-shuffles.
- Report ε/τ sensitivity and stratified ER (with/without closure).

---

## 9. Appendix — Minimal Pseudocode

```python
# inputs: decays[(L, t0)], detections[t], phi[t], gradphi[t]
for (L, t0) in decays:
    controls = match_controls(L, t0, phi[t0], gradphi[t0], k=K_CONTROLS, tol=PHI_MATCH_TOL)
    echo_hits = 0; control_hits = 0

    for t in range(t0 + TAU_MIN, min(t0 + TAU_MAX, T)):
        # echo test
        if exists_new_linon_in_ball(detections[t], center=L, eps=EPSILON):
            echo_hits += 1; break

    for C in controls:
        for t in range(t0 + TAU_MIN, min(t0 + TAU_MAX, T)):
            if exists_new_linon_in_ball(detections[t], center=C, eps=EPSILON):
                control_hits += 1; break

    record_ER_sample(echo_hit=(echo_hits>0), control_hit=(control_hits>0))

ER = bootstrap_ratio(p_echo, p_control)
```

---

## 10. Versioning & Changelog

**Policy.** Semantic Versioning applies to this document; compatibility with the core is pinned in the header.  
**1.0.0 — 2025-08-19 (initial)** — operational definition, ER metric, controls (null, A/B κ), alignment and occupancy analyses; canonical 2D scope.
