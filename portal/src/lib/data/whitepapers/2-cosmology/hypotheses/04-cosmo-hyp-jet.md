```markdown
**Title:** Hypothesis: Jet Emission from a Saturated φ-Trap
**Document ID:** 04-cosmo-hyp-jet
**Document Type:** Hypothesis
**Version:** 0.1.0
**Status:** Draft
**Date:** 2026-02-23

---
# Hypothesis: Jet Emission from a Saturated φ-Trap

## Author / Origin

inspired by AGN (Active Galactic Nuclei) jets, formulated within the Lineum project (2025)

---

## Hypothesis

If a φ-trap accumulates too many quasiparticles and φ grows beyond its usual limit, nonlinear saturation and a potential emission of energy, spin, or directional flow may occur. The ψ-flow could redirect itself in the form of a jet – similar to relativistic jets from black holes.

It is hypothesized that the emission will exhibit:

- a direction perpendicular to the φ-gradient (similar to an axis of rotation)
- a spin, dipole, or oscillation structure
- an impact on the surrounding ψ-field

---

## Testing Status

- ✅ Visualization prepared (`steps = 1000`, `TEST_EXHALE_MODE = False`)
- 📉 No directional jet or asymmetric flow was observed
- 📈 φ in the center of the field reached a value of ≈ 50 (see `phi_center_log.csv`)
- 🌀 Spin remained vortex-like, with no signs of axial concentration (`lineum_spin.gif`)
- 🔄 Hypothesis **not yet confirmed** (0 % of runs)

---

### New Test (`LOW_NOISE_MODE = False`, `TEST_EXHALE_MODE = False`)

In a newly conducted run, the φ value in the center of the field reached ≈ 2983.99, significantly higher than in previous attempts. Nevertheless:

- no jet or asymmetric ψ-directionality was recorded
- φ subsequently fluctuated but did not decrease or lead to energy release
- spin remained vortex-like, with no change in axial structure

📌 The jet hypothesis therefore **remains unproven**.  
An increase in φ alone appears **insufficient for overload** – a jet does not occur without external perturbation or a more complex structure. However, the results suggest that φ-traps can grow to extreme values without destabilization.

Further testing is recommended:

- controlled fall of multiple particles simultaneously
- or the construction of a 'star' from linons

---

## Calculation Methodology

### Simulation Parameters:

```python
TEST_EXHALE_MODE = False
LOW_NOISE_MODE = False
steps = 1000
linon_base = 0.01
linon_scaling = 0.03
disipation_rate = 0.001
```

In the tested run, a total of 315 quasiparticles (linons) were gradually inserted into the center of the grid. The `linon_scaling` parameter influences the energy input into φ, and thus the saturation rate of the φ-trap.

Calculations were performed on a regular 128×128 point grid, with fixed boundaries (Dirichlet conditions).

Field updates occur iteratively:

- φ-grid:
  φₜ₊₁ = φₜ + ∇²φₜ - disipation_rate \* φₜ + linon_input
  where `∇²φ` is the Laplacian operator (smoothing) and `linon_input` adds quasiparticles

- ψ-grid:
  ψₜ₊₁ = ψₜ + i·∇²ψₜ - i·φₜ·ψₜ

- Overload can be tested using:
  Overload ≈ |∇φ × ∇ψ|
  This expression detects shear stress between changes in φ and ψ – a potential trigger for a jet

---

## Outputs:

**phi_center_log.csv** – CSV file with logarithmic values of φ in the center of the field over time (1 column, 1000 rows). Used to detect sudden growths or saturation of the φ-trap.

**frames_curl.npy** – 3D array of shape `[steps, height, width]`, where each plane contains the calculation of ∇×ψ (curl) for a given time step. Identifies rotational flow.

**frames_amp.npy** – 3D array of shape `[steps, height, width]`, containing the amplitudes of ψ at each step. Allows detection of wave interferences and oscillations.

**lineum_spin.gif** – Animation of ∇φ (phase gradient), visually displaying flow direction, vortices, and axial structures. Suitable for monitoring deformations and jets.

**lineum_report.html** – Generated report with embedded visualizations. The "Jet emission – test mode" section contains all the aforementioned outputs clearly presented over time.

---

## Visualization Outputs

### 1. `lineum_spin.gif`

Animation of the phase gradient ∇φ over time.  
In the current run (`LOW_NOISE_MODE = False`, `steps = 1000`), vortex structures appear without signs of directional axial concentration. Neither a jet nor local destabilization was visually observed.

📌 The largest gradients move within the central vortex region, but their orientation is irregular and changes over time.

---

### 2. `phi_center_log.csv`

The graph of the logarithmic φ value in the center of the field shows a sharp increase up to **2983.99**. Nevertheless, no sudden drop or emission occurred, indicating the stability of the φ-trap even at extreme values.

It is recommended to monitor not only maximum values but also the first derivative of φ(t) as a potential jet trigger.

---

### 3. `frames_curl.npy` and `frames_amp.npy`

Visual decoding of these fields (e.g., as sequential frames or GIFs) shows:

- **`curl`**: presence of vortices, but no prominent current axes
- **`amp`**: amplitude amplification in the trap region, without directional discharge

The analysis does not indicate the formation of a jet stream.

---

## Recommended Further Tests

- Test the fall of a structured bound entity (e.g., a compact linon star) into the φ-trap – instead of individual linons
- Introduce a rotating vector structure as input – because real black holes rotate
- Introduce cumulative monitoring of `φ` + `∇φ × ∇ψ` over time as a "critical point" condition
- Introduce the calculation of `∇φ × ∇ψ` as an overload indicator
- Increase `linon_scaling` and the number of quasiparticles
- Limit dissipation and shorten run time
- Test with 2×2 φ-trap structures in the grid
- Introduce external perturbation (artificial input of linons into the φ-trap)

---

## References

- `lineum_report.html` – section "Jet emission – test mode"
- `phi_center_log.csv`, `frames_curl.npy`, `frames_amp.npy`
- prepared as a hypothesis in `09-hypotheses.md`
```