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
