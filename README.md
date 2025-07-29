# Lineum – Emergent Quantum Field Model

Lineum is a functional model of an emergent quantum field where structured dynamics, interaction, and quasi-physical behavior arise spontaneously from simple, local update rules.

At its core, the system evolves a complex scalar field ψ and an auxiliary interaction field φ in discrete time. The update rule incorporates local activation, stochastic fluctuation, nonlinear feedback, dissipation, and diffusion—without any global control, integration, or externally imposed dynamics. Despite this simplicity, the model reliably produces emergent mass, spin, trajectory, resonance, and gravitation-like flow—fully from within.

```
ψ ← ψ + 𝛌̃ + ξ + φψ − δψ + ∇²ψ + ∇φ
φ ← φ + κ ⋅ (|ψ|² − φ) + κ ⋅ ∇²φ
κ ← κ(x, y)
```

**Symbol key:**

<!-- prettier-ignore-start -->
| Symbol    | Meaning                                                                 |
|-----------|-------------------------------------------------------------------------|
| **ψ**     | Complex scalar field – primary oscillating field                        |
| **φ**     | Real interaction field – accumulates memory and structure               |
| **κ**     | Tuning field – defines local sensitivity of φ to ψ                      |
| **𝛌̃**     | Nonlinear local activation – _linon_ excitation from |∇ψ| + |ψ|         |
| **ξ**     | Quantum-like noise – phase fluctuation                                  |
| **φψ**    | Feedback from φ – local modulation of ψ                                  |
| **δψ**    | Dissipation – local damping of ψ amplitude                               |
| **∇²ψ**   | Laplacian of ψ – spatial diffusion                                       |
| **∇φ**    | Gradient of φ – directional drift (emergent gravity)                     |
| **∇²φ**   | Laplacian of φ – spatial smoothing and memory propagation               |
<!-- prettier-ignore-end -->

Despite relying solely on local and minimal update rules, the system exhibits emergent order—producing structure, phase flow, interaction fields, and reproducible observables reminiscent of physical dynamics.

Lineum provides a framework for investigating how coherent behavior, conservation-like properties, and measurable field phenomena can arise in a system that starts from near-randomness and obeys no predefined laws.

---

## 🔬 What it does

- Evolves a discrete complex field over time
- Generates spatiotemporal structure from noise
- Logs and visualizes emergent field properties
- Produces full simulation reports, animations, and data exports

> Lineum poses a simple but far-reaching question:  
> _Can the essence of physics arise from almost nothing but locality and noise?_

---

## 📚 Documentation

See the [project wiki](https://github.com/TomasTriska88/lineum-core/wiki) for details.
for theoretical background, implementation notes, and observed structures.

---

## 🌐 Simulation Output

Sample outputs from a validated test run:  
🗂 `persistent/true/1/`

- [lineum_report.html](persistent/true/1/lineum_report.html) – full simulation summary
- [lineum_particles.gif](persistent/true/1/lineum_particles.gif) – particle emergence
- [lineum_spin.gif](persistent/true/1/lineum_spin.gif) – spin field dynamics
- [multi_spectrum_summary.csv](persistent/true/1/multi_spectrum_summary.csv) – frequency spectrum per probe
- [phi_curl_low_mass.csv](persistent/true/1/phi_curl_low_mass.csv) – collapse trace near φ = 0.25
- [spectrum_plot.png](persistent/true/1/spectrum_plot.png) – central frequency log
- [trajectories.csv](persistent/true/1/trajectories.csv) – quasiparticle paths
- [spin_aura_avg.png](persistent/true/1/spin_aura_avg.png) – average spin map

---

Lineum does not assume the laws of nature.  
It asks: _what if they are remembered into being?_

---

## 📚 How to Cite

If you use Lineum in your research, software, visualization, or theoretical work, please cite:

> Tomáš Tříska.  
> _Lineum – Model of Emergent Quantum Field_. (2025)  
> Conceptual collaboration: Lina (AI)  
> [https://github.com/TomasTriska88/lineum-core](https://github.com/TomasTriska88/lineum-core)

BibTeX format:

```bibtex
@misc{triska2025lineum,
  author       = {Tomáš Tříska},
  title        = {Lineum – Model of Emergent Quantum Field},
  year         = {2025},
  note         = {Conceptual collaboration: Lina (AI)},
  howpublished = {\url{https://github.com/TomasTriska88/lineum-core}}
}
```
