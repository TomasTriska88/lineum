# Lineum Core (v1.0.6-core)

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.16934359.svg)](https://doi.org/10.5281/zenodo.16934359)
[![Donate](https://img.shields.io/badge/Donate-Revolut-ff69b4?logo=revolut)](https://revolut.me/tomastriska)
[![arXiv Endorsement](https://img.shields.io/badge/Need-arXiv%20endorsement-blue?logo=arxiv)](https://arxiv.org/auth/endorse?x=ZYULU9)

**Status:** Public, reproducible core release • **Tag:** `v1.0.6-core` • **Paper:** `whitepaper/lineum-core.md`  
**Evidence:** `output/evidence_v1.0.6-core.zip` (HTML + CSV/PNG/GIF + Figure 0)

## TL;DR

A reproducible, parameter-light emergence of a **stable localized excitation** (“linon”) with a canonical, **bin-centered** tone _f₀_, **seed-invariant** across runs. All SI quantities (E, λ, display-only m/mₑ) are direct unit conversions from _f₀_; the “effective mass” is a **display-only** scale cue (no rest-mass claim). **Structural Closure** (φ center-trace half-life + localized φ remnant) is in-scope for the v1.0.x core; trajectory-bias phenomena such as **Return Echo** and **Dimensional Transparency** live in the experimental/extension track. Tooling guardrails (commit stamping, HTML ground truth, CIs) make it **auditable and falsifiable**.

> **60-second check.** Open `output/spec6_false_s41_lineum_report.html` → table **Quasiparticle Properties** shows:  
> `f₀ = 3.91e+18 Hz`, `E ≈ 2.59e−15 J (~16.15 keV)`, `λ ≈ 7.67e−11 m`, `m/mₑ = 0.0316 (3.16%)`.  
> See also **Figure 0**: `output/spec6_false_s41_figure0_canonical.png`.

---

## Quickstart (no code edits)

**Windows PowerShell**

```powershell
# baseline
$env:LINEUM_SEED="41"; python lineum.py
# variants
$env:LINEUM_PARAM_TAG="w512";       python lineum.py
$env:LINEUM_PARAM_TAG="dt05_w512";  python lineum.py
$env:LINEUM_PARAM_TAG="grid256";    python lineum.py
```

**bash/macOS**

```bash
# baseline
LINEUM_SEED=41 python3 lineum.py
# variants
LINEUM_PARAM_TAG=w512      python3 lineum.py
LINEUM_PARAM_TAG=dt05_w512 python3 lineum.py
LINEUM_PARAM_TAG=grid256   python3 lineum.py
```

## Outputs (ground truth)

- HTML report: `output/spec6_false_s41_lineum_report.html`
- Figure 0: `output/spec6_false_s41_figure0_canonical.png`
- CSV metrics: `output/spec6_false_s41_metrics_summary.csv`
- Bundle: `output/evidence_v1.0.6-core.zip`

## What’s in the paper (core)

- **Claim:** reproducible localized excitation with bin-centered _f₀_, SI-anchored conversions, and seed invariance, plus **Structural Closure** as an in-scope consequence of the φ center-trace half-life.
- **Guardrails:** mass-from-_f₀_ consistency, commit provenance, formatting policy, CIs.
- **Verification:** C1 (W=512), C2 (Δt→½, Δf fixed), C3 (grid 256×256).
- **Figure 0:** canonical spectrum + time trace.  
  See `whitepaper/lineum-core.md` (§§4–5, Appendices C–F).
- **Scope split:** core v1.0.x keeps κ static and treats Return Echo / Dimensional Transparency as **extension-track** hypotheses (see `lineum-exp-*` / `lineum-extension-*`).

---

## How to cite

Tomáš Tříska. _Lineum Core (v1.0.6-core)._ 2025. DOI: [10.5281/zenodo.16934359](https://doi.org/10.5281/zenodo.16934359).  
_(This release corresponds to Git tag `v1.0.6-core`; HTML/CSV/PNG/GIF artifacts live in `output/` and are commit-stamped.)_

BibTeX:

```bibtex
@software{triska2025_lineumcore_v106,
  author = {Tomáš Tříska},
  title  = {Lineum Core (v1.0.6-core)},
  year   = {2025},
  doi    = {10.5281/zenodo.16934359},
  url    = {https://doi.org/10.5281/zenodo.16934359},
  note   = {Core manuscript: whitepaper/lineum-core.md (CC BY 4.0). Code \& tooling: MIT. Structural Closure is in-scope in v1.0.x; extensions (Return Echo, Dimensional Transparency) live in lineum-exp-*/lineum-extension-*.}
}
```

## Repro environment

- Python ≥ 3.10; NumPy ≥ 1.24; SciPy ≥ 1.10; Matplotlib ≥ 3.7; Pandas ≥ 2.0; Pillow ≥ 9.5; tqdm ≥ 4.65
- Install:

```bash
python -m pip install "numpy>=1.24" "scipy>=1.10" "matplotlib>=3.7" "pandas>=2.0" "pillow>=9.5" "tqdm>=4.65"
```

**Variants via env (no code edits):**

- `LINEUM_PARAM_TAG`: `w512`, `dt05_w512`, `grid256` (+ future: `disp`, …)
- `LINEUM_SEED`: optional seed override (e.g. `23`)

---

## License

Code & tooling: MIT License (see `LICENSE`).
Manuscript text & figures in `whitepaper/`: CC BY 4.0 (see the license note in `whitepaper/`).

---

## Verification & Testing

This project enforces a **"No Temporary Tests"** policy. All changes must be verified using permanent, reusable test suites. Diagnostic or "quick" scratch scripts are only for exploration and should not be used as final proof of work.

- **Lineum Core**: `pytest tests/` (Physics, simulation logic)
- **Portal (Wiki)**: `cd portal && npm run test` (Loaders, metadata, assets)
- **Simulacrum (Lab)**: `cd lab && npm run test` (Visualizations, harmonics)

Refer to [Running Tests](file:///c:/Users/Tomáš/Documents/GitHub/lineum-core/.agent/workflows/test.md) for detailed instructions.

---

_Notes:_ This `README` supersedes older wiki/sample paths. Canonical artifacts for the core release live in `output/`.

---

## Support & Endorsement

If you find Lineum valuable and would like to support further development, you can contribute here:  
👉 [Donate via Revolut](https://revolut.me/tomastriska)

At this stage, community support is also welcome in the form of **arXiv endorsements**, which are required for submission:  
👉 [arXiv Endorsement Link](https://arxiv.org/auth/endorse?x=ZYULU9)
