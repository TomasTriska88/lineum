# Whitepaper Contract Suite Report

**Generated:** 2026-02-14T19:52:10.125555+00:00
**Contract:** `lineum-core-1.0.9-core`

## Summary

- **PASS:** 0
- **FAIL:** 1
- **SKIP:** 0
- **Canonical Matches:** 1

## Runs

### `spec6_false_s41_20260214_101645`
- **Status:** FAIL
- **Failures:**
  - `baseline.invariants.dim`: Identity mismatch (Expected: `2D`, Actual: `None`)
  - `baseline.invariants.bcs`: Identity mismatch (Expected: `periodic`, Actual: `None`)
  - `baseline.invariants.precision`: Identity mismatch (Expected: `float64`, Actual: `None`)
  - `canonical.anchor.f0_mean_hz`: ordered 1.7103794642857145e+20 < min 2.3e+20 (Expected: `{'min': 2.3e+20, 'max': 2.5e+20, 'paper_ref': '§4.6'}`, Actual: `1.7103794642857145e+20`)
  - `canonical.anchor.topology_neutrality_n1`: |96.25 - 100.0| = 3.75 > tol 0.1 (Expected: `{'target': 100.0, 'abs_tol': 0.1, 'paper_ref': '§4.4'}`, Actual: `96.25`)
  - `canonical.anchor.mean_vortices`: ordered 98.775 < min 200 (Expected: `{'min': 200, 'max': 300, 'paper_ref': '§4.4'}`, Actual: `98.775`)
  - `canonical.anchor.phi_half_life_steps`: ordered 1045.0 < min 1500 (Expected: `{'min': 1500, 'max': 2500, 'paper_ref': '§4.6'}`, Actual: `1045`)

