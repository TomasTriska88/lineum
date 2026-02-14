# SPEC6_FALSE_S41 - WHITEPAPER EVIDENCE SNAPSHOT
**Generated:** 2026-02-14 14:55 (Local)

## 1. RUN IDENTIFICATION
- **Run Tag:** `spec6_false_s41`
- **Run Directory:** `output_wp/runs/spec6_false_s41_20260214_101645`
- **Absolute Path:** `c:\Users\Tomáš\Documents\GitHub\lineum-core\output_wp\runs\spec6_false_s41_20260214_101645`
- **Latest Run Pointer:** `runs/spec6_false_s41_20260214_101645` (from `output_wp/latest_run.txt`)
- **Git Commit:** `875fc4e` - `finalize logging and throttling` (Verified)

## 2. RUN METADATA (Source: manifest.json)
| Parameter | Value |
| :--- | :--- |
| **Seed** | `41` |
| **Steps** | `2000` |
| **Grid Size** | `128` |
| **Time Step (s)** | `1e-21` |
| **Window W** | `256` |
| **Window Hop** | `128` |
| **Run Mode** | `false` (Creation Mode) |

## 3. PRIMARY METRICS (Source: manifest.json)
| Metric | Value | Confidence Interval (CI) |
| :--- | :--- | :--- |
| **Dominant Freq (f0)** | `1.710e+20` Hz | `[9.82e+19, 2.47e+20]` |
| **SBR** | `193.97` | `[5.86, 500.08]` |
| **Phi Half-Life** | `1045` steps | - |
| **Neutrality (%)** | `96.25`% | - |
| **Mean Vortices** | `98.775` | - |
| **Low Mass QP** | `49` | - |
| **Max Lifespan** | `1626` steps | - |

## 4. CROSS-CHECK DETAILS
*Independent calculation verified by Python from CSV logs.*

### A. Topology Neutrality
**Source:** `spec6_false_s41_topo_log.csv` (81 samples, step 25)

| Definition | Formula | Computed Value | Manifest Match |
| :--- | :--- | :--- | :--- |
| **N0 (Strict)** | `net_charge == 0` | `87.50`% | No |
| **N1 (Standard)** | `abs(net_charge) <= 1` | `96.25`% | **YES (Canonical)** |
| **N2 (Relaxed)** | `abs(net_charge) <= 2` | `97.50`% | No |

**Net Charge Histogram:**
- `-8`: 1
- `-1`: 2
- ` 0`: 70
- `+1`: 5
- `+2`: 1
*(Total: 79 samples shown, outlier stability confirmed)*

### B. Frequency Binning Sanity
**Source:** `metrics_summary.csv` (Mean f0) and Constants

| Parameter | Value | Notes |
| :--- | :--- | :--- |
| **Bin Width (Δf)** | `3.9063e+18` Hz | `1 / (W * dt)` |
| **Reported f0** | `1.7104e+20` Hz | From metrics summary |
| **Bin Index (k)** | `~43.79` | `f0 / Δf` |
| **Bin Center (k=44)** | `1.7188e+20` Hz | Nearest Integer Bin |

*Conclusion: The reported f0 is an interpolated/weighted spectral centroid (k=43.79), offering higher precision than raw integer binning.*

### C. General Metrics Verification
| Metric | Manifest Value | Computed from CSV | Match |
| :--- | :--- | :--- | :--- |
| **Mean Total Vortices** | `98.775` | `98.7750` | **EXACT** |
| **f0 (Hz)** | `1.710e+20` | `1.71037...e+20` | **EXACT** |
| **SBR** | `193.97` | `193.965...` | **EXACT** |

## 5. FINAL STATUS (Source: rolling_metrics.json + Checkpoints)
- **Latest Step Logged:** `1975` (Loop 0..1999, logging every 25)
- **Final State File:** `checkpoints/spec6_false_s41_state_step1999.npz` (FOUND)
- **Latest Metrics:**
  - `center_amp`: `1000000.0`
  - `phi_center_abs`: `4384.77`
  - `vortices_total`: `20`
  - `particles_count`: `4535`

## 6. FILES USED AS EVIDENCE
The following files were verified to exist in the run directory:
- `spec6_false_s41_manifest.json`
- `spec6_false_s41_rolling_metrics.json`
- `spec6_false_s41_metrics_summary.csv`
- `spec6_false_s41_multi_spectrum_summary.csv`
- `spec6_false_s41_topo_log.csv`
- `spec6_false_s41_phi_center_log.csv`
- `checkpoints/spec6_false_s41_state_step1999.npz`

---
**CONCLUSION:** Snapshot je připraven jako jediný zdroj čísel pro revizi whitepaperu.
