# Lineum Appendix – Equation History

**Version:** 1.0  
**Date:** 2025-08-10  
**Related Appendices:** _(none yet)_

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

### 🔹 Version 1 – Purely oscillating field

```text
ψ ← ψ + 𝛌̃ + ξ + φψ − δψ + ∇²ψ
```

The first version contained only the ψ field. It generated linons, spin, and vortices, but did not allow accumulation or emergent attraction. The φ field was not yet dynamic.

- ✅ Generated **linons** and flows
- ❌ No accumulation or emergent gravitational behavior
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

### 🔹 Version 3 – Emergent gravity through ∇φ

> **Note:** This change affects the ψ field equation, unlike Version 2 which introduced the φ field equation.  
> It represents the first direct coupling of ψ to φ through its gradient.

```text
ψ ← ψ + 𝛌̃ + ξ + φψ − δψ + ∇²ψ + ∇φ
```

By adding the gradient of φ, flow without force emerges – **linons** move into regions where φ increases.

- ✅ Gravitational behavior without explicit force
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
In connection with DTH tests, κ appears to also determine **visibility** – in areas with low κ, no particles or vortices form.

## 4. Discussion

This progression shows a shift from a minimalistic ψ–φ interaction model to a more versatile three-field system capable of sustaining richer emergent structures. Each modification was driven by simulation feedback and aimed at increasing stability, scalability, and interpretability.
