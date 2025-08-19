# Lineum Extension — Vortex–Particle Coupling

**Document ID:** lineum-extension-vortex-particle-coupling  
**Version:** 1.0.0  
**Status:** Draft  
**Relates to:** `lineum-core.md` §6.2  
**Compatibility:** core ≥1.0.0,<2.0 ; Eq=4 ; κ static ; 2D periodic  
**Date:** 2025-08-19

---

## 1. Abstract

We formalize how phase vortices in Lineum bind into long-lived, particle-like structures (“linons”). Empirically, co-rotating vortex triads (↺↺↺ / ↻↻↻) form near-equilateral configurations stabilized by a symmetric φ basin; their interferential pattern in `arg ψ` persists for ≥20 steps. This extension provides operational detection rules, output schemas, and a validation plan for independent replication under the canonical 2D, periodic-BC regime of the core paper.

---

## 2. Motivation

The core documents robust linon dynamics but leaves micro-mechanics of binding to interpretation. This supplement isolates the vortex-binding rules: rotation sense, geometry, φ-mediated stability, and reproducible criteria. The goal is a falsifiable protocol that other groups can run on their Lineum outputs without modifying the canonical Equation (1).

---

## 3. Scope & Assumptions (canonical)

- **Dimensionality:** 2D discrete grid, **periodic BCs**.
- **κ map:** static spatial tuner sampled per step (no time evolution).
- **Inputs:** snapshots or timeseries of `ψ` (phase) and `φ` (value, ∇φ), plus run metadata.
- **Out of scope:** dynamic-κ variants, 3D, non-periodic boundaries (treat as separate experiments).

---

## 4. Definitions & Notation

| Term                 | Meaning                                                                                   |
| -------------------- | ----------------------------------------------------------------------------------------- |
| **Vortex (↺/↻)**     | Phase singularity from winding of `arg ψ` (counter-/clockwise).                           |
| **Triad**            | Unordered set of three vortices.                                                          |
| **Near-equilateral** | Triangle with edge-ratio tolerance ≤ 10% (configurable).                                  |
| **Linon**            | Localized &#124;ψ&#124;² excitation (per core).                                           |
| **Binding basin**    | Local low-&#124;∇φ&#124; pocket (often with a φ extremum) at/near the triad centroid.     |
| **Symbolic record**  | e.g., `↺⟨u ⊙ u ⊙ d⟩_△` for a co-rotating triad in triangular topology with φ-bridges (⊙). |

> **ASCII fallback:** use `CCW<C,C,D>_TRI` for ↺⟨u,u,d⟩\_△ and `BRIDGE` for ⊙ when Unicode is unavailable.

---

## 5. Expected Data Inputs

- `phi_grid_summary.csv` — φ values and (optionally) ∇φ per grid cell / per frame
- `psi_phase.(png|npy)` — phase field or images sufficient for vortex detection
- `true_trajectories.csv` (optional) — tracked linon centers over time
- Run metadata: grid size, seeds, κ-map description, noise amplitude, step count

---

## 6. Detection Algorithm (operational)

**Parameters (defaults):**

```
VORTEX_MIN_SEP = 3           # cells; de-duplicate near-overlapping cores
EQUILATERAL_TOL = 0.10       # 10% edge-ratio tolerance
STABILITY_STEPS = 20         # min consecutive frames
MAX_CENTROID_DRIFT = 2       # cells across STABILITY_STEPS
QUIET_BASIN_Q = 0.20         # centroid |∇φ| ≤ 20th percentile of local neighborhood
PHI_BRIDGE_TOL = 1           # ±1 cell around pair midpoint
```

**Steps:**

1. **Vortex identification** — compute winding of `arg ψ`; label each core as ↺ or ↻.
2. **Triad candidates** — enumerate 3-tuples with same rotation (↺↺↺ or ↻↻↻); keep near-equilateral by `EQUILATERAL_TOL`.
3. **Centroid basin check** — at triad centroid, require quiet φ pocket: local |∇φ| ≤ `QUIET_BASIN_Q` quantile; Laplacian indicates extremum (minimum/maximum) consistent with capture.
4. **Interference criterion** — between cores, detect persistent striping / nodal pattern in `arg ψ` (e.g., Fourier anisotropy vs. randomized null).
5. **Temporal stability** — track the three cores (or φ proxies) across frames; require ≥ `STABILITY_STEPS` with centroid drift ≤ `MAX_CENTROID_DRIFT`.
6. **φ-bridges (⊙)** — for each pair, test for φ extremum near pair midpoint (± `PHI_BRIDGE_TOL` cells).
7. **Emit record** — if all pass, write structured record (see §7), including symbolic form, e.g. `↺⟨u ⊙ u ⊙ d⟩_△`.

