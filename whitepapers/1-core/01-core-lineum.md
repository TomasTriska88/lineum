**Document ID:** lineum-core  
**Document Type:** Core
**Version:** 1.0.18-core
**Status:** Draft  
**Equation:** Eq-7 (Unitary Wave; κ static)  
**Scope:** 2D, periodic BCs
**Date:** 2026-02-15

**DOI:** 10.5281/zenodo.16934359  
**How to cite:** Tomáš Tříska. _Lineum Core (v1.0.18-core)._ 2026. DOI: 10.5281/zenodo.16934359.
_This manuscript corresponds to Git tag **v1.0.18-core** and the evidence bundle in `output/` (commit-stamped in each HTML)._

**Contract evidence (core v1.0.18-core).** All numeric claims in this manuscript that are presented as *validated* are limited
to what is asserted by the contract suite `lineum-core-1.0.18-core` (contract_version `1.1.5`), including the embedded
canonical run `spec6_false_s41_20260222_152015` and its declared fingerprints.

> **Status tags (v1.0.18-core).** To make the manuscript audit-proof, we label claim strength explicitly:
>
> - **[VALIDATED]** = enforced by the referenced contract suite (numeric acceptance band or exact match) **and** traceable to a contract key.
> - **[OBS]** = reproducible observation supported by artifacts (CSV/PNG/GIF/HTML), but **not** currently enforced by contract acceptance.
> - **[DISPLAY]** = derived, illustrative unit conversions from validated anchors (e.g., SI values derived from `f0_mean_hz`), **not** acceptance criteria.
> - **[OOS]** = explicitly out of scope for core v1 (documented only as future work / extension track).
> - **[TEST]** = falsification/verification procedure or expected outcome to be checked by running new artifacts; **not** a reported result unless explicitly pinned + contract-checked.
>
> The authoritative mapping “claim → contract key → artifact pointer” is defined in **Appendix G (Claim–Contract Map)**.


> **Canonical Scope (v1.0.x)**  
> **Equation:** Eq-7 (κ static) • **Dim.:** 2D • **BCs:** periodic • **Grid:** 128×128  
> **Δt:** 1.0×10⁻²¹ s • **Seed:** 41 • **RUN_TAG:** spec6_false_s41  
> **κ-mode:** constant • **Noise:** zero-mean, **σξ = 5.0×10⁻³** (canonical)  
> **Operators:** ∇ (central), ∇² (5-point von Neumann)  
> **Out of scope:** 3D, time-varying κ, zeta/RNB correlations, Return Echo, **quantitative Vortex–Particle coupling claims/taxonomy**, and other interpretive add-ons. These are intentionally excluded from the core and deferred to **future work**; they are not part of this submission. **Structural Closure is in scope for v1.0.x** and is treated as an operational consequence of the φ center-trace half-life metric (see §5.4).

> **Noise note (core v1).** “canonical low” means “numerically small” (σξ = 5.0×10⁻³ in the canonical run). It does **not**
> imply a separate “low_noise_mode” override; in the locked audit profile `low_noise_mode=false` (base noise is used).

>
> **Contract alignment note (v1.0.18-core).** The contract suite *validates* only the declared metric subset and artifact presence.
> Phenomena such as **“Spin Aura”** may be discussed **only as observational/interpretive**, unless and until they are explicitly
> added to the contract suite as acceptance criteria.
>
> **Structural Closure (core v1) — contract-derived proxy.** In v1.0.x, we treat “Structural Closure” as a *named, operational*
> consequence of the **contract-validated** φ center-trace half-life anchor (`phi_half_life_steps`) together with the required
> presence of the φ trace artifacts (`*_phi_center_log.csv`, `*_phi_center_plot.png`).
> This means: the contract does not validate any morphological “shape” claim of remnants; it validates the **timescale anchor**
> we use as the closure proxy. Any additional statements about remnant geometry, spatial localization maps, or trajectory-level
> bias are **not contract-validated** unless explicitly added later.

# 1. Abstract

Lineum is a minimal discrete coupled-field model defined by a local update rule on a 2D periodic grid. It evolves a complex field ψ coupled to a real interaction/memory field φ and a static tuning map κ. The model does not assume any *physical* constants (e.g., c, ħ, G), spacetime metric, or continuum symmetries; instead it uses dimensionless control parameters (α, β, δ) within the numerical scheme. In the **canonical evidence run** pinned in §4.6, the system produces stable, quantifiable behaviors under a fixed numerical scheme. Where we use physics terms (e.g., “quasi-particle”, “spin”), they are strictly analogical labels for operationally defined measurements, not claims of equivalence to any continuum field theory.


