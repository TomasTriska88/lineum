# Lineum Experimental — Thermo Calibration (v1.1.0-exp)

**Status:** Draft (experimental track)  
**Scope:** canonical core + explicit reservoir/noise; thermometer calibration; reporting of T and S.  
**Does _not_ change core claims.** Core stays zero-temperature deterministic; this doc defines an _extra_ apparatus.

## 1. Goal (plain English)

Define a repeatable way to talk about “temperature” and “entropy” in Lineum by:

- adding a controlled reservoir (noise/dissipation),
- calibrating a thermometer (mapping noise → T) on a reference,
- choosing a clear entropy estimator,
- and publishing falsifiable checks + artifacts.

## 2. Apparatus

- **Reservoir:** complex zero-mean noise ξ with controlled amplitude σ_ξ; optional weak dissipation δ_T for stationarity.
- **Reference thermometer:** small harmonic patch (linearized ψ) with known response → use equipartition to fit `T(σ_ξ)`.
- **Production runs:** canonical seeds (17/23/41/73) + calibrated `T(σ_ξ)`; κ static (as in core).

## 3. Definitions

- **Temperature \(T\):** scalar defined by calibrated map \(T = \mathcal{T}(\sigma\_\xi)\) from the reference experiment.  
  Store \(\mathcal{T}\) and its fit params in `*_thermo_fit.json`.
- **Entropy \(S\):** choose one and stick to it (report both if needed):
  - **Spectral entropy** \(S\_{\mathrm{spec}}\): Shannon entropy of normalized power spectrum of center trace.
  - **Field entropy** \(S\_{\mathrm{field}}\): Shannon entropy of \(|\psi|^2\) histogram over the grid (fixed binning).
- **Reporting:** mean ±95% CI over sliding windows (same bootstrap as core).

## 4. Falsifiable checks

- **(T1) Calibration sanity:** on the reference patch, variance vs. σ_ξ follows the fitted \(\mathcal{T}\) within ±10%.
- **(T2) Fluctuation–dissipation:** with tiny δ*T, measured \(S*{\mathrm{spec}}\) increases monotonically with T (no reversals).
- **(T3) Reproducibility:** at fixed T, \(S\) matches across seeds within ±10% band.
- **(T4) Zero-T limit:** as σ_ξ → 0, \(S\) approaches the deterministic baseline (core).

## 5. Outputs (per RUN_TAG_T)

- `*_thermo_fit.json` — parameters of \( \mathcal{T}(\sigma\_\xi) \) (calibration run).
- `*_thermo_summary.csv` — T, S_spec, S_field (means + 95% CI).
- `*_thermo_spectrum_plot.png` — spectra across T.
- `*_thermo_entropy_vs_T.png` — \(S\) vs. \(T\) trend with CI.

## 6. Repro manifest (example)

- Base: canonical spec6_false_s41 (Δt=1.0e−21 s, grid 128×128, κ static, float64).
- Reservoir: ξ ~ 𝒞𝒩(0, σ*ξ²), σ*ξ ∈ {0, 1e−3, 2e−3, 5e−3, 1e−2}.
- Dissipation (optional): δ_T ≪ δ_core (e.g., δ_T = 1e−4).
- Windows/CI: as in core (W=256, hop=128, bootstrap 95%).

## 7. Notes & Risks

- “Temperature” here is **operational** (via calibration), ne „fundamentální T“.
- Entropy choice must be fixed before runs; měnit definici = nový experiment.
- All numbers live in `output/` with the `{RUN_TAG_T}_…` prefix; HTML shows the calibrated T next to σ_ξ.

_Track policy:_ This is **experimental** (v1.1.x-exp). Core v1.0.3-core zůstává beze změny a neobsahuje T ani S.
