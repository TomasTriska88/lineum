**Title:** Lineum Appendix – Equation History
**Document ID:** core-equation-history
**Document Type:** Core
**Version:** 1.1.0
**Status:** Draft
**Date:** 2025-11-14

**Relates to:** `lineum-core.md` §3  
**Equation versions:** V1–V4 (canonical: V4)  

---
# Lineum Appendix – Equation History

---

## 1. Title & Scope

Chronological record of the main Lineum equation’s development, documenting all major revisions from the initial formulation to the current form presented in the core paper. This appendix preserves each historical variant, the reasons for changes, and observed impacts on simulation outcomes.

---

## 2. Motivation

The equation in the core paper represents the current, most refined formulation of the Lineum model. However, its development involved multiple iterations, parameter adjustments, and structural changes. Recording this history allows:

- Reproducibility of past results,
- Understanding of why certain terms were added, modified, or removed,
- Providing context for future experiments and related hypotheses.

---

## 3. Main Content

> **Note:** The latest equation form is **Version 4**. Its canonical expression is given in the core paper: see [Equation section](./lineum-core.md#3-equation).
> In the canonical form, **κ** is a **static spatial map** (no time evolution) that _modulates_ parameters locally (e.g., α_eff = κ·α, β_eff = κ·β) rather than directly replacing **α** or **β** in the φ-update.

**Terminology.** Throughout this appendix, we use **linon** to denote a stable, localized |ψ|² excitation (i.e., the quasi-particle of the Lineum model).

In the experimental context of the broader project, **DTH** denotes the **Dimensional Transparency Hypothesis** – a working hypothesis (not an established mechanism) about how changes in κ might affect the “visibility” of simulated structures when interpreted in terms of a prospective detector setup.

> **Interpretation note:** Terms like “gravity” or “gravitational” in this appendix describe **gravity-like patterns in the simulation**, not a confirmed physical gravitational force in nature.

### 🔹 Version 1 – Purely oscillating field

```text
ψ ← ψ + 𝛌̃ + ξ + φψ − δψ + ∇²ψ
```

The first version contained only the ψ field. It generated linons, spin, and vortices, but did not allow accumulation or emergent attraction. The φ field was not yet dynamic.

- ✅ Generated **linons** and flows
- ❌ No accumulation or emergent gravity-like behavior (in the simulation)
- ❌ φ was static, without memory

---

### 🔹 Version 2 – Introduction of the accumulation field φ

```text
φ ← φ + (|ψ|² − φ) + ∇²φ
```

Introduced in response to the question “what causes attraction?”.  
The φ field began reacting to the density |ψ|² and creating stable maxima.

- ✅ φ-traps appeared for the first time
- ✅ **Linons** started to linger in them spontaneously
- ⚠️ ψ flow still did not distinguish the direction toward the gradient of φ

---

### 🔹 Version 3 – Emergent gravity-like behavior through ∇φ

> **Note:** This change affects the ψ field equation, unlike Version 2 which introduced the φ field equation.  
> It represents the first direct coupling of ψ to φ through its gradient.

```text
ψ ← ψ + 𝛌̃ + ξ + φψ − δψ + ∇²ψ + ∇φ
```

By adding the gradient of φ, a gravity-like flow pattern emerges in the simulation – **linons** move into regions where φ increases.

- ✅ Gravity-like behavior (in the model) without an explicit force term
- ✅ Formation of φ-centers, attraction, accumulation
- ✅ The overall model has memory, interaction, and trajectory

---

### 🔹 Version 4 – Introduction of the tuning field κ

```text
φ ← φ + κ (|ψ|² − φ) + κ ∇²φ
```

> **Post-hoc note (canonical alignment):** In the core paper’s **Equation section** ([link](./lineum-core.md#3-equation)), **κ** appears as a **static spatial map** with `κ ← κ(x, y)`, and the φ-update keeps  
> `φ ← φ + α (|ψ|² − φ) + β ∇²φ`.  
> The multiplicative κ shown above is retained here as a **historical snapshot** of the development stage.

By introducing the tuning field κ, the system’s response can be controlled locally – where the field “reacts” and where it is “deaf”.  
In connection with the current Dimensional Transparency Hypothesis (DTH) test setup, κ appears to influence **visibility** in the simulation – in low-κ regions we typically do not observe particle or vortex formation. This is an empirical observation of the model, not a confirmed statement about any physical detector.

---

### 🔹 The Continuous PDE Limit (Symbolic Form)

> **Note:** This is not a new chronological version, but the **theoretical continuous limit** of the canonical discrete update rule (V4).

```text
∂ₜψ = ∇²ψ + φψ + ∇φ
∂ₜφ = α(|ψ|² - φ) + β∇²φ
```

While Lineum is fundamentally a discrete computational model (cellular automaton), its dynamics analogize to continuous physical fields. When stripped of discrete step mechanics, artificial damping, noise, and the spatial performance mask ($\kappa$), the universe's core engine reduces to this elegant PDE pair.
This continuous formulation serves as the **canonical emblem** of the Lineum project—representing the pure mathematical concept of wave diffusion, memory interaction, and emergent gravitational drift, unburdened by algorithmic implementation details.

#### Philosophical Parallel: The Schrödinger Equation

For physicists, the structural similarity to the **Schrödinger equation** for a free particle ($i \hbar \partial_t \psi = -\frac{\hbar^2}{2m} \nabla^2 \psi$) is immediately apparent. Both equations describe how a wave function ($\psi$) evolves in time ($\partial_t$) based on its spatial curvature ($\nabla^2$). However, Lineum diverges in two critical, foundational ways:

1. **The Absence of the Imaginary Unit ($i$):**
   Schrödinger relies on complex numbers to represent probability amplitudes, creating the mystique of quantum mechanics. Lineum's PDE is entirely real-valued. It acts as a deterministic reaction-diffusion system.
2. **Deterministic Stability via Memory ($\varphi$):**
   A purely real continuous wave without $i$ would typically just dissipate (like heat). However, instead of relying on complex probabilities to maintain stable states, Lineum introduces the persistent memory/gravity field ($\varphi$). The terms $\varphi\psi + \nabla\varphi$ act as a feedback loop—the dissipating wave is constantly "pulled together" by the gravity of the very memory it creates, allowing stable gliders and particles to emerge purely from real-field deterministic interactions.

This presents a paradigm shift: Instead of using abstract quantum probability to explain stable matter, Lineum achieves stability by endowing the fabric of space itself with memory. As Einstein famously argued against quantum randomness, *"God does not play dice."* Lineum offers a glimpse into a universe where stability and complexity emerge without randomness, built purely on cause, memory, and effect.

#### Philosophical Parallel: The Amplituhedron and Emergent Spacetime

Recent advances in theoretical physics, such as the formulation of the **Amplituhedron** for calculating $n$-particle scattering amplitudes, suggest that standard spacetime, locality, and unitarity might not be fundamental features of the universe, but rather emergent illusions. 

Lineum explores the exact opposite philosophical extreme: where the Amplituhedron abandons locality and operates in a top-down, non-local geometric space, Lineum strictly enforces **primitive locality and a metric-free discrete grid**. By stripping away global constants, the model attempts a pure bottom-up emergence.

> **[OBS] Hypothesis: Asymptotic limits and the "Half-Collinear" Regime**
> In continuous quantum field theories, specific kinetic scenarios—such as high-energy particles moving in parallel (the *half-collinear regime*)—often lead to divergent $n$-particle amplitudes requiring complex corrective renormalizations. We hypothesize that in the Lineum system, such overlapping extreme states do not produce mathematical infinities. Instead, when multiple linons overlap at extreme directional energies, their stabilizing phase topologies mutually interfere. This leads to a native wave-breaking event or non-linear coagulation within the $\phi$ memory field, resolving the singularity organically. 
> *Verification note:* This remains a purely observational hypothesis and a necessity for strict future verification. It is not yet a contract-validated behavior of the V4 mechanism.

## 4. Discussion

This progression shows a shift from a minimalistic ψ–φ interaction model to a more versatile three-field system capable of sustaining richer emergent structures **within the simulation**. Each modification was driven by simulation feedback and aimed at increasing stability, scalability, and interpretability of the model, not by fitting any specific physical constant or established gravitational law.

## 5. Versioning & Changelog

**Policy.** Semantic Versioning applies to this **document**; equation variants are labeled V1…V4 separately.

- **MAJOR**: structural changes that alter interpretation of historical entries.
- **MINOR**: new archival variants, added rationale, artifacts.
- **PATCH**: wording/formatting fixes.

**1.1.0 — 2025-11-14**

- Adds an explicit interpretation note that “gravity” / “gravitational” refers to gravity-like patterns **in the simulation**, not a physical gravitational force.
- Introduces the Dimensional Transparency Hypothesis (DTH) terminology and clarifies κ–visibility as an empirical property of the model, not a statement about any real detector.

**1.0.0 — 2025-08-10 (initial)**

- Establishes the V1→V4 chronology aligned with the canonical Eq-4 in the core.
- Notes that κ is a static spatial map in the canonical core; earlier multiplicative κ forms are retained here as historical snapshots.