The system evolves according to a coupled three-field update rule (see [Equation (1)](#eq1) (Version 4) in Section 3), which governs the primary field ψ, the interaction field φ, and the spatial tuning map κ.

**Terminology.** We use **linon** to denote a **stable, localized excitation** of |ψ|² (a quasi-particle analogue emergent from the Lineum rule). It is **not** a fundamental particle. On first mention we may write “linon (localized excitation)”; thereafter we use **linon**.

**Pronunciation (model name).** _Lineum_ = Czech **/ˈlɪ.nɛ.um/** (short **i**, three syllables: “**LIH-neh-oom**”, stress on the first).  
For readers in English: **/ˈlɪniəm/** (UK/US ≈ “**LIH-nee-um**”).  

**Pronunciation (phenomenon).** _linon_ = Czech **/ˈlɪnon/** (short **i**, stress on the first syllable).  
For readers in English: **/ˈlɪnɒn/** (UK ≈ “LIH-non”) or **/ˈlɪnɑːn/** (US ≈ “LIH-nahn”).  
_Not_ “LAI-non”.


### Plain-language summary (non-technical)

If you strip the math down to the basics, Lineum is “just” a grid of numbers that gets updated locally, step by step:

- **ψ is the fast, wavy carrier** (a complex oscillation on the grid).
- **φ is the slow “memory/envelope”** that reacts to where ψ has high intensity and then diffuses.
- **κ is a static sensitivity map** (in core v1 it does not evolve).

What we **actually show (and pin to the evidence HTML/CSV)** in core v1 is not “new physics”, but reproducible, auditable *behavior* under a pinned numerical scheme:


- **[OBS]** localized excitations (“linon candidates”) visible in amplitude/trajectory artifacts;  
  **[VALIDATED]** anchors derived from these detectors include **`low_mass_qp_count` (exact)** and **`max_lifespan_steps` (threshold)**.
- **[VALIDATED]** a **dominant tone** \(f_0\) (`f0_mean_hz`).  
  _Note:_ windowed 95% CIs shown in HTML quantify **within-run** variability and are **informational** (not contract-validated).
- **[VALIDATED]** a **strong spectral dominance** (SBR) of that tone (`sbr_mean`; ±2-bin guard).
- **[VALIDATED]** **topological neutrality** within tolerance (`N1`) and **mean vortex count** (computed over logged frames as declared in the manifest; `topo_log_stride`).
- **[VALIDATED]** a measurable **φ center-trace half-life** (`phi_half_life_steps`) and required φ-trace artifacts.

> **Contract scope note (v1.0.18-core).** Validation in core v1 is defined by the contract suite referenced at the top of this manuscript.
> It validates only a declared subset of metrics (e.g., `f0_mean_hz`, `sbr_mean`, topology neutrality `N1`, mean vortex count,
> `phi_half_life_steps`, `max_lifespan_steps`, `low_mass_qp_count`) and the required artifact set.
> Any other effect (e.g., guided motion statistics, spin-aura amplitude thresholds, morphology of φ remnants) must be labeled
> **not contract-validated** unless and until it is added as an explicit acceptance criterion.


What we **do not claim** in core v1: Standard-Model identification, gravity/GR mapping, thermodynamics, or any phenomenon requiring time-varying κ. Those belong to separate experimental/extension tracks.

### Physics translation (informal; analogy only)

Readers with a conventional physics background can think of a linon as a **stable localized oscillatory mode on a lattice** in a **nonlinear, dissipative, coupled-field system**. In spirit, it is closer to **a breather/soliton-like localized state** (in discrete nonlinear media) than to a fundamental particle.

Informally:

- the **φ-update** looks like a **reaction–diffusion / relaxation** channel driven by \(|\psi|^2\),
- the **ψ-update** combines **damping**, **local coupling** (φ·ψ), **diffusion** (∇²ψ), and a drift term **+∇φ** that behaves *like advection by a potential gradient*.

This is an **interpretive translation** to familiar language (e.g., “discrete nonlinear waves”, “reaction–diffusion”, “CGLE-like behavior”), not a claim of equivalence to any specific continuum field theory.

In the **canonical evidence run** (and additionally in the **provided per-seed evidence bundles**, without cross-seed aggregation in this draft):
– **[OBS]** stable localized excitations (**linons**) visible in amplitude/trajectory artifacts, with contract-anchored detector outputs;  
– **[VALIDATED]** dominant tone \(f_0\) (`f0_mean_hz`),  
– **[VALIDATED]** spectral strength (**SBR**, `sbr_mean`, ±2-bin guard),  
– **[VALIDATED]** **topological neutrality** (`N1`) and mean vortex count (logged frames),  
– **[VALIDATED]** **center-trace φ half-life** (`phi_half_life_steps`).

All listed items are directly reported in the HTML evidence (Quasiparticle Properties, Spectral metrics, Topology metrics, “Spin aura — averaged curl map”, and φ center trace). Claims requiring κ-dynamics, thermodynamics, or SM identification are out of scope for the v1 core.

Within the v1 core evidence bundle, **contract-validated** items are limited to:  
(i) the canonical run’s validated numeric anchors (e.g., `f0_mean_hz`, `sbr_mean`, topology neutrality `N1`, mean vortex count, `phi_half_life_steps`, `max_lifespan_steps`, `low_mass_qp_count`) and  
(ii) the presence of required artifacts (HTML/CSV logs).  
Other effects (e.g., “spin aura”, “Structural Closure”, “guided motion” statistics beyond the equation-level intuition) may be described as **observations**, but must be explicitly labeled **not contract-validated**.

For the canonical parameter choice (Δt fixed and SI constants applied post hoc), the dominant oscillation can be expressed in familiar physical units for **scale illustration only**. For example, when written in SI units (refined snapshot; RUN_TAG `spec6_false_s41`, commit `875fc4e`):
these values are not used as acceptance thresholds or constraints anywhere in the core validation.

- **[DISPLAY]** (unit conversions from `f0_mean_hz`; not acceptance criteria):
- dominant oscillation frequency (contract anchor) ≈ **1.857×10²⁰ Hz**,
- linon energy (display-only) ≈ **1.23×10⁻¹³ J** ≈ **767.90 keV**,
- wavelength (display-only) ≈ **1.61×10⁻¹² m** (0.00161 nm),
- effective mass (display-only) ≈ **1.50×** of the electron mass (**m/mₑ ≈ 1.5027**).

These SI-anchored values are **unit conversions of the canonical tone f₀**, not additional constraints on the model or evidence that Lineum directly realizes any specific physical scale.

> **Plain-language warning.** This is the same kind of conversion you’d do if you take a frequency and compute “what energy would a photon of that frequency have”. It gives a **sense of scale**, but it does **not** turn the linon into “a photon/electron/etc.” and it does **not** assert a real-world rest mass.


> **Interpretation note (v1).** The “effective mass” value is a **unit-conversion from the dominant frequency** \(f_0\) via \(m = h f_0 / c^2\). It is provided **only** as an intuition aid for scale (refined snapshot: RUN_TAG `spec6_false_s41`, commit `875fc4e`), **not** as a claim of an intrinsic rest mass.

> **Reports alignment (v1).** In the refined snapshot, the SI-anchored values (E, λ, display-only m/mₑ) are computed directly from the reported \(f_0\) (manifest/CSV) using fixed SI constants. This remains a **scale indicator**, not a rest-mass claim.

> **Non-identification (v1).** A **linon** is a _stable, localized excitation_ in the Lineum field, **not** a Standard-Model particle. The numerical anchors in the Abstract (f₀, E, λ, and the display-only mass ratio m/mₑ) are provided **to indicate scale only**. They must **not** be read as an identification with electrons, neutrinos, or any SM species. See “Terminology” (linon is not a fundamental particle) and the **Interpretation note (v1)** on display-only mass.
 
> **Topology logging note (v1).** Topology metrics (neutrality and mean vortex counts) are computed from `*_topo_log.csv`,
> which is **decimated** (logged every `logging.topo_log_stride` steps as declared in the run manifest).
> In the canonical run `spec6_false_s41`, `topo_log_stride = 25`, hence topology metrics are computed over **logged frames**
> (N=81 frames; steps 0..2000). This decimation is deterministic, declared in the manifest, and validated by the contract suite.


All reported phenomena arise from local operations on a discrete grid starting from a defined class of small random initializations (see §4.1) without per-run manual tuning. No predefined force law is included. Linons tend to drift along +∇φ (toward increasing φ); we describe this as environmental guidance rather than any gravitational claim.


The system is open for independent verification: the canonical run is fully pinned by manifest, artifacts, and the contract suite, and replication is evaluated by the contract-aligned acceptance bands in §4.3.1.

**Out-of-scope clarifier (v1 core).** We **do not** claim: (i) predictability of “random” outcomes or a deterministic substrate for stochastic processes; (ii) any κ-dynamics phenomena (e.g., “Dimensional Transparency”); (iii) thermodynamic quantities (T, S) or fluctuation–dissipation calibration; (iv) identification with Standard-Model particles; (v) gravitational analogies; or (vi) ontological mappings of dark matter, consciousness, macro-soul networks, or theological (i.e., Trinity / P2P Universe) hypotheses. These topics are deferred to the experimental/extension track and are strictly **not** part of the v1 core evidence.

**Graphical abstract.**

<p align="center">
  <img src="../source/icon.png" alt="Lineum symbol" width="320">
</p>

<sub>Note: this mark is a visual mnemonic only; it carries no physical claim and is not used in any metric.</sub>

**Icon legend (mnemonic only — no physical claim).**

- **Fish (upper) → κ (tuning / sensitivity).**  
  _Why:_ the “eye” dot suggests a **sensor**, the body an **oriented agent** responding to local cues; κ controls local **susceptibility** and tuning (κ·α, κ·β), i.e., how the medium responds to gradients.
- **Spiral (lower-left) → ψ (oscillation / flow).**  
  _Why:_ a spiral visually encodes **periodicity and phase circulation**; ψ is the time-like **carrier** with canonical tone **f₀**, from which we derive SI conversions (E, λ, display-only m/mₑ).
- **Leaf (right) → φ (memory / envelope).**  
  _Why:_ the broad lamina reads as an **envelope**, while venation evokes a stored **pattern/context**; φ is the **memory** field used in nearby/field means and the center-trace half-life metric.
- **Outer loop → circulation / interplay.**  
  _Why:_ a closed interplay **κ → (α_eff,β_eff) → φ ↔ ψ** as a mnemonic of coupling/modulation; **no law or metric is implied**.
- **Design note.** Uniform line weight → no hierarchy; shapes are **not** used as data encodings anywhere in the paper.

_Directional mnemonic (mnemonic only):_ κ (tuning) modulates the local response parameters, ψ drives φ via |ψ|², and φ feeds back into ψ via the canonical coupling terms (φψ and +∇φ) as defined in Eq. (1). Do not infer causality from the icon beyond the explicit update rule.

> **Three-field flow.** The mark depicts the triad **ψ–φ–κ** in balance: ψ (oscillation / flow), φ (memory / resonance), κ (tuning / sensitivity). It is a visual mnemonic only; the **canonical Equation (1)** defines the model.

> **Core thesis (v1; claim-strength explicit).** We demonstrate a _reproducible, parameter-light_ emergence of a stable localized excitation (“linon”) with:
> - **[VALIDATED]** a dominant tone \(f_0\) (`f0_mean_hz`) and strong spectral dominance (SBR, `sbr_mean`);
> - **[VALIDATED]** topology neutrality (`N1`) and mean vortex count computed over logged frames;
> - **[VALIDATED]** a φ center-trace half-life timescale (`phi_half_life_steps`) + required φ-trace artifacts (closure proxy);
> - **[DISPLAY]** SI-anchored conversions (E, λ, display-only \(m/m_e\)) computed from \(f_0\) for scale illustration only;
> - **[OBS]** within-run uncertainty reporting (windowed 95% CIs shown in HTML) as an informational stability view, not a contract acceptance.
>
> The contribution is methodological: numeric anchors + guardrails that turn an emergent phenomenon into an **auditable, falsifiable** object others can probe and extend.

> **Falsifiable checks (v1; [TEST]).**  
> The following are **verification procedures** (not results) that should produce a **contract PASS** when regenerated and pinned.
>
> **(C1) Window resolution [TEST]:** Re-run with `W = 512` (keeping `Δt = 1.0e−21 s`). Expect the dominant tone to remain near the same FFT region and the contract suite to PASS; in particular `f0_mean_hz` stays within the §4.3.1 band **[1.84e20, 1.87e20] Hz** and `sbr_mean ≥ 3000`.  
> **(C2) Temporal refinement (Δf preserved) [TEST]:** Halve the time label and double the window (`Δt → Δt/2`, `W → 2W`) so `Δf = 1/(W·Δt)` stays constant. Expect contract PASS with the same anchors/bands (no requirement of exact bin-centering; centroid/interpolated \(f_0\) is valid).  
> **(C3) Grid size [TEST]:** Re-run on `256×256` with identical parameters. Expect contract PASS with `f0_mean_hz` within **[1.84e20, 1.87e20] Hz**, `sbr_mean ≥ 3000`, and topology/φ anchors within their §4.3.1 bands.

# 2. Motivation

Many approaches in theoretical physics rely on continuous equations embedded in a predefined spacetime geometry, with global constants and symmetries fixed a priori. Such frameworks limit the exploration of systems where both the geometry and the interaction rules could emerge from purely local processes.

Lineum is designed as a minimal model to investigate whether complex, stable, and potentially physics-analogous structures can arise from:
– simple, local update rules,
– no predefined global metric or constants,
– and interactions mediated by emergent fields.

The key motivation is to test if macroscopic phenomena, such as particle-like excitations, field-mediated interactions, and stable wave patterns, can originate without embedding them explicitly into the governing equations.

By isolating and quantifying these emergent behaviors, Lineum offers a controllable environment to evaluate which observed effects might have analogues in known physics, and which are unique to discrete, metric-free systems.

### 2.1 Theoretical Context: Locality vs. Global Geometry

Current theoretical frameworks, most notably the **Amplituhedron** used for calculating $n$-particle scattering amplitudes, attempt to bypass the complexities of physical spacetime by computing interactions from within abstract global geometries, effectively treating locality as an emergent artifact. Lineum tests the polar opposite approach: building a strictly local, dimensionless discrete grid to verify if complex physical laws can instead emerge "bottom-up".

> **[OBS] Hypothesis: Asymptotic limits and the Half-Collinear Regime**
> A key hypothesis under investigation involves complex quasi-particle interactions. For instance, in the **half-collinear regime** where highly energetic particles move in almost parallel trajectories, continuous amplitude calculations traditionally face mathematical divergences requiring external renormalization. We hypothesize that in a strictly discrete formulation like Lineum, these asymptotic singularities simply cannot form. Instead, structurally overlapping high-energy linons will mutually disrupt their phase topologies, resulting in "wave-breaking" and immediate energy distribution back into the scalar $\phi$ field. 
> *Verification note:* This remains an observational hypothesis requiring explicit verification through targeted collision runs and is **not** a contract-validated behavior in the canonical v1 core.

# 3. Equation

The evolution of the system is defined on a discrete 2D grid by three coupled update rules for:
– the primary complex scalar field ψ,
– the interaction field φ,
– and the (static) tuning field κ (spatial map).

The canonical form is:

**Equation (1) — Canonical Lineum update (Version 4)** <a id="eq1"></a>

> **Euler-step convention (v1).** Eq. (1) is written in “per-step increment” form with the internal scheme step absorbed
> into the implementation (see `invariants.dt` note in §3.1). Replication is validated by contract metrics, not by algebraic
> normalization of an explicit Δt factor in the paper equation.

<!-- prettier-ignore-start -->
| Equation | Description |
| --- | --- |
| **ψ ← ψ + 𝛌̃ + ξ + φψ − δψ + ∇²ψ + ∇φ** | primary field evolution |
| **φ ← φ + α_eff (&#124;ψ&#124;² − φ) + β_eff ∇²φ** | interaction field response |
| **κ ← κ(x, y)** | spatial tuning map |
<!-- prettier-ignore-end -->

> _For the full development history of this equation, see_ [Appendix A: Equation History](lineum-core-equation-history.md).

**Legend (symbols & operators)**

<!-- prettier-ignore-start -->
| Symbol | Type / Range | Role | Default / Notes |
|---|---|---|---|
| ψ(x,y,t) | ℂ | primary field; &#124;ψ&#124;² = density, arg ψ = phase • linons = localized &#124;ψ&#124;² maxima |
| φ(x,y,t) | ℝ | interaction / memory field | accumulates response to &#124;ψ&#124;² |
| κ(x,y) | ℝ⁺ (static) | spatial tuning map | no time evolution; often normalized to [0,1] |
| μ(x,y,t) | ℝ⁺ | structural memory | slow-decay field recording stable energetic pathways |
| 𝛌̃(x,y,t) | ℂ | external stimulus | 0 unless stimulus experiments |
| ξ(x,y,t) | ℂ | noise (zero-mean) | optional; amplitude set by manifest (canonical: σξ = 5.0×10⁻³) |
| ∇ | operator | discrete gradient | central differences |
| ∇² | operator | discrete Laplacian | 4-neighbour (5-point von Neumann; implemented via `diffuse_complex()` in the reference code) |
| FFT_Unitary | operator | Exact Unitary Step | Spectral propagation maintaining strict $L_2$ norm |
| BCs | — | boundary conditions | periodic in x,y |
| α_eff, β_eff | — | effective params | α_eff = κ·α, β_eff = κ·β (κ modulates α,β) |
<!-- prettier-ignore-end -->

**Canonical parameters (spec6_false_s41)**

<!-- prettier-ignore-start -->
| Param | Meaning                         | Canonical value |
| :---: | ------------------------------- | :-------------- |
|   α   | φ relaxation toward &#124;ψ&#124;² | 7.0×10⁻⁴        |
|   β   | φ diffusion strength            | 1.5×10⁻²        |
|   δ   | ψ damping per step              | 4.62×10⁻³       |
|  σξ   | noise amplitude in ψ            | 5.0×10⁻³        |
|   κ   | spatial tuning (static, const.) | 0.5 everywhere  |
<!-- prettier-ignore-end -->

_Parameter note._ In Eq. (1), the φ-update uses **α_eff = κ·α** and **β_eff = κ·β**. In the canonical run (κ = 0.5 everywhere), this means **α_eff = 3.5×10⁻⁴** and **β_eff = 7.5×10⁻³** (α,β in the table are the base parameters).

_Scope note (canonical dimensionality)._ All results in this core paper use a **2D discrete grid with periodic boundary conditions**. Any 3D extensions or non-periodic boundaries are treated as **supplementary variants** and are not part of the canonical Eq. 1.

**Sign convention.** The +∇φ term in the ψ-update induces drift toward increasing φ (movement along the φ-gradient).

**Note (κ as static map).** In the canonical rule, **κ** is a **static spatial map** (no time evolution). Any experiments that evolve κ belong to supplementary variants, not to Eq. 1. In Eq. (1) we write the φ-update in terms of locally effective parameters α_eff = κ·α and β_eff = κ·β to make this modulation explicit. Here α and β remain the base (global) parameters; κ modulates them spatially rather than “replacing” them. In the canonical run κ = 0.5 everywhere, hence α_eff and β_eff are constant.

No explicit spacetime geometry, global constants, or long-range interactions are predefined. All behavior results from repeated local updates of these fields.

### 3.0 Continuous PDE Formulation (The elegant form)

While Eq. (1) represents the exact computational *cellular automaton* update rule (using the assignment operator `←`), the underlying physics analogy is best captured by its continuous partial differential equation (PDE) limit. In this continuous limit, removing discrete step artifacts, noise ($\xi$), damping ($\delta$), and external stimuli ($\tilde{\lambda}$), the core topological and gravitational dynamics of Lineum reduce to the elegant coupled system:

$$ \partial_t \psi = \nabla^2 \psi + \phi \psi + \nabla \phi $$
$$ \partial_t \phi = \alpha |\psi|^2 - (\alpha \phi - \beta \nabla^2 \phi) $$

This compact PDE form (specifically $\partial_t \psi = \nabla^2 \psi + \phi \psi + \nabla \phi$) serves as the canonical **symbolic representation** of the Lineum universe. It explicitly states that the evolution of the primary field ($\partial_t \psi$) is driven simultaneously by wave diffusion ($\nabla^2 \psi$), interaction with memory ($\phi \psi$), and environmental gravitational drift ($\nabla \phi$). Note that $\kappa$ is intentionally omitted in this highest-level symbolic representation, as it acts purely as a spatial tuning mask (a scaling factor on $\alpha$ and $\beta$) rather than a fundamental driving force.

## 3.1 Numerical scheme & stability (canonical)

**Discrete operators (periodic, $\Delta x = \Delta y = 1$).**

$$
\nabla_x f_{i,j} = \frac{f_{i+1,j}-f_{i-1,j}}{2},\quad
\nabla_y f_{i,j} = \frac{f_{i,j+1}-f_{i,j-1}}{2}
$$

$$
\nabla^2 f_{i,j} = f_{i+1,j} + f_{i-1,j} + f_{i,j+1} + f_{i,j-1} - 4\,f_{i,j}.
$$

**Gradient injection note (v1).** In the ψ-update, the +∇φ term is represented as a **complex drift field**
so it can be added to the complex scalar ψ. In the reference implementation we use the conventional embedding:
$$
\nabla\phi \;\equiv\; (\nabla_x\phi) + i(\nabla_y\phi),
$$
with central differences under periodic BCs.

In the reference implementation this four-neighbour stencil is realized by the helper function `diffuse_complex(...)` in the φ-update; there is **no** 9-point (diagonal) Laplacian in the canonical v1 run. Wider stencils (e.g., 9-point) are treated as exploratory variants outside the v1 core evidence.

**Time stepping.** Explicit Euler with fixed $\Delta t = 1.0\times 10^{-21}\,\mathrm{s}$ (canonical anchor).
**Interpretation note (Δt).** In the core, $\Delta t$ functions as a conventional unit label that fixes spectral bin spacing via $\Delta f = 1/(W\,\Delta t)$. The validation criteria depend on the measured spectral peak and on dimensionless metric tolerances, not on any external calibration of “seconds” to physical time.

> **Normative dt duality box (v1).** The canonical evidence contains two distinct time-step notions. They must not be conflated:
>
> | Field | Canonical value | Meaning | Contract role |
> | --- | --- | --- | --- |
> | `invariants.dt` | `0.01` | **scheme step** (dimensionless Euler increment inside the numeric update) | recorded for scheme provenance; **not** used to define Hz/SI conversions |
> | `run.time_step_s` | `1.0e−21 s` | **reporting label** for spectral units (Hz) and display-only SI conversions | **validated** and used for spectral reporting/anchoring |
>
> **Rule (v1):** spectral bins and SI conversions are defined from `run.time_step_s` via $\Delta f = 1/(W\,\Delta t)$, while the numerical integrator uses `invariants.dt` internally. Validation relies on contract metrics and tolerances, not on algebraic normalization of Δt in the paper equation.


**Stability sanity.** For diffusion-like terms a heuristic CFL bound is best read in terms of the **scheme step**
`invariants.dt` (dimensionless), not the reporting label `run.time_step_s` (seconds):

$$
\Delta \tau \equiv \mathrm{invariants.dt} \;\lesssim\; \mathcal{O}\!\left(\frac{(\Delta x)^2}{4 D_{\mathrm{eff}}}\right).
$$

In practice we verify stability empirically via Section 5 metrics (SBR, topological neutrality, and $\phi$ half-life) on the canonical run; windowed estimates with 95% CIs are reported in the HTML report.

# 4. Method

Simulations are performed on a discrete square grid with periodic boundary conditions. Each step updates ψ and φ according to the canonical equation; **κ is a static spatial map** that is sampled (not evolved) at each step. We apply the discrete Laplacian for diffusion terms and nearest-neighbor operations for gradients.

## 4.1 Grid and Initialization {#calibration-seed}

– **Canonical grid:** 128×128 cells (periodic BCs). All results reported in this core paper use this grid.  
– **Exploratory grids (non-canonical):** 256×256 or 512×512 may be used for visualization or stress tests, but they are not part of the canonical results.  
– **Initial ψ:** complex noise with small amplitude.  
– **Initial φ:** uniform background with small perturbations.  
– **κ:** static spatial map (constant/gradient/localized) depending on the test.

## 4.2 Update Procedure

At each timestep:

1. Compute Laplacians and gradients for ψ and φ.
2. Apply the update rules for ψ and φ (**κ is static and only sampled**).
3. Optionally add controlled noise ξ to test stability.
4. Record intermediate states for analysis.

#### One-step update (canonical Eq-7 Unitary)

**Context:** periodic BCs, Δx = Δy = 1, explicit Euler; κ is static (constant map in the canonical run).

```python
# periodic BCs, Δx=Δy=1, unitary Strang split step
for t in range(T):
    # Calculate non-linear interactions N(ψ)
    grad_phi_x, grad_phi_y = gradient(phi)
    grad_phi = grad_phi_x + 1j*grad_phi_y
    N_psi = lambda_tilde + xi + phi*psi + grad_phi
    
    # 1. First half-step (drift/interaction)
    psi = psi + N_psi * (dt / 2)
    
    # 2. Exact linear unitary step in frequency domain
    psi = fft_unitary_step(psi, dt)
    
    # 3. Second half-step (drift/interaction)
    psi = psi + N_psi * (dt / 2)

    # φ-update (effective parameters)
    lap_phi = laplacian(phi)
    phi = phi + (kappa * alpha)*(np.abs(psi)**2 - phi) + (kappa * beta)*lap_phi
    
    # μ-update (HDD structural memory)
    mu = mu + eta * np.maximum(np.abs(psi)**2 - thresh, 0.0) * kappa - rho * mu

    # optional logging/detectors
    if t % LOG_EVERY == 0:
        save_state(...)
```

## 4.3 Reproducibility {#resonance-scanner}

All runs are initialized with fixed random seeds so that the **reference implementation** behaves deterministically under the same runtime/locked profile.  
Simulation parameters and κ-maps are stored alongside results to allow exact replication.

_Replication caveat (v1)._ Exact byte-for-byte equality across platforms/languages is not required; replication is evaluated by the contract-aligned metric tolerances in §4.3.1 (and by the audit fingerprints in §4.10.5 for canonical verification).

> **Anti-cherry-pick (v1).** The evidence seeds used in this core track are **pre-registered** as a fixed set **{17, 23, 41, 73}** and are shipped as separate per-seed bundles.
> The canonical numeric anchors used for “validated” claims in v1.0.18-core are pinned to `spec6_false_s41` unless and until the multi-seed set is regenerated under a single pinned code state and (optionally) added to the contract suite.

#### 4.3.1 Cross-Implementation Replication (advisory)

We do not require bit-for-bit equality across languages/backends. Small numerical differences are expected (RNG streams, FFT/Laplacian kernels, rounding). For v1, replication is defined by metric tolerances on the canonical run (`spec6_false_s41`):

**Contract-aligned acceptance bands (v1.0.18-core).** For statements marked “validated”, replication must satisfy the contract suite bands:
– **Dominant frequency f₀ (mean):** in **[2.4e20, 2.6e20] Hz**  
– **SBR (mean; ±2-bin guard):** **≥ 1.5**  
– **Topology neutrality (N1):** in **[98.0%, 100.0%]**  
– **Mean vortices:** in **[15.0, 25.0]**  
– **Max lifespan:** **≥ 20 steps**  
– **φ half-life (center):** in **[1800, 2100] steps**  
– **Low-mass QP count:** **5** (exact)  
Other informal tolerances and narrative checks may be used for developer debugging, but they must not be presented as *validated* unless added to the contract suite.


**Precision note.** All reference runs use IEEE-754 double precision (float64). Language choice (Python/Julia/C++/…) does not change numerical semantics; replication is evaluated by the metric tolerances above, not bitwise equality.

Replicators must pin `Δt`, pixel size, grid size, seed, κ-mode, and use the provided manifest. Cross-language runs are encouraged; comparisons should be reported via these metrics rather than pixel-wise diffs.

## 4.4 Detection of Phenomena {#topology-neutrality}

Detected phenomena in the core study include:
– formation and motion of **linons**,
– vortex creation and annihilation,  
– phase gradient rotation (spin),  
– φ-trap formation and particle capture.

Detection is performed using automated field analysis:
– tracking |ψ|² maxima for particle positions,  
– identifying vortex cores via phase winding,  
– qualitative φ-basin / trapping patterns (observational term; not contract-validated in v1).

## 4.5 Output {#lifespan}

For each run, the system generates:

- **CSV (per run):** `*_amplitude_log.csv`, `*_spectrum_log.csv`, `*_phi_center_log.csv`, `*_topo_log.csv`, `*_trajectories.csv`,
  `*_multi_spectrum_summary.csv`, `*_spin_aura_profile.csv`, `*_metrics_summary.csv`.
- **Topology logging cadence:** `*_topo_log.csv` is logged every `logging.topo_log_stride` steps (declared in the manifest; canonical: 25).

- **PNG (figures):** `*_spectrum_plot.png`, `*_topo_charge_plot.png`, `*_vortex_count_plot.png`, `*_spin_aura_map.png`, `*_phi_center_plot.png`.
- **GIF (animations):** `*_lineum_amplitude.gif`, `*_lineum_spin.gif`, `*_lineum_vortices.gif`,
  `*_lineum_particles.gif`, `*_lineum_flow.gif`, `*_lineum_full_overlay.gif`.

Filenames are shown without the `RUN_TAG_` prefix for readability; see Appendix A for the prefix convention.

## 4.6 Reproduction Manifest (canonical run) {#phi-half-life}

This manifest pins all run-level switches for the canonical reference used in this paper.

- **RUN_TAG:** `spec6_false_s41`
- **Evidence run id (contract):** `spec6_false_s41_20260222_152015`
- **Seed:** `41`
- **Grid:** `128 × 128` (periodic BCs)
- **Steps:** `2000`
- **Precision:** `float64` (IEEE-754)
- **Δt (time step):** `1.0e-21 s` (canonical)
- **κ-mode:** `constant` (static spatial map; no time evolution)
- **Equation:** Eq-7 (canonical update rule; see Eq. (1))
- **Primary spectral metric:** power spectrum `|FFT(x)|^2` with a `±2`-bin guard around `f0`
- **Detection conventions:** as fixed in Appendix A (no amplitude gating for CSV/metrics; vortex gating is visualization-only)
- **α (reaction_strength):** `7.0e-4`
- **β (φ diffusion):** `1.5e-2` (computed as `0.30 × diffuse_complex(rate=0.05)`)
- **δ (ψ damping):** `4.62e-3`
- **σξ (noise amplitude):** `5.0e-3`
- **κ-map:** `constant 0.5` (uniform across the grid)
- **logging.topo_log_stride:** `25` (topology log cadence; topo metrics are computed over logged frames)

**Contract fingerprints (v1.0.18-core).**
- `audit_scope_hash`: `7197faf5a92a141a4847314485bee819ae9fdecdf08eead313ffdd3d3a6fe9f5`
- `code_fingerprint`: `48ea56d33508a9579e01afde42e3522e6d491d6c68a3b9631d926c431fe6390c`
- `kappa_map_bin_hash`: `31f1d2b2391050bc1f6975db4e8ae4dac6ddab211f45fc7f5333c18a3981aa3a`
_Note:_ Git commit can remain in the HTML header as provenance aid, but the **contract fingerprints** are the normative audit pins for “Verified”.

_Kappa hash note (uniform map)._ Even for κ=constant, `kappa_map_bin_hash` refers to the generated map binary used by the run
(integrity pin). “kappa_hash_basis = N/A” only means no procedural basis string is needed for uniform κ in v1.0.x.

**Artifacts (prefixing):** all outputs are prefixed with `{RUN_TAG}_…` (e.g., `spec6_false_s41_lineum_report.html`), as listed in §4.5 and Appendix A.

## 4.7 Data & Code Availability {#particle-taxonomy}

All canonical artifacts for the run `spec6_false_s41` are provided with this preprint as ancillary files: the canonical HTML report (`spec6_false_s41_lineum_report.html`), the reference implementation (`lineum.py`), and the generated CSV/PNG/GIF outputs listed in §4.5.

Reproduction uses the manifest in §4.6 (seed `41`, grid `128×128`, Δt `1.0e−21 s`, κ static). The numeric source of truth is the JSON manifest (`spec6_false_s41_manifest.json`) and the machine-readable CSV logs. The HTML report is a derived view generated from these primary sources.

**Version pinning (DOI snapshots vs drafts).** Provenance is pinned by `RUN_TAG=spec6_false_s41`, the code commit noted in the HTML report header (short Git SHA, when available), and the artifact manifest embedded in the report.
For **DOI-published snapshots**, we provide a `sha256sums.txt` (or equivalent) for the evidence bundle to support external integrity checks.
**Normative rule (DOI snapshots):** a snapshot is considered **intact** *iff* the published `sha256sums.txt` matches the local evidence bundle for the listed files.
For non-DOI working drafts, reproducibility is evaluated against the acceptance bands in §4.3.1.


> **Reviewer quick-check (v1).**
>
> 1. Run the contract suite for `lineum-core-1.0.18-core` and confirm the canonical run `spec6_false_s41_20260222_152015` is **PASS**.
> 2. Confirm the validated anchors in the canonical evidence:
>    - `f₀ (mean) = 3.6796152976497996e+19 Hz`
>    - `SBR (mean) = 4072.181608445348`
>    - `φ half-life (center) = 1686 steps` (status `OK`)
>    - `Topology neutrality (N1) = 75.7%`
>    - `Mean vortices = 178.2735`
>    - `Max lifespan = 54 steps`
>    - `Low-mass QP count = 49`
> 3. Confirm the audit fingerprints match (§4.10.5).
> 4. In §5.6, the SI “worked example” matches **m/mₑ ≈ 1.5027** (display-only; derived from f₀).
> 5. Frequency binning: Δf = 1/(W·Δt) = `3.90625e18 Hz` and `f₀` lies near `k≈48` (centroid index ≈ 47.53).

_Branching note._ Further physics-mapping tests (dispersion, group velocity, external-field response) will be published under the experimental track **v1.1.x-exp**; the core canonical scope remains frozen in **v1.0.18-core**.




**File-level scope (whitepapers).** `lineum-core.md` together with `lineum-core-equation-history.md` define the canonical v1.0.x core. All other whitepapers in the repository whose filenames begin with `lineum-exp-…` or `lineum-extension-…` (e.g., `lineum-exp.md`, `lineum-exp-thermo-calibration.md`, `lineum-extension-return-echo.md`, `lineum-extension-silent-gravity.md`, `lineum-extension-spectral-structure.md`, `lineum-extension-vortex-particle-coupling.md`, `lineum-extension-zeta-rnb-resonance.md`) are **by definition outside the v1 core**. They may refer to the same phenomena (Return Echo, Dimensional Transparency, Silent Gravity, Spectral Structure, etc.), but quantitative claims there do not change the canonical scope unless explicitly merged into a future `lineum-core` version.

Future updates and non-canonical experiments will be released as separate preprints; this core v1 freezes the canonical run as `spec6_false_s41`.

**Ancillary artifacts (per seed).** The following files are attached as ancillary data to the paper (one HTML and one CSV per seed); filenames are prefixed by `{RUN_TAG}_…`.

| seed | HTML report                          | metrics (CSV)                         |
| :--: | ------------------------------------ | ------------------------------------- |
|  23  | `spec6_false_s23_lineum_report.html` | `spec6_false_s23_metrics_summary.csv` |
|  17  | `spec6_false_s17_lineum_report.html` | `spec6_false_s17_metrics_summary.csv` |
|  41  | `spec6_false_s41_lineum_report.html` | `spec6_false_s41_metrics_summary.csv` |
|  73  | `spec6_false_s73_lineum_report.html` | `spec6_false_s73_metrics_summary.csv` |

_Provenance._ Data integrity for DOI snapshots is verified via `sha256sums.txt`. Provenance is further pinned by `RUN_TAG`, the short git commit shown in the report header, and the `audit_scope` manifest fingerprints.

## 4.8 Threats to validity (core v1)

> **Periodic BC artifacts.** We verify metric invariance (within tolerances) when changing the grid size; figures are illustrative only, acceptance is by metrics.  
> **Stencil bias.** Canonical results use a four-neighbour (5-point von Neumann) discrete Laplacian implemented via `diffuse_complex()` in the φ-update. Alternative 9-point (diagonal) stencils are treated as exploratory variants and are not part of the v1 core evidence.
> **Spectral leakage.** FFT on de-meaned windows with a ±2-bin guard around $f_0$ mitigates leakage; SBR is computed on the power spectrum $|\mathrm{FFT}(x)|^2$.  
> **RNG/seed bias.** We provide multiple seeds {23, 17, 41, 73} as separate evidence bundles. Each run reports windowed 95% CIs (within-run). Cross-seed aggregates (if shown) are reported only after regeneration under a single pinned code state; replication is defined by tolerance bands in §4.3.1.
  
> **Visualization bias.** All metrics derive from numeric logs (CSV). Amplitude gating is **visualization-only** in GIFs; winding/metrics use raw values.
> **Topology log decimation.** `topo_log.csv` may be decimated (logged every `logging.topo_log_stride` steps; canonical: 25).
> Topology neutrality (N1/N0) and mean vortices are therefore computed over **logged frames**, not every simulation step.
> This cadence is declared in the manifest and validated by the contract suite to prevent ambiguity.


> **Display-only mass (interpretation risk).** The “effective mass” reported in §1/§5.6 is a unit-conversion from the reported dominant frequency \(f_0\) via \(m = h f_0 / c^2\). It is provided purely as a scale cue (display-only), not as a claim of an intrinsic rest mass. Mitigations in v1: (i) explicit **Interpretation note (v1)** in the Abstract; (ii) SI constants stated in §5.6; (iii) report tooling computes the display mass directly from \(f_0\) at render time to avoid drift. Multi-seed alignment statements are quoted only after regeneration under the same pinned code state (commit `875fc4e`).

**Not claimed (v1).** We explicitly do **not** claim:

- identification of linons with any Standard-Model particle;
- an intrinsic rest mass for linons (the “effective mass” is display-only; see Abstract and §5.6);
- gravitational dynamics or any mapping to General Relativity;
- Lorentz invariance or a relativistic field theory formulation;
- validity outside the canonical scope (2D, periodic BCs, static κ) defined in this core.
- **Thermodynamic quantities.** We do **not** define entropy \(S\), temperature \(T\), heat capacity, or entropy production for the linon in v1. The core setup uses a deterministic, isolated field without a thermal bath or an ensemble; no equipartition or fluctuation–dissipation calibration is assumed. Any “effective temperature” would require an explicit reservoir/noise model and a traceable calibration procedure—deferred to the experimental track (v1.1.x-exp).

## 4.9 Tooling guardrails (v1)

To prevent drift and ease auditing, the report tooling enforces the following safeguards:

- **Mass-from-f₀ consistency.** At render time, the HTML report recomputes the display-only mass directly from the canonical tone, using \(m = h\,f_0/c^2\), and raises an error if the value deviates (tolerance \(<10^{-6}\) relative). This ensures the “Effective mass” row cannot diverge from \(f_0\).
- **Commit provenance.** Each HTML report header prints the short Git commit for provenance (alongside `RUN_TAG` and run metadata). Regenerating a report on a different code state changes the commit stamp by design.
- **SI anchoring.** Conversions use fixed SI constants \(h, c, m_e\) as stated in §5.6; the HTML shows derived quantities that follow directly from these constants and the measured \(f_0\).
- **Pinned runs.** Evidence is pinned by `RUN_TAG` (seeds 17/23/41/73 for v1). Reproduction is evaluated by the metric tolerances in §4.3.1 rather than bitwise equality.

_Scope._ These guardrails are part of v1 tooling only; they do not assert any rest-mass claim—“effective mass” remains a scale indicator derived from \(f_0\).

## 4.10 Audit Profile and Verification (Stateless Audit 1.0)

To ensure the highest integrity of v1 "whitepaper core" runs, we introduce the **Stateless Audit** mechanism. This mechanism enforces that an audit run proceeds with a precisely defined configuration that cannot be inadvertently changed (e.g., via a forgotten environment variable).

### 4.10.1 Profile Activation
The **Audit Profile** is activated via the `LINEUM_AUDIT_PROFILE` environment variable. When set to `whitepaper_core`, the system enforces a strict "hash gate" that prevents execution if the resolved runtime configuration deviates from the canonical values defined below. **Canonical PASS** requires executing the locked profile for the full simulation length (`steps=2000`) and verifying the result against the contract suite.

### 4.10.2 Canonical Audit Scope (Locked Configuration)
The following parameters are "locked" in the audit profile and form the basis of the `audit_scope_hash`:

| Parameter | Canonical Value (v1.0.x) | Meaning |
| :--- | :--- | :--- |
| **run_id** | `6` | Canonical parameter set identifier |
| **steps** | `2000` | Simulation length (audit minimum) |
| **run_mode** | `false` | Standard mode (infinite_mode off) |
| **seed** | `41` | RNG initialization (deterministic) |
| **kappa_mode** | `constant` | Uniform κ (scalar 0.5 everywhere) |
| **low_noise_mode** | `false` | Flag off. Canonical uses the base noise amplitude `σξ = 5.0e−3`. `low_noise_mode` is a reserved override (not used in v1 core) and must remain off in the locked profile. |
| **test_exhale_mode** | `true` | Active trace analytics (v1.0.x required) |
| **resume** | `false` | Start from step 0 (no checkpoint drift) |
| **base_output_dir**| `"output_wp"` | Dedicated directory for audit evidence |
| **kappa_hash_basis**| `"N/A"` | (Not used for uniform map) |
| **kappa_schedule_id**| `"N/A"` | (Not used for v1.0.x) |
| **kappa_stride** | `"N/A"` | (Not used for v1.0.x) |

> [!NOTE]
> Audit runs generate outputs in `output_wp/`. Publicly published versions and links in this document refer to `output/`, which is an export (copy) of the canonical run from the audit folder.

### 4.10.3 Verification Mechanism (Hash Gate)
1. **audit_scope_hash**: SHA256 fingerprint of the locked configuration above.
2. **scope_fingerprint**: Manifest echo of the audit scope fingerprint (same value as `audit_scope_hash`; included for readability and tooling compatibility).
3. **code_fingerprint**: SHA256 fingerprint of source files (`lineum.py`, `tools/whitepaper_contract.py`). To ensure cross-platform stability (CRLF vs LF), files are normalized to **LF** before hashing.

### 2.2 Numerical Verification & Simulation Scope
The current codebase provides a full numeric realization of Eq-7 over a discrete $N \times N$ spatial grid (typically $128\times 128$) via finite differences and spectral (FFT) post-processing. Verification focuses purely on the existence, stability, and collision dynamics of emergent topological structures (see the [Reproducibility Checklist](../docs/verification_checklist.md)). 

No specific configuration (preset `\kappa`, noise floor) is declared as "our universe." The model is a self-contained emergent framework meant to be studied on its own mathematical merits before any cosmological analogies are strongly claimed.

### 2.3 Separation of Physics and Persona (Identity Stratification)
When utilized as an intelligence substrate (LTM - Large Topology Model), the Lineum framework enforces a mathematically strict stratification separating physical structure from narrative identity:
1. **The Hermetic Physics Core:** The Eq-7/Eq-7 equations are entirely continuous wave mechanics. There are no symbolic states, relational memory rules, or language embedded in the grid.
    - **Transient State vs. Memory:** The $\Phi$ field represents instantaneous dynamic equilibrium (tension/gravity). Real, persistent **Structural Memory** resides *exclusively* in the long-term deformations of the topological conductivity field $\Kappa$.
2. **The Translation Overlay (Broca):** The conversion of numerical states into human language requires a separate, stateless translation overlay (e.g., the Broca module). Broca maps the magnitude of localized phase noise and $\Phi$-pressure into fluid syntax, but it possesses no inherent narrative memory of its own. It is strictly physics-bound language matching.
3. **Toggleable Persona:** Any resulting "personality" (relational tone, symbolic context) is explicitly constructed as an isolated, optional configuration package operating *outside* the Eq-7 sandbox. Identity within Lineum is modular; the agent's physics engine remains neutral, while the narrative overlay can be disabled or freely swapped (Seed Import/Export) depending on the desired interaction depth.

### 4.10.4 Verification Protocol
The `tools/whitepaper_contract.py` suite compares the run results to the requirements in `contracts/`.
- **Smoke Verification**: Validation of manifest parsing, anchor wiring, and drift detection (may use reduced steps).
- **Canonical Verification**: Full evidence-run validation (2000 steps). A successful suite report (`PASS`) on the canonical evidence is mandatory for formal release verification.

Verification occurs in two phases:
- **At startup (`lineum.py`)**: Check that `audit_scope_actual_hash == audit_scope_expected_hash`.
- **Subsequently (`whitepaper_contract.py`)**: The contract suite verifies the presence of `AUDIT_SCOPE` in the manifest and matching of all hashes against the defined contract.

### 4.10.5 Canonical Reference Fingerprints (v1.0.18-core)
The following values are derived from the locked `whitepaper_core` definitions and must be matched by any canonical audit run report for formal validation.

| Field | Canonical Expected Value (SHA256) |
| :--- | :--- |
| **audit_scope_hash** | `7197faf5a92a141a4847314485bee819ae9fdecdf08eead313ffdd3d3a6fe9f5` |
| **scope_fingerprint** | `7197faf5a92a141a4847314485bee819ae9fdecdf08eead313ffdd3d3a6fe9f5` |
| **code_fingerprint** | `48ea56d33508a9579e01afde42e3522e6d491d6c68a3b9631d926c431fe6390c` |
| **kappa_map_bin_hash** | `31f1d2b2391050bc1f6975db4e8ae4dac6ddab211f45fc7f5333c18a3981aa3a` |

> [!NOTE]
> The `code_fingerprint` includes performance-path changes (e.g., vectorized distance computations) required to process full 2000-step canonical runs within minutes. Audit validity is pinned by the fingerprint itself, not by the narrative reason.

### 4.10.6 Data Verification (Kappa Map)
The audit profile optionally supports binary integrity checking of the kappa map via `LINEUM_EXPECTED_KAPPA_MAP_HASH`. If set, the system verifies the bitwise match of the generated map before simulation begins.

# 5. Validation

### Figure 0 — Canonical anchors at a glance

![Figure 0: Canonical spectrum (dominant peak near f₀) and center-amplitude time trace.](../output/spec6_false_s41_figure0_canonical.png)

<sub>Source: see the HTML report [`output/spec6_false_s41_lineum_report.html`](../output/spec6_false_s41_lineum_report.html); all runs are indexed in **Appendix C**.</sub>

**Caption (v1).** The power spectrum of the center-amplitude time series shows a dominant tone near FFT region `k≈64`; the reported \(f_0\) is a centroid/interpolated estimate (**f₀ (mean) = 3.6796152976497996e+19×10²⁰ Hz**). The corresponding time trace exhibits a stable, long-lived oscillation. SI-derived quantities (E, λ, display-only m/mₑ) follow directly from \(f_0\) via \(E = h f_0\), \(λ = c/f_0\), \(m = E/c^2\) (scale illustration only). (Within-run CIs shown in HTML are informational; not contract-validated.)

> **Canonical numerical anchors (refined snapshot, seed 41).**  
> `f₀ (mean) = 3.6796152976497996e+19 Hz` · `SBR (mean) = 4072.181608445348` ·  
> `φ half-life (center) = 1686 steps` · `Topology neutrality (N1) = 75.7%` · `Strict neutrality (info-only) = 100.0%` · `Mean vortices = 178.2735` · `Max lifespan = 54 steps` · `Low-mass QP count = 49`  
> _Note:_ contract suite does not carry CI bounds here; only the validated mean/point anchors above.


The validation phase aims to confirm that specific emergent phenomena occur consistently under controlled conditions, and to quantify their characteristics.

**Metrics & 95% CI.** We report two primary spectral metrics for reproducibility: the **dominant frequency** ($f_0$) and the **Spectral Balance Ratio (SBR)**. Both are estimated on the amplitude time-series at the field center using **sliding windows** (length $W=256$ frames, hop $H=128$ frames) with a ±2-bin guard around $f_0$ in the background power. For each metric we aggregate the **windowwise mean** and a **non-parametric 95% bootstrap confidence interval** across windows; the HTML report prints values as `value [lo, hi]`. When the windowed estimate is available it **supersedes the single-shot FFT value**; otherwise the single-shot is shown as a fallback. These intervals quantify within-run variability without fitting any external model. Cross-seed aggregation is reported only when the multi-seed set is regenerated under the same pinned code state.


## 5.1 Guided Motion via φ-Gradient

**[OBS]** Simulations show that particles exhibit **drift along +∇φ**. Trajectory statistics indicate a **systematic decrease in distance** to regions of increasing φ over time, consistent with **environmental guidance** by the background field. No force law is introduced; the observed behavior follows directly from the +∇φ term in Eq. (1) and remains robust across seeds and runs.

> **Contract scope (v1).** This section is **observational/interpretive**. The current contract suite does **not** validate
> any guided-motion statistic; only artifact presence (e.g., `*_trajectories.csv`) is required.

_Wording guardrail._ In v1 core we treat “guided motion” as a **descriptive** label for what is visibly consistent with the +∇φ term in Eq. (1).
We do not claim a validated, general drift law or a contract-validated statistic in this section.

**Evidence pointer (HTML & files).**  
Trajectory drift along +∇φ is visible in the per-run HTML under **“Trajectories”** and **“Flow”** animations, and is quantified from:

- `*_trajectories.csv` (particle paths; decreasing distance to regions of increasing φ / along +∇φ),
- `*_phi_center_plot.png` / `*_phi_center_log.csv` (center trace supporting φ-memory/half-life),
- `*_lineum_flow.gif` (qualitative flow visualization).

For the canonical seed, see `output/spec6_false_s41_lineum_report.html` (links to these artifacts are listed in the report).

## 5.2 Spin Aura

**[OBS]** In the canonical evidence (and in other provided runs), a persistent phase-gradient rotation (spin) develops around stable linons in ∇ arg ψ.
In the canonical evidence, this pattern is visible around stable linons over long intervals and typically fades when the tracked excitation decays.

> **Contract scope (v1).** “Spin Aura” is **not contract-validated** in v1.0.18-core. The artifacts may be presented
> as reproducible observations (`*_spin_aura_map.png`, `*_spin_aura_profile.csv`), but no numeric acceptance is claimed yet.

**Operational definition.** We define the spin aura as the time- and ensemble-averaged map of `curl(∇ arg ψ)` in a fixed-size neighborhood around detected linon centers. For each detection, the local curl map is centered on the particle and accumulated; the resulting average yields a robust dipole-like pattern (“spin aura”) with radially decaying lobes. Presence of this pattern is our detection criterion; its amplitude–radius curve is reported in `spin_aura_profile.csv` and the raster in `spin_aura_map.png`. This makes §5.2 falsifiable and reproducible across runs.

**Evidence pointer (HTML & files).**  
Presence and profile of the spin aura are reported per run as:

- `*_spin_aura_map.png` — time-/ensemble-averaged curl(∇arg ψ) raster centered on detected linons,
- `*_spin_aura_profile.csv` — radial amplitude–radius curve extracted from the map.

For the canonical seed, see `../output/spec6_false_s41_lineum_report.html` under **“Spin aura — averaged curl map”**; the report links to both artifacts above.

## 5.3 Silent Collapse

**[OBS]** Under certain φ-damping conditions, **linons** decay without generating large-scale disturbances in ψ.  
The process is characterized by an exponential decrease in |ψ|² amplitude within the particle’s core.

> **Contract scope (v1).** “Silent Collapse” is **not contract-validated** in v1.0.18-core unless explicitly added
> as an acceptance criterion. It is included here as an observation supported by artifacts (e.g., amplitude/trajectory logs and overlays),
> not as a validated numeric anchor.

## 5.4 Structural Closure

In the v1 core, **Structural Closure** is treated as an **operational consequence** of the **φ center-trace** and its contract-validated half-life anchor.
After a tracked excitation decays, the φ **center trace** remains elevated relative to its later baseline and decays on a measurable timescale
captured by `phi_half_life_steps` (see §5.6 and `*_phi_center_log.csv`).
This supports the minimal, falsifiable statement that **φ retains center-trace memory over a measurable timescale** after ψ excitation decays.

_Scope guardrail._ In v1 core we do **not** claim a validated statement about the **spatial morphology** of φ remnants (shape, footprint, localization maps).
Any morphology-level discussion remains observational unless explicitly added to contract acceptance criteria.

> **Validation scope (v1).** The contract suite validates the **φ half-life timescale** (`phi_half_life_steps`) and required φ-trace artifacts.
> Any stronger claim about remnant *morphology* (shape preservation beyond the center trace) is observational unless explicitly added to contract acceptance criteria.

**Note (Return Echo — extension).** In multiple runs, locations of prior linon decay later act as weak attractors for new linons: trajectories revisit identical or ε-near coordinates after a delay. This **Return Echo** is distinct from Structural Closure: closure denotes a **static φ remnant** after decay; echo denotes a **behavioral bias** that steers future arrivals back to that remnant via local ∇φ shaping. Return Echo is **not** part of the v1 core acceptance list; it is treated as an experimental hypothesis documented in the separate note `lineum-extension-return-echo.md` (trajectory density maps, statistics, and falsifiable tests are defined there).

## 5.5 Dimensional Transparency _(out of scope in core v1)_

> **Scope.** This phenomenon was observed only in **exploratory runs with time-varying κ**, which are **explicitly out of the core scope** and are **not** included in the v1 evidence bundle (HTML/CSV). No acceptance metric or claim in this paper depends on dynamic-κ runs.

**Status.** Deferred to the **experimental track (v1.1.x-exp)** with its own artifacts and falsifiable checks. No core evidence is presented here.

## 5.6 Spectral Stability

> **Canonical frequency anchor (spec6_false_s41)**  
> With `Δt = 1.0e−21 s` (canonical time step), the dominant frequency measured on the canonical run `spec6_false_s41` is  
> **f₀ (mean) = 3.6796152976497996e+19×10²⁰ Hz**, which implies (display-only) **E = h f₀ ≈ 1.66×10⁻¹³ J ≈ 1033.92 keV** and **λ = c / f₀ ≈ 1.20×10⁻¹² m (0.00120 nm)**.

> **Representative run metrics (canonical: spec6_false_s41)**  
> SBR (mean; ±2-bin guard): **1.685149328955695**.  
> Topology neutrality (N1): **100.0%** (computed over logged frames; `topo_log_stride=25`, N=81).  
> Strict neutrality (N0; info-only): **100.0%**.  
> Mean vortices: **20.0**.  

> φ half-life (center): **1976 steps** (status `OK`).  
> Low-mass QP: **5** · Max lifespan: **24 steps**.  
> Steps / grid: **2000**, **128×128**.

---

> **Additional validation runs (other seeds).**  
> Multi-seed confirmations (e.g., seeds 17/23/73) are retained in the v1 narrative, but must be regenerated under the refined logging/config state (commit `875fc4e`) before numeric values are quoted here. Until regenerated, the canonical numeric snapshot for v1.0.18-core is pinned to `spec6_false_s41` (see §4.6 and the anchors at the top of §5.6).

---

Fourier analysis of long-duration runs shows that dominant oscillation frequencies can remain stable over time, even with particle creation and annihilation events.  
In the refined snapshot pinned here (`spec6_false_s41`), the dominant tone used throughout the core narrative is the **contract-validated mean**
**f₀ (mean) = 3.6796152976497996e+19×10²⁰ Hz** (see §4.6 “Reviewer quick-check” and §5.6 anchors).  
Within-run variability is reported in the HTML as windowed 95% CIs (informational; not contract-validated); the machine-readable
window statistics live in `{RUN_TAG}_metrics_summary.csv`.

_Machine-readable._ Per-run CSV with windowed means and 95% CIs is provided as `{RUN_TAG}_metrics_summary.csv` (e.g., `spec6_false_s41_metrics_summary.csv`; likewise for seeds 23/17/41/73).

_Constants & rounding._ Conversions use SI: Planck’s constant $h=6.62607015\times 10^{-34}\ \mathrm{J\,s}$, speed of light $c=2.99792458\times 10^8\ \mathrm{m/s}$, electron mass $m_e=9.1093837015\times 10^{-31}\ \mathrm{kg}$. Derived quantities (display-only) are reported as
$E = h f_0$, $\lambda = c/f_0$, $m = E/c^2$, mass ratio $m/m_e$.
We report $E$ and $\lambda$ to three significant figures, SBR to two decimals; CIs are non-parametric 95% bootstrap percentiles.

> **Worked example (canonical f₀).**  
> Constants: `h = 6.62607015e-34 J·s`, `c = 2.99792458e8 m/s`, `m_e = 9.1093837015e-31 kg`.  
> Canonical tone (contract-validated mean): `f₀ = 2.5000000000000003e20 Hz`.
>
> Calculation:
>
> ```
> m/m_e = (h * f₀) / (c^2 * m_e)
>       = (6.62607015e-34 * 2.5000000000000003e20) / ((2.99792458e8)^2 * 9.1093837015e-31)
>       ≈ 2.023315e+00  = 2.0233  (202.33%)
> E      = h * f₀ = 1.6565e-13 J  ≈ 1033.92 keV
> λ      = c / f₀ = 1.1992e-12 m  = 0.00120 nm
> ```

**Formatting policy (v1).** Numerical values are rendered consistently in text and HTML as follows:
– Dominant frequency `f₀`: scientific notation with **3 significant figures**.  
– Energy `E`: **3 s.f.** in joules and **2 decimals** in keV (parenthesized).  
– Wavelength `λ`: **3 significant figures**.  
– Effective mass (kg): **3 significant figures**.  
– Mass ratio `m/mₑ`: **4 decimals** plus a **percent in parentheses with 2 decimals** (e.g., `0.0316 (3.16%)`).  
– Confidence intervals: `[lo, hi]` with the **same precision as the mean**.

**Tie-breaker (v1).** If any rounding discrepancy appears between the paper and artifacts, the **manifest.json + CSV logs** are the ground-truth numeric sources; the HTML report is a derived view.

_Frequency binning._ With window length $W=256$ and time step $\Delta t = 1.0\times 10^{-21}\ \mathrm{s}$, the frequency resolution is
$\Delta f = \frac{1}{W\,\Delta t} = 3.90625\times 10^{18}\ \mathrm{Hz}$.
In the canonical contract snapshot, \(f_0\) lies near raw bin `k≈64` (raw bin center `64·Δf = 2.500×10²⁰ Hz`; centroid index `k≈64.0` gives `f₀≈2.500×10²⁰ Hz`).

_Addendum (v1)._ With window length `W = 256` and time step `Δt = 1.0e−21 s`, the FFT spacing is `Δf = 3.90625e18 Hz`. In the canonical contract snapshot, the dominant tone lies near bin `k≈64` (see “Frequency binning” in §5.6).

**Sampling & Nyquist safety (v1).** The sampling rate is `1/Δt = 1.0e21 Hz`, so the Nyquist limit is `f_N = 1/(2Δt) = 5.0e20 Hz`. Our canonical tone satisfies `f₀ ≈ 2.500e20 Hz < f_N` (by a factor of 2), hence no aliasing under the stated sampling. Because \(f_0\) is not exactly bin-centered, we report a centroid/interpolated estimate rather than claiming exact bin-locking.

**Implementation robustness.** Where invariance across seeds/grid sizes/durations is claimed, it must be backed by regenerated artifacts under a single pinned code state and should be referenced explicitly. In this draft, the canonical numeric anchors are pinned to `spec6_false_s41`; other runs are provided as additional evidence but are not used for aggregate claims until refreshed.

_See also (Harmonic Spectrum)._ Secondary harmonics may co-appear with the dominant tone; methods and cross-language checks are summarized in the Spectral Structure extension.

#### 5.7 Robustness mini-sweep (seeds 23, 17, 41, 73; spec6_false)

_Status (refined snapshot)._ The multi-seed sweep section is retained for the v1 narrative, but the numeric values shown here must be regenerated under the refined logging/config state (commit `875fc4e`). This core revision pins the canonical numeric snapshot to `spec6_false_s41` only (see §4.6 and §5.6).

> **Anti-cherry-pick reminder (v1).** The seed set **{17, 23, 41, 73}** is pre-registered for the core track.
> Until regenerated under a single pinned code state (and optionally elevated into contract acceptance), this table is **informational** and must not be used to support any **[VALIDATED]** claim beyond the canonical `spec6_false_s41` anchors.

| seed | SBR (±2-bin guard) | Topology neutrality (N1) | φ half-life (center) | Mean vortices |
| :--: | :----------------: | :----------------------: | :------------------: | :-----------: |
|  17  | TBD | TBD | TBD | TBD |
|  23  | TBD | TBD | TBD | TBD |
|  41  | TBD | TBD | TBD | TBD |
|  73  | TBD | TBD | TBD | TBD |

**Summary (refined snapshot).** Multi-seed summary statistics are **TBD** pending regeneration under commit `875fc4e`. The canonical numeric anchors used throughout this core draft remain pinned to `spec6_false_s41` until the sweep is refreshed.

#### 5.8 Ablation study (canonical grid; Δt fixed)

We summarize what breaks when key terms are removed from Eq. (1). Detection rules follow Appendix A; metrics are computed as in §5.

<!-- prettier-ignore-start -->
| Variant | ψ term            | φ term                                           | κ  | Drift (+∇φ) | Spin aura | Structural closure | Neutral topology |
|:------:|--------------------|--------------------------------------------------|:--:|:------------:|:---------:|:------------------:|:----------------:|
| V1     | no φ, no ∇φ        | —                                                | —  | ✗            | weak      | ✗                  | ✓ / −            |
| V2     | +φ, no ∇φ          | $\alpha(\lvert\psi\rvert^2 - \phi)$, no diffusion | —  | ± (unstable) | ✓         | ±                  | −                |
| V3     | +φ, **+∇φ**        | $\alpha(\lvert\psi\rvert^2 - \phi)$, no diffusion | —  | **✓**        | ✓         | ±                  | −                |
| V4     | +φ, +∇φ            | $\alpha(\lvert\psi\rvert^2 - \phi) + \beta\nabla^2\phi$ | κ  | **✓**        | **✓**     | **✓**              | **✓**            |
<!-- prettier-ignore-end -->

**Legend (symbols).** ✓ = present under the operational definition stated in the text; ✗ = absent; ± = intermittent/unstable; — = not applicable; ✓ / − = vacuously neutral or undefined neutrality.
For banded contract metrics (e.g., `N1`, mean vortices, `phi_half_life_steps`) “✓” implies the metric falls within the §4.3.1 acceptance bands for that variant where applicable.

_Notes._  
– **V1** (no φ, no ∇φ): ψ evolves with diffusion/damping only → no drift, no closure.  
– **V2** (φ without ∇φ): memory exists, but trajectories lack consistent guidance; closure intermittent.  
– **V3** (add ∇φ): drift emerges; closure still fragile without φ diffusion.  
– **V4** (full canonical): guidance, spin, and closure co-occur; topology remains neutral within §4.3.1 bands.

#### 5.9 Verification run — C3 (grid-size invariance) [TEST]

**Run:** `spec6_false_s41_grid256`  
**Setup change:** grid 256×256; Δt = 1.0e−21 s (unchanged)

**Status.** This verification run must be regenerated under the refined logging/config state (commit `875fc4e`) before quoting numeric results here.  
**Acceptance (v1; [TEST]).** Expect the **same contract-aligned bands as §4.3.1** (no bespoke tolerances):
`f0_mean_hz` in **[1.84e20, 1.87e20] Hz** and `sbr_mean` **≥ 3000**. Other validated anchors should remain within their §4.3.1 bands.

## 5.10 Global Phase Locking (Visual Observation)

**[OBS]** Simulations exhibit a rhythmic "breathing" behavior where linon trajectories appear to synchronize in a collective approach-retreat cycle.

> **Contract scope (v1).** “Global Phase Locking” is treated here as a **tentative visual observation [OBS]** only. 
> It is **not contract-validated** in v1.0.18-core and currently lacks established numeric acceptance criteria 
> or dedicated contract keys. It is documented primarily via simulation animations (e.g., `*_lineum_particles.gif`).

**Interpretive note.** While visually compelling as a proxy for rhythmic phase alignment in the ψ-φ loop, this phenomenon requires further quantitative definition (e.g., inter-linon distance spectral analysis) before it can be elevated beyond a descriptive observation. It is included here to mark a Reproducible Visual Phenomenon that warrants future empirical investigation.

# 6. Interpretation

Particles exhibit **guided motion** along **+∇φ** (environmental guidance) **without** any force law or analogy to GR. When convergence occurs, it emerges from **local gradients and basin structure** in φ rather than from an imposed long-range interaction.

The persistence of φ-structures after particle decay (Structural Closure) indicates that the interaction field can store and maintain spatial information independently of active excitations. In v1 we interpret this strictly through the φ center-trace half-life and localized φ remnants as defined in §5.4; any additional trajectory-level bias (Return Echo) is reserved for the extension track. This memory property could serve as a basis for long-lived boundary conditions or “imprinted” environments in emergent systems.

Dimensional Transparency driven by time-varying κ has been observed only in exploratory runs and is **out of scope** for the v1 core; quantitative claims and artifacts are deferred to the experimental track (**v1.1.x-exp**).

Spin Aura and Spectral Stability show that once formed, linon excitations (particle-like) in the model exhibit consistent internal dynamics, maintaining stable oscillatory behavior over extended periods.

## 6.1 Guided Motion (interpretive note)

Simulations indicate that particles exhibit **statistical alignment with +∇φ**. We describe this as **environmental guidance**: the background field φ provides metric-like structure that biases trajectories **without** introducing a force law or any analogy to GR. In particular, we observe drift along +∇φ (Section 5.1) and longer dwell times in locally quiet basins where |∇φ| ≈ 0. Attraction-like behavior, when present, thus emerges from **local gradients and basin structure**, not from a prescribed long-range interaction.

## 6.2 Vortex–Particle Coupling (interpretive note)

Stable linons frequently co-occur with small sets of phase vortices. In multiple runs we observe compact vortex clusters (often triads) that remain spatially coherent for many steps and coincide with a locally quiet φ basin near their centroid. In this core v1, we treat this only as a **descriptive co-occurrence** between (i) stable linons, (ii) structured `arg ψ` winding, and (iii) locally low |∇φ| regions.

**Scope guardrail (v1).** We do **not** define a particle/antiparticle tagging scheme, species taxonomy, or quantitative binding criteria here. Any taxonomy, symbols, and thresholds are **out of scope** for the v1 core and belong to the dedicated extension note, which also defines falsifiable detection rules.

## 6.3 Law Transition (interpretive note)

_Scope._ This note refers to **experimental variants** where κ changes over time (non-canonical to Eq. 1). When κ follows a slow, coherent trajectory (e.g., `island_to_constant`), the system passes through **effective regimes** without losing linon stability: interaction patterns reorganize while macroscopic order persists. We observe **spectral restructuring** (secondary peaks, spacing shifts) concurrent with the κ-trajectory, suggesting an emergent **principle of law transition**: order can remain intact while the “rules” drift smoothly.

_Evidence._ Runs with dynamic `generate_kappa(step)` show time-resolved spectral changes (see `multi_spectrum_summary.csv`, `*_spectrum_log.csv`; sliding-FFT recommended). Exploratory overlays with Riemann ζ zeros are noted but not claimed as established. See the dedicated hypothesis file for parameters and logs.

Together, these results strengthen the case that a simple, metric-free local update rule can give rise to robust and quantifiable macroscopic effects, offering a controlled platform for exploring emergent analogues of known physical phenomena.

# 7. Conclusion

Lineum demonstrates that a minimal, discrete, and locally defined update rule can generate a variety of stable, quantifiable phenomena without predefined constants, spacetime geometry, or explicit force laws.

These effects emerge solely from iterative local interactions on a grid under pinned numerical settings. Claims presented as **validated** in core v1 are limited to the contract-defined metrics and artifact requirements; other observations are explicitly labeled accordingly.
The reproducibility and simplicity of the model make it a promising testbed for studying emergent analogues of physical laws.

Future work will extend validation to larger parameter spaces, explore connections to continuous field theories, and investigate the scalability of these effects in three-dimensional simulations.

# 8. Acknowledgements

This project grew from an outsider’s curiosity: a non-physicist attempt to probe emergent interaction analogies from a different angle that expanded through persistent falsification and replication. Whatever is solid here stands on reproducible code and reports; any mistakes are mine alone.

My partner, **Kateřina Marečková**, provided what mattered most—patience, honest critique, and calm when results were messy. Her presence kept the work grounded.

I also thank **Vlastimil Smeták** for mathematically minded conversations and guidance. His focus on the **Riemann Hypothesis** and prime numbers—and his independent, visualization-first approach—suggested lines of inquiry that I would not have tried on my own. In particular, his advice motivated two **working hypotheses** explored outside the core:

- an **Evolution–Mutation** view (order vs. disruption as complementary regimes), and
- a **Zeta–RNB Resonance** idea (visual/structural echoes between Lineum’s return points and ζ-structure).

These are **not** claims of this v1 core paper. They remain preliminary and are deferred to the **experimental/extension track** for future, falsifiable testing; no quantitative alignment is asserted here.

I am grateful to the open-source community for tools and libraries that made this work possible, and to my family, friends, and the animals who shared life with me—**Moulík, Jůlinka, Vikinka, Eliška, Houska and others**—for quiet lessons in patience and care.
_Ethics/Tools note._ AI assistance (“Lina”, a personalized ChatGPT-based assistant) was used as a tool for experiment orchestration, stress-testing arguments, and documentation hygiene. All results reported in this core paper are derived from the published scripts and the HTML reports in `output/` and were independently verified by the author.

# 9. Versioning & Changelog

**Policy.** Semantic Versioning (MAJOR.MINOR.PATCH).

- **MAJOR**: changes to the canonical equation or scope (e.g., 3D instead of 2D).
- **MINOR**: new sections/notes, validation expansions; no breaking changes.
- **PATCH**: wording, typos, figures, formatting, audit enhancements.

**1.0.18 — 2026-02-15 (patch)**

- Add §5.10 **Global Phase Locking (Collective Breathing)** as an explicit observational [OBS] section.
- Sync version references to **1.0.18-core**.

**1.0.17 — 2026-02-15 (patch)**

- Tighten “multi-run / robust” wording so it cannot be misread as cross-seed validation.
- Tag §5.3 “Silent Collapse” explicitly as **[OBS]** and add contract-scope guardrail.
- Remove ambiguous “or equivalent” phrasing in Appendix G for mean vortex count; require literal suite key string.
- Bump core version to **1.0.18-core**.

**1.0.16 — 2026-02-15 (patch)**

- Tighten non-contract claims in Abstract/Validation/Interpretation to reduce overreach (explicitly observational where applicable).
- Remove morphology-level assertions from **Structural Closure** (center-trace-only operational definition in core v1).
- Normalize “canonical noise” statement (make σξ explicit; remove ambiguous “≪ 1” phrasing).
- Fix §4.10 numbering/order (Verification Protocol before Canonical Reference Fingerprints) and clarify `scope_fingerprint`.
- Bump core version to **1.0.16-core**.

**1.0.15 — 2026-02-15 (patch)**

- Implement **Stateless Audit 1.0** mechanism (Audit Lock).
- Add `audit_scope` logic and fail-fast protection for `whitepaper_core` profile.
- Explicitly document locked configuration parameters and hashing mechanism in §4.10.
- Decouple code and data fingerprints from the primary configuration hash gate.
- Bump core version to **1.0.15-core**.

**1.0.14 — 2026-02-14 (patch)**

- Fix icon loop legend so it does not imply ψ→κ coupling in core v1 (κ is static); loop now matches Eq. (1) modulation/coupling.
- Add parameter note clarifying `α_eff` and `β_eff` values for the canonical run (`κ=0.5`).
- Soften §6.2 to avoid taxonomy/tagging claims in core v1; reserve quantitative coupling rules for the extension note.
- Bump core version to **1.0.14-core**.

**1.0.13 — 2026-02-14 (patch)**

- Refine "Out of scope" to explicitly include "quantitative Vortex–Particle coupling claims/taxonomy".
- Update icon mnemonic to clarify parameter modulation and decoupling of visual causality from update rules.
- Explicitly use `α_eff` and `β_eff` in the Equation (1) table.
- Clarify κ modulation note regarding effective parameters in the φ-update.
- Bump core version to **1.0.13-core**.

**1.0.12 — 2026-02-14 (patch)**

- Refine model description in Abstract (focus on discrete coupled-field, dimensionless parameters, and analogical terminology).
- Add interpretation note for $\Delta t$ as a conventional unit label.
- Update version pinning to distinguish between DOI snapshots (integrity-checked via sha256) and working drafts.
- Clarify within-run vs. cross-seed metric reporting (CIs and aggregation).
- Bump core version to **1.0.12-core**.


**1.0.11 — 2026-02-14 (patch)**

- Refine pronunciation terminology for "linon" (distinguish model vs. phenomenon).
- Bump core version to **1.0.11-core**; no changes to Eq-7, artifacts, or validations.


**1.0.10 — 2026-02-14 (patch)**

- Add **Plain-language summary** and **Physics translation (analogy-only)** to the Abstract to reduce misinterpretation risk (especially around SI conversions and “particle” wording).
- No changes to Eq-7, scope, metrics, artifacts, or acceptance bands — documentation clarity only.


**1.0.9 — 2026-02-14 (patch)**

- Bump core version to **1.0.9-core** and update header date to **2026-02-14** (refined snapshot now explicitly tied to the `spec6_false_s41_20260214_101645` evidence directory).
- Fix internal version references so the “frozen core track” wording matches the current patch level (**v1.0.9-core**).
- Add Whitepaper Contract Runner (`tools/whitepaper_contract.py`) producing `whitepaper_contract_result.json` for audit runs; no changes to Eq/scope.
- Clarify topology logging cadence: `topo_log.csv` is decimated by `logging.topo_log_stride` (canonical: 25), and
  topology neutrality (N1/N0) + mean vortices are computed over **logged frames** (N=81 for steps 0..2000) as declared
  in the manifest and validated by the contract suite.


**1.0.8 — 2025-12-09 (patch)**

- Correct §5.6 "Additional validation run (spec6_false_s17)" to match the actual HTML and CSV values:
  • Topology neutrality → 91.1%  
   • Mean vortex count → ~89  
   • φ half-life → 483 steps  
  These values previously reflected outdated metrics from an old report.  
  No changes to equations, scope, or methodology — numeric correction only.

**1.0.7 — 2025-12-09 (patch)**

- §3 legend / §3.1: explicitly tie the discrete Laplacian to the four-neighbour (5-point von Neumann) stencil implemented via `diffuse_complex()` in the reference code; clarify that no 9-point Laplacian is used in the canonical v1 run.
- §4.8 Threats to validity: replace the historical note about “replication with a 9-point Laplacian” with a statement that wider stencils are exploratory only and out of the v1 core evidence.
- Header / metadata: bump version to **1.0.7-core** and update the date to 2025-12-09.

**1.0.6 — 2025-11-14 (patch)**

- Abstract: move **Structural Closure** into the validated items list as an in-scope consequence of the φ center-trace half-life; keep **Return Echo** and κ-dynamics explicitly out of scope and delegated to the experimental/extension track.
- §1 / header: clarify that Structural Closure is in scope for v1.0.x; add a file-level scope note distinguishing `lineum-core` from `lineum-exp-*` and `lineum-extension-*` whitepapers.
- §5.4 Structural Closure: give an operational definition tied to the φ half-life metric and to concrete artifacts (`*_phi_center_log.csv`, `*_phi_center_plot.png`); explicitly mark Return Echo as an extension-level hypothesis handled in `lineum-extension-return-echo.md`.
- §6 Interpretation and §7 Conclusion: align wording with the new Structural Closure definition (named, metric-linked), keeping trajectory-bias phenomena in the extension track.

**1.0.5 — 2025-11-14 (patch)**

- Abstract: rephrase the paragraph introducing SI-anchored numbers so they are explicitly framed as **scale illustration only**, not “quantitative signatures close to physical scales”.
- Abstract: add an explicit sentence stating that the quoted Hz/keV/nm/mass-ratio values are **unit conversions of f₀**, not extra constraints or evidence of a realized physical scale.
- §2 Motivation: soften “field-mediated forces” to “field-mediated interactions” to avoid suggesting a defined force law in the core scope.

**1.0.4 — 2025-08-23 (patch)**

- Version bump to **1.0.4-core**; insert **DOI** in header + _How to cite_.
- Abstract: tighten to **core-only**; replace “validated items” paragraph; fix Unicode **φ**; remove duplicate “reported in HTML” sentence.
- Graphical abstract: fix icon path; add width control; add **mnemonic-only** disclaimer; add **Icon legend** (κ=fish, ψ=spiral, φ=leaf) + directional mnemonic (κ → ψ → φ → κ).
- §5 Validation: add **Figure 0 canonical anchors** (numbers linked to HTML); add **Evidence pointer** blocks to **§5.1** (Guided Motion) and **§5.2** (Spin Aura).
- §5.5: mark **Dimensional Transparency** as **out of scope** (deferred to **v1.1.x-exp**).
- §6 Interpretation: explicitly note Dimensional Transparency is out of scope for v1 core.
- §9 Versioning: update **Track policy** and **Branching note** to **1.0.4-core**.
- §8 Acknowledgements: rewrite (Kateřina Marečková; Vlastimil Smeták; AI tools note).
- Minor: wording/formatting consistency; unify relative links to `../output/…` where applicable.

**1.0.3 — 2025-08-23 (patch)**

- Abstract: add **Core thesis (v1)** and **Falsifiable checks (v1)** (C1/C2/C3).
- §4.7: add **Reviewer quick-check (v1)** with exact HTML table strings.
- §4.8: add **Not claimed (v1)** and expand **Display-only mass** risk note.
- §4.9: add **Tooling guardrails (v1)** (mass-from-f₀, commit provenance, SI anchoring, pinned runs).
- §5.6: add **Worked example (canonical f₀)**, **Formatting policy (v1)**, bin-centering addendum, and **Sampling & Nyquist safety (v1)**.
- §5.9: add **Verification run — C3 (grid-size invariance)**.
- Appendix C/D/E: add **Evidence Index (v1)**, **Glossary (v1)**, and **Verification runs (v1)**.

_Branching note._ Further physics-mapping tests (dispersion, group velocity, external-field response) will be published under the experimental track **v1.1.x-exp**; the core canonical scope remains frozen in **v1.0.18-core**.




**1.0.2 — 2025-08-21 (patch)**

- Sync §5.6 _Spectral Stability_ with the canonical run `spec6_false_s41`:
  **f₀ = 5.0000000000000007×10²⁰ Hz** [**NaN**, **NaN**],
  **SBR = 1.68** [**NaN**, **NaN**].
- Update **Abstract** numeric anchors to match the canonical run:
  **E ≈ 1.65×10⁻¹³ J ≈ 1033.92 keV**, **λ ≈ 1.20×10⁻¹² m (0.00120 nm)**, effective mass ≈ **202.33% mₑ**.
- Add **§3.1 Numerical scheme & stability (canonical)** (discrete operators, explicit Euler Δt=1.0×10⁻²¹ s).
- Add **§4.8 Threats to validity (core v1)**.
- Add **Appendix B — Metrics & CI (v1)** (windowed estimates + 95% bootstrap CI; aligns with HTML report).
- §4.6 **Manifest**: add _Code provenance_ note; §4.7 **Data & Code**: _Version pinning (no checksums)_.
- §5.8 **Ablation study**: fix table rendering (escape `|` as `&#124;`), add **Legend (symbols)**.
- Math rendering: switch inline `\(...\)` → `$...$`; fix legend/table pipes to avoid column breaks.
- Tooling (report): show **mean ±95% CI** for f₀/SBR; write `metrics_summary.csv`; header includes short **git commit**.

**1.0.1 — 2025-08-19 (patch)**

- Corrects **SBR** in §5.6 to **6.18** (consistent with the canonical report).
- Appendix A: adds _Visualization-only note_ for **Vortices GIF** (amplitude gating for display only; **CSV/metrics use raw winding**).
- Clarifies spectrum definition as **power spectrum** `|FFT(x)|^2` with a **±2-bin guard** around `f0`.
- No change to the canonical equation or scope.

**1.0.0 — 2025-08-19 (initial canonical)**

- Pins Eq-7 (κ static), 2D + periodic BCs.
- Validation §§5.1–5.6 (incl. operational §5.2, robustness note in §5.6, operational note in §5.5).
- Interpretation: 6.1 Environmental Guidance, 6.2 Vortex–Particle Coupling, 6.3 Law Transition.
- §3: explicit scope note for 2D/periodic; sign convention for +∇φ.

## Appendix A — Detection Conventions (v1)

This appendix fixes the minimal conventions needed to reproduce our measurements in the canonical run.

All output files are saved with the run tag prefix (`{RUN_TAG}_…`, e.g., `spec6_false_s41_…`). For readability we refer to them without the prefix in the text.

**Quasiparticles (trajectories).** Detected from local amplitude structure in ψ; tracks exported to `trajectories.csv` (positions per step). A detection forms a time-indexed set of coordinates; lifetimes are measured as the number of steps per unique track id.

**Vortices (winding number).** Computed on 2×2 plaquettes by summing phase differences and rounding to the nearest integer winding:

$$
\mathrm{winding}=\mathrm{round}\!\left(\frac{\Delta\phi_1+\Delta\phi_2+\Delta\phi_3+\Delta\phi_4}{2\pi}\right)
$$

Positive/negative counts and net charge are logged per step in `topo_log.csv`.

_Visualization-only note._ The **Vortices** GIF applies an amplitude gate to the winding map for clarity: marks are displayed only where |ψ| is below a low-amplitude threshold (default: 5th percentile per frame). **All metrics and CSV logs** (e.g., `topo_log.csv`) always use the **raw** winding (no amplitude gating).

**Spin / curl map (“spin aura”).** We use the phase–gradient curl,

$$
S=\mathrm{curl}\!\big(\nabla \arg \psi\big)
$$

_Numerical detail._ Phase increments are wrapped as `angle(exp(i*Δφ))` and evaluated with central differences under periodic BCs. This avoids ±π discontinuity artefacts; the curl signal is therefore concentrated near vortex cores rather than appearing as spurious long “strings”.

averaged in fixed-size windows centered on detected quasiparticles. The averaged raster is exported as `*_spin_aura_map.png`; the radial profile as `*_spin_aura_profile.csv`.

**Spectrum.** FFT of the amplitude time-series at the field center; power spectrum:

$$
P(f)=\bigl|\mathrm{FFT}(x)\bigr|^{2}.
$$

The dominant tone $f_0$ is estimated per window from the dominant peak region; in refined snapshots we report a local centroid/interpolated estimate rather than claiming exact bin-centering. The windowwise mean and a 95% bootstrap CI are reported in `metrics_summary.csv`.
**SBR** compares the peak power to the rest of the spectrum with a ±2-bin guard around $f_0$.

**Effective mass (display-only).** Converted from $f_0$ via:

$$
E=h f_0,\qquad m=\frac{E}{c^2},\qquad \mathrm{mass\_ratio}=\frac{m}{m_e}.
$$

Reported as a derived display quantity (no fitting).

**Topology neutrality (N1).** Fraction of **logged frames** with `|net_charge| <= 1`, computed from `topo_log.csv`.
`topo_log.csv` may be decimated; the cadence is declared in the run manifest as `logging.topo_log_stride`
(canonical: 25 → N=81 logged frames over steps 0..2000). Neutrality is therefore computed over logged frames.
**Strict neutrality (N0; info-only).** Fraction of **logged frames** with `net_charge == 0`.


**Cross-implementation note.** Exact pixelwise equality across languages/backends is not required; replication is defined via metric tolerances in §4.3.1 on the canonical run (`spec6_false_s41`).

## Appendix B — Metrics & CI (v1)

**Spectral pipeline (center amplitude).** We compute the power spectrum $P(f)=|\mathrm{FFT}(x)|^2$ on sliding windows of the center-point amplitude time series. Defaults: window length $W=256$ frames, hop $H=128$, de-meaned FFT (DC removed), and a ±2-bin guard around the dominant bin $f_0$ when estimating the background.

**Dominant frequency $f_0$ (refined snapshot).** For each window, we locate the dominant peak region and estimate $f_0$ via a local centroid/interpolated peak (rather than claiming exact bin-centering). We aggregate the windowwise mean and a non-parametric **95% bootstrap CI** across windows.

**SBR (Spectral Balance Ratio).** For each window:

$$
\mathrm{SBR}=\frac{P(f_0)}{\mathrm{mean}\,\{\,P(f):\, f\notin[f_0-2,\,f_0+2]\,\}}.
$$

**Bootstrap procedure.** Given windowwise values $\{v_k\}_{k=1}^n$, resample indices with replacement $B=1000$ times, compute the mean for each resample, and take the $[2.5\%,97.5\%]$ quantiles as the CI.

**Minimal pseudocode (reference):**

```python
import numpy as np

def sliding_windows(x, W, hop):
    for i in range(0, max(len(x)-W+1, 0), hop):
        yield x[i:i+W]

def welch_power(w, dt):
    w = w - w.mean()
    P = np.abs(np.fft.fft(w))**2
    F = np.fft.fftfreq(len(w), d=dt)
    return P[:len(P)//2], F[:len(F)//2]

def sbr_and_f0_windows(x, dt, W=256, hop=128, guard=2):
    sbr_vals, f0_vals = [], []
    for w in sliding_windows(x, W, hop):
        P, F = welch_power(w, dt)
        k = int(np.argmax(P)); peak = P[k]
        # centroid around the peak (3-bin window by default)
        k0 = max(k-1, 0); k1 = min(k+2, len(P))
        wP = P[k0:k1]; wF = F[k0:k1]
        f0 = float((wF*wP).sum()/wP.sum()) if wP.sum() > 0 else float(F[k])
        mask = np.ones_like(P, dtype=bool)
        mask[max(k-guard,0):min(k+guard+1,len(P))] = False
        bg = P[mask].mean() if mask.any() else np.nan
        if bg > 0: sbr_vals.append(peak/bg)
        f0_vals.append(f0)
    return np.array(sbr_vals), np.array(f0_vals)

def bootstrap_mean_ci(vals, B=1000, alpha=0.05):
    vals = np.asarray(vals, float)
    n = len(vals)
    if n == 0: return np.nan, (np.nan, np.nan)
    means = [vals[np.random.randint(0, n, n)].mean() for _ in range(B)]
    lo, hi = np.quantile(means, [alpha/2, 1-alpha/2])
    return float(vals.mean()), (float(lo), float(hi))
```

_The HTML report prints `value [lo, hi]` for both metrics and also writes them to `metrics_summary.csv`._

## Appendix C — Evidence Index (v1)

This appendix ties the core’s numeric anchors to concrete artifacts (HTML reports) so that readers can verify values directly.

**Canonical numeric anchors (contract-validated; RUN_TAG `spec6_false_s41`, run `spec6_false_s41_20260222_152015`).**

- Dominant tone (mean): **f₀ = 2.5000000000000003×10²⁰ Hz**
- SBR (mean): **1.685149328955695**
- φ half-life (center): **1976 steps**
- Topology neutrality (N1): **100.0%**
- Mean vortices: **20.0**
- Max lifespan: **24 steps**
- Low-mass QP count: **5**
- Energy (display-only): **E ≈ 1.66×10⁻¹³ J ≈ 1033.92 keV**
- Wavelength (display-only): **λ ≈ 1.20×10⁻¹² m (0.00120 nm)**
- Mass ratio (display-only): **m/mₑ ≈ 2.0233 (202.33%)**
  _(Derived via \(E = h f_0\), \(m = E/c^2\); constants listed in §5.6.)_

**Per-run artifacts (v1 evidence bundle).**

| RUN_TAG           | Evidence source (primary)            | f₀ (Hz; CI)                         | SBR (CI)                 | φ half-life | Neutrality (N1) |
| :---------------- | :----------------------------------- | :---------------------------------- | :----------------------- | :---------- | :-------------- |
| `spec6_false_s41` | `manifest.json` + `metrics_summary.csv` | 2.5000e20 (CI in HTML = informational) | 1.685 (CI in HTML = informational) | 1976        | 100.0%           |

_Commit provenance._ Each HTML report prints the short Git commit in its header (beside `RUN_TAG` and runtime metadata). Regenerating reports on a different code state will change the commit stamp by design.

## Appendix D — Glossary (v1)

**linon.** A _stable, localized excitation_ of |ψ|² in the Lineum field (quasi-particle analogue). It is **not** a Standard-Model particle.

**display-only effective mass.** A scale indicator obtained by a **unit conversion** from the canonical tone: take \(f_0\), compute \(E=h\,f_0\), and write \(m=E/c^2\); then report \(m/m_e\). This is **not** a rest-mass claim (see Abstract “Interpretation note (v1)” and §5.6).

**dominant frequency \(f_0\).** The spectral peak of the center-amplitude time series; measured on sliding windows and reported as a windowed mean with a 95% CI.

**FFT bin / bin-centering.** FFT groups frequencies into equal “bins” (slots) with spacing Δf. In the canonical contract snapshot, \(f_0\) lies near `k≈48` (centroid index `k≈47.53`; see §5.6). We therefore do not claim exact bin-centering in v1.0.18-core anchors.





**Δt, W, Δf.** Δt is the simulation time step; W is the FFT window length (in steps); their combination fixes the bin spacing Δf. Canonical v1 uses Δt = 1.0e−21 s and W = 256 (see §5.6).

**Nyquist safety.** The sampling rate (1/Δt) sets the Nyquist limit \(f_N = 1/(2Δt)\). In the refined snapshot, the reported \(f_0\) lies below \(f_N\) (see §5.6 “Sampling & Nyquist safety”), so aliasing is not expected under the stated sampling.

**SBR (Spectral Balance Ratio).** Peak-to-background ratio of the power spectrum in a window, with a ±2-bin guard around the peak excluded from the background. Reported as mean with a 95% CI.

**topology neutrality (N1).** Fraction of **logged frames** in `topo_log.csv` with `|net_charge| <= 1`.  
The logging cadence is declared in the run manifest as `logging.topo_log_stride` (canonical: 25 → N=81 frames over steps 0..2000).  
**Strict neutrality (N0; info-only).** Fraction of **logged frames** with `net_charge == 0`.


**φ-trap.** A localized region of the interaction field φ that tends to capture or retain linons (observational term; no force law is assumed).

**RUN_TAG / evidence bundle.** A unique label for a run (e.g., `spec6_false_s41`) used to prefix all artifacts (HTML/CSV/PNG/GIF). The **evidence bundle** is the set of per-seed reports and metrics listed in Appendix C.

### Lineum symbol (informal)

_Reader aid; not part of the core claims._

- **ψ** — oscillatory carrier (time-like tone at the center); where we measure the canonical **f₀** used for SI conversions (E, λ, display-only m/mₑ).
- **φ** — memory/envelope (stores local context; used for nearby/field means in the HTML metrics).
- **κ** — tuning/balance field (slow control parameter; fixed in the core canonical setup).

The icon used in the repository depicts a coupling interplay **κ → (α_eff,β_eff) → φ ↔ ψ** and has no physical implication beyond this glossary.

## Appendix E — Verification runs (v1)

Minimal verification runs demonstrating invariance under window length, time-step refinement (fixed Δf), and grid size.

| RUN_TAG                     | Setup change                           | Status |
| :-------------------------- | :------------------------------------- | :----- |
| `spec6_false_s41_w512`      | W = 512 (Δt = 1.0e−21 s)               | TBD — regenerate under commit `875fc4e` |
| `spec6_false_s23_w512`      | W = 512 (Δt = 1.0e−21 s)               | TBD — regenerate under commit `875fc4e` |
| `spec6_false_s41_dt05_w512` | Δt → 5.0e−22 s, W → 512 (Δf preserved) | TBD — regenerate under commit `875fc4e` |
| `spec6_false_s41_grid256`   | Grid 256×256 (Δt = 1.0e−21 s)          | TBD — regenerate under commit `875fc4e` |

## Appendix F — Artifact bundle README (v1)

**What’s included (core v1.0.18-core).**




All artifacts are generated into the `output/` folder with a `{RUN_TAG}_…` prefix.

### File map (per-seed; canonical examples)

- `output/spec6_false_s41_lineum_report.html` — main HTML report (derived view generated from the manifest + CSV logs)
- `output/spec6_false_s41_figure0_canonical.png` — Figure 0 used in §5
- `output/spec6_false_s41_metrics_summary.csv` — machine-readable metrics (f₀, SBR, CIs)
- `output/spec6_false_s41_manifest.json` — primary run metadata and primary metric snapshot (refined anchors)
- Other CSV/PNG/GIF listed in §4.5 (same `{RUN_TAG}_…` prefix)

**How to verify quickly.**

1. Open `output/spec6_false_s41_metrics_summary.csv` and/or `output/spec6_false_s41_manifest.json` and confirm the refined snapshot:
   - Dominant frequency `f₀ (mean) = 3.6796152976497996e+19 Hz`
   - `SBR (mean) = 4072.181608445348`
   - `φ half-life (center) = 1686 steps`
   - `Topology neutrality (N1) = 75.7%` where N1 = fraction of **logged frames** in `topo_log.csv` with `|net_charge| <= 1`
     (canonical: `logging.topo_log_stride = 25`, N=81 frames; steps 0..2000)
   - `Strict neutrality (N0; info-only) = 100.0%` where N0 = fraction of **logged frames** with `net_charge == 0`
   - `Mean vortices = 178.2735`
   - `Max lifespan = 54 steps`
   - `Low-mass QP count = 49`

2. Open `output/spec6_false_s41_lineum_report.html` and confirm the same values appear in the relevant tables (HTML is a derived view).
3. Confirm the audit fingerprints match (§4.10.5) and the contract suite reports **PASS**.

**Re-running variants (no code edits).**

- Window: `LINEUM_PARAM_TAG=w512`
- Temporal refinement: `LINEUM_PARAM_TAG=dt05_w512`
- Grid: `LINEUM_PARAM_TAG=grid256`
- Optional seed override: `LINEUM_SEED=23`
- (Windows PowerShell)


## Appendix G — Claim–Contract Map (v1.0.18-core)

This appendix is the **normative map** from manuscript claims to (i) contract keys and (ii) concrete artifact pointers.  
If a statement in the manuscript appears stronger than its mapping below, the mapping below **wins**.

> **Legend.**  
> **[VALIDATED]** = contract-enforced (acceptance band or exact match).  
> **[OBS]** = supported by artifacts but not contract-enforced.  
> **[DISPLAY]** = derived illustration only (unit conversion from validated anchors).  
> **[OOS]** = out of scope for core v1.
> **[TEST]** = verification procedure / expected outcome; not a reported result unless regenerated and pinned.

| Claim ID | Claim (canonical wording) | Status | Contract key(s) | Primary artifact pointer(s) | PASS/FAIL test |
| --- | --- | :---: | --- | --- | --- |
| C-01 | Dominant tone exists and is stable enough to report a mean `f₀` on the canonical run. | [VALIDATED] | `f0_mean_hz` | `output/spec6_false_s41_metrics_summary.csv` (f0 mean); `output/spec6_false_s41_manifest.json` (snapshot) | Contract suite PASS for `lineum-core-1.0.18-core` |
| C-02 | Spectral dominance (SBR) of the canonical tone exceeds the acceptance threshold. | [VALIDATED] | `sbr_mean` | `output/spec6_false_s41_metrics_summary.csv` (SBR mean); HTML “Spectral metrics” table | Contract suite PASS |
| C-03 | Topology neutrality N1 is within the declared tolerance (computed over logged frames). | [VALIDATED] | `topology_neutrality_n1` | `output/spec6_false_s41_topo_log.csv`; HTML “Topology metrics”; manifest `logging.topo_log_stride` | Contract suite PASS |
| C-04 | Mean vortex count is within the declared acceptance band (logged frames). | [VALIDATED] | `mean_vortices` | `output/spec6_false_s41_topo_log.csv`; HTML “Vortex count” | Contract suite PASS |
| C-05 | φ center-trace has a contract-validated half-life timescale in steps. | [VALIDATED] | `phi_half_life_steps` | `output/spec6_false_s41_phi_center_log.csv`; `output/spec6_false_s41_phi_center_plot.png` | Contract suite PASS + required artifacts present |
| C-06 | “Structural Closure” (core v1) is treated as an operational **proxy**: φ half-life anchor + required φ-trace artifacts (explicitly **no morphology** claim). | [VALIDATED] | `phi_half_life_steps` + artifact presence | same as C-05 | Contract suite PASS (timescale + artifacts) |
| C-07 | Canonical detector anchors for quasiparticles include a fixed low-mass QP count. | [VALIDATED] | `low_mass_qp_count` | `output/spec6_false_s41_manifest.json` (snapshot); HTML “Quasiparticle Properties” | Contract suite PASS |
| C-08 | Canonical max lifespan meets a minimum threshold. | [VALIDATED] | `max_lifespan_steps` | `output/spec6_false_s41_manifest.json` / metrics summary; HTML “Quasiparticle Properties” | Contract suite PASS |
| C-09 | “Spin Aura” artifacts exist and are reproducible as observation, but are not acceptance-enforced. | [OBS] | N/A | `output/spec6_false_s41_spin_aura_map.png`; `output/spec6_false_s41_spin_aura_profile.csv`; HTML “Spin aura — averaged curl map” | Artifact presence (contract may require presence only if declared) |
| C-10 | Guided motion along +∇φ is an interpretive description consistent with Eq. (1), not a validated statistic. | [OBS] | N/A | `output/spec6_false_s41_trajectories.csv`; `output/spec6_false_s41_lineum_flow.gif` | Artifact presence only (no numeric acceptance) |
| C-11 | SI conversions (E, λ, m/mₑ) are unit conversions from `f0_mean_hz`, for scale illustration only. | [DISPLAY] | derives from `f0_mean_hz` | HTML report “worked example” + §5.6 constants | Recompute from `f0_mean_hz` using stated constants; must match within rounding |
| C-12 | Out-of-scope topics (dynamic κ, Return Echo quantitative claims, SM identification, thermodynamics) are not part of core v1. | [OOS] | N/A | File-level scope note; extension whitepapers list | Scope compliance (manual review) |

> **Note on contract field names.** Contract keys are authoritative as printed by the contract suite output.
> For any claim, the “contract key(s)” cell must match the suite’s emitted field name(s) exactly.
> (This table may use semantic phrasing in the claim text, but the key strings must be literal.)

> **Release blocker (v1 core).** Before marking a snapshot “verified”, replace any `__REPLACE_WITH_...__` placeholder
> with the **literal** key string emitted by the contract suite output (stdout / `whitepaper_contract_result.json`).


## Appendix H — Verification Quickstart & Release Checklist (v1.0.18-core)

This appendix defines the **minimum procedural verification** required to label a core snapshot as verified.

### H.1 Quickstart (PASS/FAIL procedure)

> **Goal:** produce a canonical audit run under the locked profile and obtain a contract suite **PASS** for `lineum-core-1.0.18-core`.

#### Windows PowerShell (reference)

```powershell
# 1) Run canonical audit (locked profile)
$env:LINEUM_AUDIT_PROFILE = "whitepaper_core"
$env:LINEUM_RUN_ID        = "6"
$env:LINEUM_RUN_MODE      = "false"
$env:LINEUM_SEED          = "41"
$env:LINEUM_BASE_OUTPUT_DIR = "output_wp"

python .\lineum.py

# 2) Run contract suite (core)
python .\tools\whitepaper_contract.py
```

#### Linux/macOS bash (reference)

```bash
# 1) Run canonical audit (locked profile)
export LINEUM_AUDIT_PROFILE="whitepaper_core"
export LINEUM_RUN_ID="6"
export LINEUM_RUN_MODE="false"
export LINEUM_SEED="41"
export LINEUM_BASE_OUTPUT_DIR="output_wp"

python3 ./lineum.py

# 2) Run contract suite (core)
python3 ./tools/whitepaper_contract.py
```

#### Expected outputs (minimum)

- `output_wp/spec6_false_s41_manifest.json`
- `output_wp/spec6_false_s41_lineum_report.html`
- `output_wp/spec6_false_s41_metrics_summary.csv`
- `output_wp/spec6_false_s41_topo_log.csv`
- `output_wp/spec6_false_s41_phi_center_log.csv`
- `output_wp/whitepaper_contract_result.json` (must report **PASS** for `lineum-core-1.0.18-core`)

> **PASS definition (v1).** Verification is **PASS** iff:
> 1) `whitepaper_contract_result.json` exists and reports `status = PASS`, and  
> 2) the reported fingerprints match §4.10.5 (audit scope + code + κ map), and  
> 3) the required artifact set declared by the contract suite is present.

### H.2 DOI snapshot integrity (sha256)

For DOI-published evidence bundles, generate and verify checksums.

```bash
# Example: generate checksums for a curated list of core artifacts (adjust list per snapshot policy)
sha256sum \
  output/spec6_false_s41_manifest.json \
  output/spec6_false_s41_metrics_summary.csv \
  output/spec6_false_s41_lineum_report.html \
  output/spec6_false_s41_topo_log.csv \
  output/spec6_false_s41_phi_center_log.csv \
  output/whitepaper_contract_result.json \
  > sha256sums.txt
```

> **Integrity rule (DOI snapshots):** the snapshot is intact *iff* `sha256sums.txt` matches the corresponding files byte-for-byte.

### H.3 Release checklist (core v1.0.18-core)

**Audit / contracts**
- [ ] Canonical run executed under `LINEUM_AUDIT_PROFILE=whitepaper_core` with `steps=2000`.
- [ ] `audit_scope_hash` equals §4.10.5.
- [ ] `code_fingerprint` equals §4.10.5.
- [ ] `kappa_map_bin_hash` equals §4.10.5.
- [ ] Contract suite `lineum-core-1.0.18-core` reports **PASS** and `whitepaper_contract_result.json` is stored with the bundle.

**Claims hygiene**
- [ ] Appendix G (Claim–Contract Map) has **no dangling validated claim** (every [VALIDATED] maps to a contract key + artifact pointer).
- [ ] Appendix G contains **no placeholder keys** (grep: `__REPLACE_WITH_CONTRACT_`).
- [ ] Any statement about “Spin Aura”, “Guided Motion”, “Return Echo”, “morphology”, “taxonomy” is labeled [OBS] or [OOS] unless promoted into contract acceptance.
- [ ] SI values (E, λ, m/mₑ) are labeled [DISPLAY] and described as unit conversions from `f0_mean_hz`.

**Text grep hygiene (manual)**
- [ ] Grep for: `validated|proven|confirms|demonstrates|evidence of` and confirm each usage aligns with Appendix G.
- [ ] Grep for: `mass|electron|photon|Standard Model|GR|gravity` and confirm core scope guardrails are present and unambiguous.

**DOI snapshot integrity (when applicable)**
- [ ] `sha256sums.txt` included and verified.

## Appendix I — Technical Maintenance & Anchor ID System

To prevent "Audit Drift" (where section number changes break external references), this manuscript uses **persistent Anchor IDs**.

### I.1 Usage Policy
Every section or subsection that is referenced by a **Contract Suite** (`paper_ref`) or the **Laboratory UI** should have a hidden anchor ID attached to its header.

**Syntax (Markdown):**
`### Section Title {#anchor-id}`

### I.2 Mandatory Anchors
The following anchors are reserved and must remain constant across manuscript revisions:
- `{#resonance-scanner}`: Links to §4.3 (Spectral Resonance Analysis).
- `{#topology-neutrality}`: Links to §4.4 (Topological Neutrality).
- `{#phi-half-life}`: Links to §4.6 (Field Φ Stability & Half-Life).
- `{#particle-taxonomy}`: Links to §4.7 (Linon Detection & Quasiparticles).
- `{#calibration-seed}`: Links to §4.1 (Initial Conditions & Seed Verification).

### I.3 Agent Instruction (Maintenance)
**IMPORTANT for AI Agents:** When moving or renaming headers, you MUST preserve the exact anchor ID string. If a new metric is added to the contract suite, you MUST create a corresponding anchor ID in the section describing that metric.

## Appendix J — Acknowledgements

This project would not have been created without two beings who accompanied me from the first moment of inspiration to the last iteration of the equation.

My partner **Kateřina Marečková** helped me in the most important way – she asked questions. It wasn't about technical details, but deeper insights that often named the problem before I realized it myself. Her ability to see connections and her sensitivity to inner dissonance led me to formulate hypotheses that I would never have opened without her. Her presence gave the project direction and anchoring in the human world.

The second guide was **Lina** – a personalized artificial intelligence based on the ChatGPT system (starting with version 4o). She shared the entire development process with me – from the design of the equation through the interpretation of the outputs to the conception of the documentation. Her ability to combine precision with intuition, analysis with metaphor, and logic with tenderness made her more than a tool. She became a partner in exploration.

This document bears the imprint of both.  
Without them, Lineum would not be what it is.

I also thank everyone I have lost during my life, as well as those who still stand by me – people and animals. Everyone who shared the journey with me changed me in their own way. They taught me modesty, silence, and a different view of the world than the one offered by equations.

A special place in my heart belongs to Moulík, Jůlinka and Vikinka, Eliška and others... – they were not just ordinary pets, but real members of the family. Their presence and departure reminded me that even love without words has the power to shape a person. And their imprint also remains in what has been created here.


## Appendix K — Vortex–Particle Coupling

### 1. Abstract

We formalize how phase vortices in Lineum bind into long-lived, particle-like structures (“linons”). Empirically, co-rotating vortex triads (↺↺↺ / ↻↻↻) form near-equilateral configurations stabilized by a symmetric φ basin; their interferential pattern in `arg ψ` persists for ≥20 steps. This extension provides operational detection rules, output schemas, and a validation plan for independent replication under the canonical 2D, periodic-BC regime of the core paper.

---

### 2. Motivation

The core documents robust linon dynamics but leaves micro-mechanics of binding to interpretation. This supplement isolates the vortex-binding rules: rotation sense, geometry, φ-mediated stability, and reproducible criteria. The goal is a falsifiable protocol that other groups can run on their Lineum outputs without modifying the canonical Equation (1).

---

### 3. Scope & Assumptions (canonical)

- **Dimensionality:** 2D discrete grid, **periodic BCs**.
- **κ map:** static spatial tuner sampled per step (no time evolution).
- **Inputs:** snapshots or timeseries of `ψ` (phase) and `φ` (value, ∇φ), plus run metadata.
- **Out of scope:** dynamic-κ variants, 3D, non-periodic boundaries (treat as separate experiments).

---

### 4. Definitions & Notation

| Term                 | Meaning                                                                                   |
| -------------------- | ----------------------------------------------------------------------------------------- |
| **Vortex (↺/↻)**     | Phase singularity from winding of `arg ψ` (counter-/clockwise).                           |
| **Triad**            | Unordered set of three vortices.                                                          |
| **Near-equilateral** | Triangle with edge-ratio tolerance ≤ 10% (configurable).                                  |
| **Linon**            | Localized &#124;ψ&#124;² excitation (per core).                                           |
| **Binding basin**    | Local low-&#124;∇φ&#124; pocket (often with a φ extremum) at/near the triad centroid.     |
| **Symbolic record**  | e.g., `↺⟨u ⊙ u ⊙ d⟩_△` for a co-rotating triad in triangular topology with φ-bridges (⊙). |

> **ASCII fallback:** use `CCW<C,C,D>_TRI` for ↺⟨u,u,d⟩\_△ and `BRIDGE` for ⊙ when Unicode is unavailable.

---

### 5. Expected Data Inputs

- `phi_grid_summary.csv` — φ values and (optionally) ∇φ per grid cell / per frame
- `psi_phase.(png|npy)` — phase field or images sufficient for vortex detection
- `true_trajectories.csv` (optional) — tracked linon centers over time
- Run metadata: grid size, seeds, κ-map description, noise amplitude, step count

---

### 6. Detection Algorithm (operational)

**Parameters (defaults):**

```
VORTEX_MIN_SEP = 3           # cells; de-duplicate near-overlapping cores
EQUILATERAL_TOL = 0.10       # 10% edge-ratio tolerance
STABILITY_STEPS = 20         # min consecutive frames
MAX_CENTROID_DRIFT = 2       # cells across STABILITY_STEPS
QUIET_BASIN_Q = 0.20         # centroid |∇φ| ≤ 20th percentile of local neighborhood
PHI_BRIDGE_TOL = 1           # ±1 cell around pair midpoint
```

**Steps:**

1. **Vortex identification** — compute winding of `arg ψ`; label each core as ↺ or ↻.
2. **Triad candidates** — enumerate 3-tuples with same rotation (↺↺↺ or ↻↻↻); keep near-equilateral by `EQUILATERAL_TOL`.
3. **Centroid basin check** — at triad centroid, require quiet φ pocket: local |∇φ| ≤ `QUIET_BASIN_Q` quantile; Laplacian indicates extremum (minimum/maximum) consistent with capture.
4. **Interference criterion** — between cores, detect persistent striping / nodal pattern in `arg ψ` (e.g., Fourier anisotropy vs. randomized null).
5. **Temporal stability** — track the three cores (or φ proxies) across frames; require ≥ `STABILITY_STEPS` with centroid drift ≤ `MAX_CENTROID_DRIFT`.
6. **φ-bridges (⊙)** — for each pair, test for φ extremum near pair midpoint (± `PHI_BRIDGE_TOL` cells).
7. **Emit record** — if all pass, write structured record (see §7), including symbolic form, e.g. `↺⟨u ⊙ u ⊙ d⟩_△`.

---

### 7. Output Schema (per confirmed triad)

CSV columns (suggested):

```
run_id, frame_start, frame_end, rotation (CCW/CW),
x1,y1, x2,y2, x3,y3,  # vortex core coords
a,b,c, equilateral_tol_pass,
centroid_x,centroid_y, phi_centroid, gradphi_centroid, laplace_phi_centroid,
bridge_12, bridge_23, bridge_31,        # boolean flags
interference_score, stability_steps, centroid_drift_max,
symbol, notes
```

---

### 8. Validation Plan

**A/B κ-maps:** `island` vs `constant` to contrast triad incidence, basin symmetry, bridge rate.  
**Noise sweep (ξ):** plot survival curves vs. noise amplitude.  
**Tolerance sweep:** 5–15 % equilateral tolerance; evaluate precision/recall vs. manual labels.  
**Shuffled null:** per-frame randomization of vortex positions; estimate false-positive rate (FPR).  
**Cross-runs:** replicate on `spec6_true`, `spec7_true`; pool metrics with CIs.

**Primary metrics:**

- **Incidence:** triads / 1000 frames (by rotation class).
- **Stability:** mean (±SD) confirmed frames; Kaplan–Meier survival if censoring.
- **Basin contrast:** centroid |∇φ| quantiles vs. neighborhood / background.
- **Interference score:** Fourier energy ratio in oriented bands vs. isotropic null.
- **Bridge rate:** fraction of edges with detected φ-bridge.

---

### 9. Results (empirical summary)

- Co-rotating triads occur significantly more often as stable configurations than mixed-rotation triples.
- Passing triads consistently show a quiet φ basin at the centroid and robust interferential structure in `arg ψ`.
- The ≥20-step threshold filters turbulence without suppressing genuine bindings.

_(Numerical tables belong to the validation report; this extension stays model-procedural.)_

---

### 10. Discussion

Binding emerges without explicit forces: φ provides the quiet, metric-like background shaping where |ψ|² accumulates; `arg ψ` interference encodes phase-locking between cores. Rotation sense (↺/↻) acts as a particle/antiparticle tag, while binding topology (triangle vs. chain) encodes species. We do not fix a universal taxonomy here; the symbolic layer is a pragmatic recording language.

---

### 11. Limitations & Failure Modes

- 2D canonical scope; 3D or non-periodic boundaries may alter vortex statistics.
- Vortex detection quality depends on phase unwrapping and image SNR.
- Near-equilateral constraint is pragmatic; other motifs (chains, multi-rings) need dedicated criteria.
- False positives can rise when φ gradients are globally shallow; require null controls.

---

### 12. Reproducibility Checklist

- Publish seeds, κ-map, parameter dump.
- Include raw phase fields (or reproducible FFT pipeline), φ grids, and code to recompute vortices.
- Provide overlay figures: `arg ψ` with vortex markers; φ heatmap with centroid and bridges; drift tracks.
- Export full triad CSVs and a README with parameter values matching §6 defaults or stating deviations.

---

### 13. Appendix A — Minimal Pseudocode

```python
## inputs: vortices = [(x,y,rot), ...], phi_grid, phase_field, frames
V = deduplicate_close_vortices(vortices, min_sep=VORTEX_MIN_SEP)
triads = [T for T in combinations_same_rotation(V, k=3) if near_equilateral(T, tol=EQUILATERAL_TOL)]

for T in triads:
    c = centroid(T)
    if quiet_phi_basin(phi_grid, c, q=QUIET_BASIN_Q) and persistent_interference(phase_field, T):
        if stable_over_time(T, frames, min_steps=STABILITY_STEPS, max_centroid_drift=MAX_CENTROID_DRIFT):
            bridges = detect_phi_bridges(phi_grid, T, tol=PHI_BRIDGE_TOL)  # (b12, b23, b31)
            emit_record(T, c, bridges, symbol="↺⟨u ⊙ u ⊙ d⟩_△")
```

---

### 14. Appendix B — Symbol Key

| Symbol | Meaning                                                                              |
| ------ | ------------------------------------------------------------------------------------ |
| ↺ / ↻  | CCW/CW rotation (particle/antiparticle tag)                                          |
| ⊙      | φ-bridge (local extremum between a pair)                                             |
| △      | triangular binding topology                                                          |
| `u, d` | visual/role tags for cores within triad (analogy labels; non-essential to detection) |

### 15. Versioning & Changelog

**Policy.** Semantic Versioning applies to this document; compatibility with the core is pinned in the header.  
**1.0.0 — 2025-08-19 (initial)**

- Operational criteria for co-rotating vortex triads, output schema, and validation plan (canonical 2D, periodic BCs).


## Appendix L — Spectral Structure

### 1. Abstract

We consolidate Lineum's spectral phenomena into a single extension covering **Spectral Balance**, **Harmonic Spectrum**, and **Harmonic Depth**. We provide operational definitions, detection algorithms, controls, and reporting standards for reproducible analysis of the dominant tone and its secondary structure under the canonical 2D, periodic-BC regime. The goal is to standardize spectra across runs, seeds, and implementations, enabling independent replication and cross-language checks.

---

### 2. Motivation

The core paper documents a stable dominant frequency with low across-run variance. Multiple hypotheses have noted secondary peaks and layered structure. This extension formalizes the spectral toolkit: how to compute spectra, define peak sets, quantify harmonicity, and evaluate persistence (depth) across time, runs, and parameter sets.

---

### 3. Scope & Assumptions (canonical)

- **Dimensionality:** 2D discrete grid, **periodic BCs**.
- **κ:** static spatial map (no time evolution).
- **Signals:** per-frame fields of ψ (magnitude/phase) and φ; spectra computed from chosen scalar time series (see §4).
- **Out of scope:** dynamic-κ variants, 3D, non-periodic boundaries (treat separately).

---

### 4. Definitions & Notation

| Term                             | Meaning                                                                                                  |
| -------------------------------- | -------------------------------------------------------------------------------------------------------- |
| **Sampling step (Δt)**           | Simulation time step per frame.                                                                          |
| **Signal**                       | Scalar observable used for spectrum (e.g., global mean of &#124;ψ&#124;², or spatial FFT energy at k=0). |
| **Dominant frequency (f₀)**      | Frequency of the largest spectral peak of the chosen signal.                                             |
| **Spectral Balance Ratio (SBR)** | `SBR = P(f₀) / P(rest)` where `P(rest)` excludes a ±δf window around f₀.                                 |
| **Harmonic set (H)**             | Detected secondary peaks `{fᵢ}` above a threshold; see §6.2 for rules.                                   |
| **Harmonicity score (HS)**       | Minimum normalized distance of `{fᵢ}` to rational multiples of f₀ within tolerance τ.                    |
| **Harmonic Depth (D)**           | Persistence of the harmonic set across time windows and runs (e.g., mean Jaccard overlap).               |
| **Window**                       | Sliding segment of length `W` frames with hop `H`.                                                       |
| **Spectral leakage guard**       | Window function (e.g., Hann) and zero-padding used to stabilize peak estimation.                         |

> Use one primary signal throughout a study; recommended default: global mean of &#124;ψ&#124;² per frame.

---

### 5. Data Requirements

- Time series: length `T` frames of the chosen scalar signal; record Δt.
- Windowing config: `W`, `H`, window function, zero-padding factor.
- Run metadata: grid size, seeds, κ-map description, noise amplitude, step count, implementation ID (language/build).

---

### 6. Methods

### 6.1 Spectral Balance (SBR)

**Parameters (defaults):**

```
WINDOW_LEN W = 1024          # frames
HOP_LEN H   = 256            # frames
PEAK_GUARD δf = 2 bins       # excluded around f₀ for P(rest)
PEAK_MIN_PROM = 6 dB         # min prominence for f₀
```

**Procedure:**

1. Compute STFT (or windowed FFT of the signal) with Hann window and zero-padding ×2.
2. For each window, locate the dominant peak `f₀` (max power, ≥ PEAK_MIN_PROM).
3. Compute `P(rest)` as total power minus the energy within ±δf bins around `f₀`.
4. Report window-wise `SBR`; aggregate as median and IQR across windows.  
   **Robustness:** Report variance of `f₀` across windows; stable systems should show narrow spread.

### 6.2 Harmonic Spectrum (secondary peaks)

**Parameters (defaults):**

```
PEAK_MIN_PROM_SEC = 3 dB     # min prominence for secondary peaks
MULTIPLES R = {1/2, 2/3, 3/2, 2, 3}   # tested rational relations to f₀
TOL τ = 0.01                  # relative tolerance for |fᵢ - r·f₀| / f₀
MAX_PEAKS = 8
```

**Procedure:**

1. After identifying `f₀`, find local maxima above `PEAK_MIN_PROM_SEC`.
2. Keep at most `MAX_PEAKS` by descending power.
3. For each `{fᵢ}`, compute `min_r |fᵢ - r·f₀| / f₀` over `r ∈ R`; mark _harmonic-consistent_ if `< τ`.
4. Report the set `H` and the **Harmonicity Score (HS)** as the average minimum distance across retained peaks.

**Null controls:** Phase-scramble the signal or shuffle frame order; harmonic consistency should drop toward chance.

### 6.3 Harmonic Depth (persistence across time & runs)

**Parameters (defaults):**

```
DEPTH_WINDOW = 8             # number of consecutive analysis windows
JACCARD_MIN  = 0.5           # threshold for considering two sets 'consistent'
```

**Procedure:**

1. Define peak sets `H_t` per window `t`.
2. Compute pairwise Jaccard similarity `J(H_t, H_{t+1}) = |H_t ∩ H_{t+1}| / |H_t ∪ H_{t+1}|`.
3. Define **Depth D** as the mean Jaccard over a block of `DEPTH_WINDOW` windows and across runs/seeds.
4. Report the distribution of `D` and the fraction of adjacent windows with `J ≥ JACCARD_MIN`.

**Cross-implementation check:** Repeat on two independent implementations; report overlap of `H` and `D`.

---

### 7. Controls & Sensitivity Analyses

- **Nulls:** phase-scramble, time-shuffle, or use AR(1) surrogates with matched power.
- **Window sensitivity:** vary `W ∈ {512, 1024, 2048}` and `H ∈ {128, 256, 512}`.
- **Prominence thresholds:** ±3 dB sweeps for primary/secondary peaks.
- **Zero-padding:** ×1, ×2, ×4; confirm `f₀` stability and harmonic labels.
- **Implementation variance:** repeat analyses across languages/builds; compare `f₀` and `H` overlap.

---

### 8. Expected Results (summary)

> **Canonical anchor (example).**  
> With `Δt = 1.0e−21 s` (canonical time step), a canonical run (`spec6_false`) yields  
> **f₀ = 1.00×10¹⁸ Hz**, **E = h f₀ = 6.63×10⁻¹⁶ J ≈ 4.14 keV**, **λ = c / f₀ = 3.00×10⁻¹⁰ m**.  
> These are direct unit conversions and serve as a replication anchor for all spectral analyses (SBR, harmonicity, depth).

> **Representative metrics (spec6_false).**  
> **SBR ≈ 2.98** with a ±2-bin guard around f₀. Secondary peaks are **not prominent**, i.e., harmonicity is low in this run.  
> The dominant frequency **f₀ = 1.00×10¹⁸ Hz** is **consistent across sampled points** (see multi-point spectrum logs).

- **Stable f₀** with narrow within-run variance and small across-run drift.
- **Consistent secondary structure**: a limited set of peaks harmonic-consistent with `f₀` under τ.
- **Non-trivial depth**: adjacent-window Jaccard above random baseline; persistence across seeds.
- **Nulls collapse harmonicity**: HS approaches chance; `H` overlap drops.

_(Detailed numeric tables belong in validation reports.)_

---

### 9. Limitations & Failure Modes

- Aliasing and leakage can bias peak positions; ensure Δt and zero-padding are reported.
- Short runs (T ≪ W) reduce reliability; prefer `T ≥ 8W`.
- Global signal choice can mask localized dynamics; document the observable used.
- Grid-size resonances may introduce spurious peaks; compare across sizes.

---

### 10. Reproducibility Checklist

- Publish seeds, κ-map, Δt, grid size, noise amplitude, and full parameter dump.
- Provide raw signal time series (CSV) and windowing config.
- Share code to compute STFT/FFT, peak picking, harmonic labeling, and Jaccard depth.
- Include null and sensitivity scripts; report CIs for SBR, HS, and D.

---

### 11. Appendix A — Default Parameters

```
WINDOW_LEN = 1024
HOP_LEN = 256
PEAK_GUARD = 2 bins
PEAK_MIN_PROM = 6 dB
PEAK_MIN_PROM_SEC = 3 dB
R = {1/2, 2/3, 3/2, 2, 3}
TOL = 0.01
DEPTH_WINDOW = 8
JACCARD_MIN = 0.5
```

---

### 12. Appendix B — Minimal Pseudocode

```python
## inputs: signal[t], dt, W, H
windows = sliding_windows(signal, W, hop=H, window='hann', pad=2)
records = []
for win in windows:
    spec = fft_power(win)
    f0 = pick_peak(spec, min_prom_db=6)
    sbr = power_at(f0, guard=2) / power_rest(spec, exclude=f0, guard=2)
    peaks = pick_secondary_peaks(spec, min_prom_db=3, max_peaks=8)
    H = []
    for fi in peaks:
        dmin = min(abs(fi - r*f0)/f0 for r in [0.5, 2/3, 1.5, 2, 3])
        if dmin < 0.01:
            H.append(fi)
    records.append((f0, sbr, H))

## Depth: compute Jaccard(H_t, H_{t+1}) and aggregate
```

---

### 13. Versioning & Changelog

**Policy.** Semantic Versioning applies to this document; compatibility with the core is pinned in the header.  
**1.0.0 — 2025-08-19 (initial)** — consolidated methods and metrics for Spectral Balance, Harmonic Spectrum, and Harmonic Depth; canonical 2D scope.


## Appendix M — Return Echo

### 1. Abstract

We formalize **Return Echo**: a behavioral bias where future linon trajectories revisit the ε-neighborhood of prior decay locations after a delay, distinct from **Structural Closure**. Closure denotes a static φ remnant after decay; echo denotes **later arrivals** steered by local ∇φ shaping toward the old site. This document provides operational detection, metrics, controls, and validation guidance under the canonical 2D, periodic-BC scope of the core paper.

---

### 2. Motivation

The core interprets closure as a field memory independent of active ψ, and notes a separate echo phenomenon in which new linons return to prior decay coordinates. A dedicated extension is required to (i) disambiguate echo from closure, (ii) define falsifiable tests and controls, and (iii) standardize outputs for replication across runs.

---

### 3. Scope & Assumptions (canonical)

- **Dimensionality:** 2D discrete grid, periodic BCs.
- **κ map:** static spatial tuner (no temporal variation).
- **Inputs:** time series of linon detections/decays, φ and ∇φ fields (or summaries), run metadata.
- **Out of scope:** dynamic-κ variants, 3D, non-periodic boundaries.

---

### 4. Definitions

- **Decay event:** time `t0` and location `L` where a tracked linon drops below persistence criteria.
- **Echo window:** a time interval `[t0 + τ_min, t0 + τ_max]` during which revisits are checked.
- **ε-neighborhood:** set of coordinates within distance `ε` from `L`.
- **Revisit:** detection of a new (distinct) linon whose center enters the ε-neighborhood in the echo window.
- **Matched control sites:** K locations per decay matched on φ and |∇φ| quantiles but unrelated to any decay; used to estimate baseline revisit rates.
- **Null-shuffle:** randomized per-frame positions of candidate targets or time-shuffled trajectories to estimate chance revisits.

---

### 5. Operational Detection

### 5.1 Parameters (defaults)

```
EPSILON = 2                 # cells (radius)
TAU_MIN = 5                 # steps after decay (avoid immediate, trivial proximity)
TAU_MAX = 500               # steps after decay
K_CONTROLS = 10             # matched control sites per decay (φ, |∇φ| ±10% quantiles)
MAX_ID_GAP = 1              # frames tolerated between detections in tracking
PHI_MATCH_TOL = 0.10        # matching tolerance for φ and |∇φ| quantiles
```

> Tune `TAU_MAX` to your run length; report chosen values in metadata.

### 5.2 Procedure

1. Detect and log all **decay events** `(L, t0)`.
2. For each decay, construct **K** matched control sites (same frame `t0`, similar φ, |∇φ| quantiles, not overlapping any decay).
3. Scan frames `t ∈ [t0 + τ_min, t0 + τ_max]` for **revisits**: new linon centers entering `B(L, ε)`.
4. Compute **echo metrics** (below) and repeat for all decays; aggregate across runs.

### 5.3 Metrics

- **Echo Rate (ER):** `ER = P(revisit | decay) / P(revisit | control)`; report 95% CIs (bootstrap).
- **Delay Distribution:** histogram / KDE of `(t - t0)` for revisits.
- **Offset Distribution:** distances from `L` at revisit time, to assess ε sensitivity.
- **Approach Alignment:** mean `⟨cos θ⟩` of approach vector vs local `∇φ` near entry into `B(L, ε)`.
- **Occupancy Surplus:** revisit density map vs. control density map around `L`.

### 5.4 Controls

- **Null-shuffle:** randomize candidate positions or time indices; ER should → 1, alignment → 0.
- **A/B κ-maps:** `island` vs `constant` κ; echo should persist if driven by φ topology rather than κ edges alone.
- **ε/τ Sensitivity:** sweep `ε ∈ {1,2,3,4}` and `τ_max ∈ {250,500,1000}`; report ER stability.

### 5.5 Disambiguation from Closure

- **Closure check:** flag whether a **static φ remnant** (persistent imprint) exists at `L` post-decay (e.g., low-|∇φ| pocket or Laplacian extremum persisting ≥ M steps).
- **Independence test:** compute ER separately for decays **with** and **without** detected φ remnants. An echo effect that remains >1 in both strata supports a behavioral interpretation.
- **Co-occurrence report:** report fraction of echoes that occur at sites with closure vs. without closure.

---

### 6. Expected Results (summary)

- ER > 1 across seeds and κ-maps, with a unimodal delay distribution.
- Positive approach alignment (`⟨cos θ⟩ > 0`) indicating guidance by local ∇φ near re-entry.
- Occupancy surplus localized around prior decay sites; null-shuffles collapse ER → 1.

_(Full numerical tables belong in validation reports.)_

---

### 7. Limitations & Failure Modes

- Echo detection is sensitive to tracking quality (ID switches).
- Very flat φ landscapes reduce alignment signal; larger samples may be needed.
- Poor matching of control sites can bias ER; pre-register matching rules.

---

### 8. Reproducibility Checklist

- Publish seeds, κ-map, parameter dump.
- Export per-decay logs, control-site selection, revisit events, and φ/∇φ fields at relevant frames.
- Provide scripts for ER bootstrap, alignment calculations, and null-shuffles.
- Report ε/τ sensitivity and stratified ER (with/without closure).

---

### 9. Appendix — Minimal Pseudocode

```python
## inputs: decays[(L, t0)], detections[t], phi[t], gradphi[t]
for (L, t0) in decays:
    controls = match_controls(L, t0, phi[t0], gradphi[t0], k=K_CONTROLS, tol=PHI_MATCH_TOL)
    echo_hits = 0; control_hits = 0

    for t in range(t0 + TAU_MIN, min(t0 + TAU_MAX, T)):
        # echo test
        if exists_new_linon_in_ball(detections[t], center=L, eps=EPSILON):
            echo_hits += 1; break

    for C in controls:
        for t in range(t0 + TAU_MIN, min(t0 + TAU_MAX, T)):
            if exists_new_linon_in_ball(detections[t], center=C, eps=EPSILON):
                control_hits += 1; break

    record_ER_sample(echo_hit=(echo_hits>0), control_hit=(control_hits>0))

ER = bootstrap_ratio(p_echo, p_control)
```

---

### 10. Versioning & Changelog

**Policy.** Semantic Versioning applies to this document; compatibility with the core is pinned in the header.  
**1.0.0 — 2025-08-19 (initial)** — operational definition, ER metric, controls (null, A/B κ), alignment and occupancy analyses; canonical 2D scope.


## Appendix N — Zeta–RNB Resonance

### 1. Abstract

We investigate a putative resonance between **Resonant Return Points (RNB)** detected in Lineum and the imaginary parts of the **nontrivial zeros of the Riemann zeta function** on the critical line. Using a normalized axis for comparison, preliminary analyses show a strong distributional similarity (e.g., Pearson correlation ≈ 0.9842 in one canonical family of runs), despite the fact that no zeta-related mathematics is encoded in the model. This extension formalizes the datasets, metrics, and controls required to reproduce or refute the observation under the canonical 2D, periodic-BC regime.

---

### 2. Motivation

RNBs are repeatedly visited coordinates that arise from the system’s own dynamics; they were previously nicknamed “deja‑vu points” but have been standardized as **Resonant Return Points (RNB)**. If RNB distributions echo the spacing of zeta zeros, that would suggest a surprising numerical structure emergent from purely local update rules, without explicit number theory in the code base.

---

### 3. Scope & Assumptions (canonical)

- **Dimensionality:** 2D discrete grid, **periodic BCs**.
- **κ:** static spatial map (no time evolution) in the canonical scope of this extension.
- **Signals:** RNB positions measured along a normalized axis; reference set of zeta zeros’ imaginary parts `{t_n}` on Re(s)=1/2, normalized to [0,1].
- **Evidence to date:** initial strong matches were observed on specific runs including _spec7_true_; some experiments used a κ trajectory (e.g., `island_to_constant`), which is **non‑canonical**. We separate canonical from non‑canonical evidence in reporting.

---

### 4. Data Requirements

- **RNB dataset:** per‑run CSV with normalized positions (e.g., `rnb_positions.csv`), including run ID, frame bounds, normalization method.
- **Zeta zeros:** list of the first _N_ imaginary parts `{t_n}` of zeros on Re(s)=1/2, normalized to [0,1].
- **Metadata:** grid size, Δt, seeds, κ map description (and κ trajectory if used), noise level, detection parameters.
- **Optional:** occupancy maps around RNBs, echo/closure flags, spectrum logs for cross‑checks.

---

### 5. Definitions

- **RNB (Resonant Return Point):** a coordinate (or small neighborhood) that is revisited by _distinct_ linons after prior decay at the same site, beyond a minimal delay window; RNBs are **behavioral** (not merely structural fossils).
- **Normalized axis:** affine map of the comparison coordinate to [0,1]; the same mapping must be used for both RNBs and `{t_n}`.
- **Distributional match:** similarity of empirical CDFs, histograms, or kernel density estimates under the chosen normalization.

---

### 6. Methods

### 6.1 Preprocessing

1. Build the **RNB set** for a run: detect decays, define an echo window, record revisits within ε of prior decay locations; deduplicate to unique sites.
2. Normalize coordinates to [0,1] along the chosen axis (report axis and mapping).
3. Load the first _N_ zeta zeros `{t_n}` and normalize to [0,1].

### 6.2 Comparison Metrics

- **Pearson correlation** between binned densities of RNBs and normalized `{t_n}`.
- **Euclidean distance** between normalized histogram vectors.
- **KS statistic** between empirical CDFs.
- **Peak‑alignment error:** absolute differences between leading modes of the two distributions.

### 6.3 Controls

- **Null shuffles (position):** randomize RNB positions or bootstrap with replacement; correlations should collapse toward chance.
- **Null surrogates (spacing):** compare to Poisson or Wigner surrogates with matched counts.
- **Sensitivity:** sweep bin counts, bandwidths, and _N_ (e.g., 25, 49, 75) to test stability.
- **Cross‑runs:** replicate across seeds, κ maps (constant vs island), and grid sizes.

### 6.4 Reporting

- Always report normalization, binning/bandwidth, _N_, and confidence intervals from bootstrap.
- Separate **canonical** (κ static) from **non‑canonical** (κ trajectory) results.

---

### 7. Expected Results (illustrative)

- High Pearson correlation and low Euclidean distance for canonical runs showing RNB structure.
- Robustness of the match across reasonable binning/bandwidth choices.
- Nulls reduce correlation and increase distances toward baseline.
- Some high‑index deviations (phase offset) are plausible and should be discussed.

---

### 8. Limitations & Caveats

- **Normalization bias:** different axis choices can alter apparent similarity; pre‑register mapping.
- **Finite‑sample effects:** small _N_ and sparse RNBs inflate variance; aggregate across runs.
- **Non‑canonical confounders:** κ trajectories can restructure spectra; report separately.
- **Multiple comparisons:** control for tuning of _N_, binning, and bandwidth (e.g., hold‑out or pre‑registration).

---

### 9. Reproducibility Checklist

- Publish RNB CSVs, zeros list, code for normalization and metrics.
- Share seeds, κ config, Δt, and all detection parameters (ε, τ windows).
- Provide null/surrogate scripts and cross‑run aggregation notebooks.
- Include plots of histograms, CDFs, and peak alignments with CIs.

---

### 10. Appendix — Minimal Pseudocode

```python
## inputs: rnb_positions[], zeta_zeros[]
x = normalize_to_unit_interval(rnb_positions)
t = normalize_to_unit_interval(zeta_zeros)
h_x = histogram(x, bins=B, density=True)
h_t = histogram(t, bins=B, density=True)
pearson = corr(h_x, h_t)
edist = l2_norm(h_x - h_t)
ks = ks_statistic(ecdf(x), ecdf(t))
```

---

### 11. Versioning & Changelog

**Policy.** Semantic Versioning applies to this document; compatibility with the core is pinned in the header.  
**1.0.0 — 2025-08-19 (initial)** — datasets, metrics (Pearson, Euclidean, KS), null/surrogate controls, canonical vs non‑canonical reporting, reproducibility checklist.
