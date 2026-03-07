**Title:** Lineum EXP Note: New & Self-Similar Information
**Document ID:** core-exp-selfsimilarity
**Document Type:** Experiment
**Version:** 1.0.0
**Status:** Draft
**Date:** 2026-02-22

---
# Lineum EXP Note: New & Self-Similar Information


> [!WARNING]
> This document describes an **experimental extension** architecture ($\mu$ / Mobility Field) intended for the Lineum Portal commercial routing track. The metrics and mechanisms discussed here are **out-of-scope** for the canonical `lineum-core.md` scientific certification and do NOT participate in the SBR/Topology contract of Core v1.

## 1. Introduction & The "PC Metaphor"
In practical applications of Lineum (e.g. B2B routing, flow optimization), we face the need to persistently stabilize structural memory over time without breaking the core quantum engine's strict thermodynamic neutrality.

To explain this to engineers pedagogically (this is a communication metaphor, not a scientific physical claim):
- **$\kappa$ (ROM):** The absolute, static terrain map.
- **$\phi$ (RAM):** The short-term active tension field (Eq-7). It forms rapid flows but vanishes over its natural half-life.
- **$\mu$ (HDD):** Long-term, slowly shifting structural memory ("mobility" or "scars").
- **$\psi$ (Signal):** The blind radar stream traversing the structure.

This document formally defines the **Geometry Metrics** we use to prove that engaging the HDD ($\mu$) physically creates stable pathways without collapsing the intrinsic fractal structure of the Lineum waves into white noise.

## 2. Metric Definitions: "New & Self-Similar Information"

We evaluate the structural health of the memory fields at the end of benchmark runs (e.g., 300 steps) across severely masked, obstacle-dense environments.

### 2.1 "New Information" (Geometric Shift/Density)
These metrics measure how nervously the paths explore new configurations versus how effectively they settle and store structural complexity.

1. **`novelty_vs_prev` (L1 Convergence):**
   - **Formula:** $\frac{\sum |\phi_t - \phi_{t-\Delta}|}{\sum \phi_t}$ (Evaluated usually at $\Delta=50$ steps against the final frame).
   - **Meaning:** Measures continuous path shifting. Higher novelty means paths are wandering like smoke. Lower novelty means the structure has locked into a stable valley.
2. **`compression_proxy` (GZIP Array Bytes):**
   - **Formula:** Length in bytes of the GZIP compressed output of the raw rounded CSV array.
   - **Meaning:** An objective, topology-agnostic proxy for structural detail. A pure zero field compresses tiny. White noise compresses massive. Intricate, deep fractal veins compress to a specific distinct payload bracket.
3. **`structural_components`:**
   - **Formula:** Number of distinct connected geometric blobs (via standard Scipy labeling) evaluated strictly on the **Top $k$\%** density mask of $\phi$.

### 2.2 "Self-Similar Information" (Scale-Invariance)
Lineum forms structures that resemble root networks, rivers, and cosmic webbing. This requires proving multiscale topology.

1. **`box_counting_dim` ($D_0$):**
   - **Formula:** The fractal box-counting dimension evaluated on the Top $k$\% binary threshold mask of the field.
   - **Meaning:** Maps the exact scale-fractal nesting of the flow.
2. **`downsample_corr` (Structural Retention):**
   - **Formula:** Pearson correlation between the original masked map and the map subjected to severe downsampling ($2\times$, $4\times$, $8\times$) and upsampling interpolations back to the original grid.
   - **Meaning:** A field that correlates $>0.8$ after a $4\times$ destructive downsample loss retains massive cross-scale structural continuity (it is NOT Brownian noise).
3. **`spectrum_slope`:**
   - **Formula:** The slope of the radially-averaged 2D Power Spectrum (FFT) plotted in $\log_{10}-\log_{10}$ space. 
   - **Meaning:** Slopes approaching $-2.0$ perfectly characterize physical stochastic fractal veining.

## 3. Verified Sweep Results
(See robust cross-seed matrix at `output_mobility_v2/novelty_selfsim_sweep_summary.csv` for raw data).

Evaluating Canonical Baseline against an active Mobility $\mu$ Field (V2 Drift+Interaction architecture) yields consistent invariants across thresholds ($k \in \{1, 2, 5, 10, 20\}$%), grid sizes ($128, 256$), and seeds:

### Finding A: The HDD physically stabilizes shifting space
- Engaging V2 universally **lowers** `novelty_vs_prev` (e.g., from $\approx0.26$ to $\approx0.24$), proving paths stop wandering randomly once a deep scar is dug.
- Engaging V2 universally **raises** the `compression_proxy` bytes (e.g. from $\approx55.8$ KB to $\approx57.2$ KB), meaning the locked paths are structurally deeper and sharper than the baseline, not blurrier.

### Finding B: Lineum is Universally Scale-Invariant
- The Power Spectrum `spectrum_slope` remains locked tightly at $\approx -1.89$ to $-1.93$ independent of seed or $\mu$-intervention.
- The Downsample $4\times$ topology correlation securely anchors at $r \approx 0.85$ universally.
- The Box-Counting $D_0$ follows an exact universal growth curve against density percentiles $k$:
  - $k=1\% \rightarrow D_0 \approx 0.85$ (sparse core channels)
  - $k=5\% \rightarrow D_0 \approx 1.25$ (fully defined web)
  - $k=20\% \rightarrow D_0 \approx 1.60$ (diffuse aura filling space)

**Conclusion:** The Lineum organically creates continuous scale-invariant geometry. The experimental $\mu$ V2 extension successfully deepens and stabilizes this structure for routing purposes without destroying its physical fractal guarantees.