---

## 7. Output Schema (per confirmed triad)

CSV columns (suggested):

```
run_id, frame_start, frame_end, rotation (CCW/CW),
x1,y1, x2,y2, x3,y3,  # vortex core coords
a,b,c, equilateral_tol_pass,
centroid_x,centroid_y, phi_centroid, gradphi_centroid, laplace_phi_centroid,
bridge_12, bridge_23, bridge_31,        # boolean flags
interference_score, stability_steps, centroid_drift_max,
symbol, notes
```

---

## 8. Validation Plan

**A/B κ-maps:** `island` vs `constant` to contrast triad incidence, basin symmetry, bridge rate.  
**Noise sweep (ξ):** plot survival curves vs. noise amplitude.  
**Tolerance sweep:** 5–15 % equilateral tolerance; evaluate precision/recall vs. manual labels.  
**Shuffled null:** per-frame randomization of vortex positions; estimate false-positive rate (FPR).  
**Cross-runs:** replicate on `spec6_true`, `spec7_true`; pool metrics with CIs.

**Primary metrics:**

- **Incidence:** triads / 1000 frames (by rotation class).
- **Stability:** mean (±SD) confirmed frames; Kaplan–Meier survival if censoring.
- **Basin contrast:** centroid |∇φ| quantiles vs. neighborhood / background.
- **Interference score:** Fourier energy ratio in oriented bands vs. isotropic null.
- **Bridge rate:** fraction of edges with detected φ-bridge.

---

## 9. Results (empirical summary)

- Co-rotating triads occur significantly more often as stable configurations than mixed-rotation triples.
- Passing triads consistently show a quiet φ basin at the centroid and robust interferential structure in `arg ψ`.
- The ≥20-step threshold filters turbulence without suppressing genuine bindings.

_(Numerical tables belong to the validation report; this extension stays model-procedural.)_

---

## 10. Discussion

Binding emerges without explicit forces: φ provides the quiet, metric-like background shaping where |ψ|² accumulates; `arg ψ` interference encodes phase-locking between cores. Rotation sense (↺/↻) acts as a particle/antiparticle tag, while binding topology (triangle vs. chain) encodes species. We do not fix a universal taxonomy here; the symbolic layer is a pragmatic recording language.

---

## 11. Limitations & Failure Modes

- 2D canonical scope; 3D or non-periodic boundaries may alter vortex statistics.
- Vortex detection quality depends on phase unwrapping and image SNR.
- Near-equilateral constraint is pragmatic; other motifs (chains, multi-rings) need dedicated criteria.
- False positives can rise when φ gradients are globally shallow; require null controls.

---

## 12. Reproducibility Checklist

- Publish seeds, κ-map, parameter dump.
- Include raw phase fields (or reproducible FFT pipeline), φ grids, and code to recompute vortices.
- Provide overlay figures: `arg ψ` with vortex markers; φ heatmap with centroid and bridges; drift tracks.
- Export full triad CSVs and a README with parameter values matching §6 defaults or stating deviations.

---

## 13. Appendix A — Minimal Pseudocode

```python
# inputs: vortices = [(x,y,rot), ...], phi_grid, phase_field, frames
V = deduplicate_close_vortices(vortices, min_sep=VORTEX_MIN_SEP)
triads = [T for T in combinations_same_rotation(V, k=3) if near_equilateral(T, tol=EQUILATERAL_TOL)]

for T in triads:
    c = centroid(T)
    if quiet_phi_basin(phi_grid, c, q=QUIET_BASIN_Q) and persistent_interference(phase_field, T):
        if stable_over_time(T, frames, min_steps=STABILITY_STEPS, max_centroid_drift=MAX_CENTROID_DRIFT):
            bridges = detect_phi_bridges(phi_grid, T, tol=PHI_BRIDGE_TOL)  # (b12, b23, b31)
            emit_record(T, c, bridges, symbol="↺⟨u ⊙ u ⊙ d⟩_△")
```

---

## 14. Appendix B — Symbol Key

| Symbol | Meaning                                                                              |
| ------ | ------------------------------------------------------------------------------------ |
| ↺ / ↻  | CCW/CW rotation (particle/antiparticle tag)                                          |
| ⊙      | φ-bridge (local extremum between a pair)                                             |
| △      | triangular binding topology                                                          |
| `u, d` | visual/role tags for cores within triad (analogy labels; non-essential to detection) |

## 15. Versioning & Changelog

**Policy.** Semantic Versioning applies to this document; compatibility with the core is pinned in the header.  
**1.0.0 — 2025-08-19 (initial)**

- Operational criteria for co-rotating vortex triads, output schema, and validation plan (canonical 2D, periodic BCs).
