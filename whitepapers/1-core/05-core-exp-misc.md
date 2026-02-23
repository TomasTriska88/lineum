**Title:** Lineum — Experimental Track
**Document ID:** core-exp-misc
**Document Type:** Experiment
**Version:** 1.1.0-exp
**Status:** Draft
**Date:** 2025-08-23

**Depends on:** Lineum Core **v1.0.3-core**

---
# Lineum — Experimental Track (v1.1.0-exp)

> **Track policy.** This experimental track extends the frozen core (v1.0.3-core). It inherits all definitions, guardrails, and disclaimers from the core. Results here are iterative and version-stamped; artifacts include explicit `LINEUM_VERSION = v1.1.0-exp`.

## 1. Scope & objectives (pre-registered for v1.1.x-exp)

- **D1 — Dispersion ω(k):** extract k–ω map from windowed snapshots; fit small-k branch; report \(c*\*\) and \(m*\*\) (if applicable).
- **D2 — Group velocity:** pulse test; compare measured front speed with ∂ω/∂k from D1.
- **D3 — External-field response:** controlled shift of f₀ under φ-bias; report Δf₀ vs. control parameter.
- **D4 — Convergence:** Δt↓, Δx↓, grid↑; verify invariants within the core’s tolerance bands.

## 2. Methods (delta to core)

- Same codebase as core; **variants toggled via env** (no code edits):
  - `LINEUM_VERSION="v1.1.0-exp"`
  - `LINEUM_PARAM_TAG`: `disp`, `w512`, `dt05_w512`, `grid256`, `fieldX` (TBD) …
  - optional `LINEUM_SEED`
- Windowing/CI, SI constants, assertions, commit stamping = **identical** to core.

## 3. Falsifiable checks (exp)

- **(E1) Dispersion small-k fit:** reproducible \(c\_\*\) within ±5% across seeds/resolutions.
- **(E2) Group velocity match:** |v_group(measured) − ∂ω/∂k(fit)| ≤ 5%.
- **(E3) Field response:** linear (or specified) Δf₀ law within stated band on repeats.
- **(E4) Convergence:** key dimensionless ratios stable within core bands.

## 4. Evidence bundle (v1.1.0-exp)

- Artifacts will be named with version & tag, e.g.:
  - `spec6_false_s41_disp_lineum_report.html`
  - `spec6_false_s41_dt05_w512_lineum_report.html`
  - `spec6_false_s41_grid256_lineum_report.html`
- CSV/PNG/GIF mirrors included; each HTML prints `version`, `RUN_TAG`, and short **Git commit**.

## 5. Non-claims (carry-over)

We do **not** claim SM particle identification, intrinsic rest mass, GR mapping, or Lorentz invariance. “Effective mass” remains **display-only** unless explicitly superseded by dispersion-based \(m\_\*\) with stated assumptions.

## Appendix A — Results logbook (to be filled)

- [ ] D1 initial k–ω slice (seed 41)
- [ ] D2 pulse test (seed 41)
- [ ] D3 field sweep (params TBD)
- [ ] D4 convergence table
