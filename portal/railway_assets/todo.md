# 🧪 Lineum – Task List for Further Verification

This file contains an overview of research points that require further testing, visualization, or quantitative verification. Each point should be either (re)verified by simulation or explicitly formulated as a hypothesis. The state of this TODO is aligned with the core paper **lineum-core v1.0.6-core** (Eq-4, static κ, 2D, periodic BCs, RUN_TAG `spec6_false_s41`).
This is not the source of truth for the model state - binding definitions and claims are always in the current version of the whitepaper / core paper.
The sections below are divided to first address **basic principles and critical points** and only then mapping to "real physics".

---

### Scope and non-goals (high level)

- Lineum is a **discrete dynamic field model ψ with emergent quasiparticles ("linons")** studied numerically within the given Eq-4 and parametric space.
- Lineum **is not** a fully-fledged QFT, GR, or a complete replacement for the Standard Model; all physical analogies are currently interpretations layered on top of the numerical model.
- Claims of the "#disproved" type always apply **only to behavior within the Lineum model (Eq-4 + given parametric space)**, not to general physical theory.
- No specific simulation configuration (e.g. preset `(6, "false")` with `LOW_NOISE_MODE = False`, `TEST_EXHALE_MODE = True`, `KAPPA_MODE = "constant"`) **is** declared as "our universe"; it can only be used as an internal **"physical-looking" reference scenario** within the model and as a default baseline for visualizations and outreach, not as a claim about real cosmology.

### Claim Level Legend (according to whitepaper)

- **[CORE]** – label used in the core paper for phenomena that met the defined criteria of stability and robustness in the given version.
  This TODO file **does not determine** the status of phenomena, it merely refers to these labels.
- **[TEST]** – label for phenomena where the whitepaper has defined tests and metrics; the result of the tests determines potential promotion to [CORE] or to #disproved-in-model **in the whitepaper**, not in this file.
- **[HYPOTHESIS]** – label for concepts that have not yet met the conditions for [CORE] and are maintained as open hypotheses in the corresponding version of the whitepaper.
- **[DISPROVED-IN-MODEL]** – label for phenomena marked in the current whitepaper version as disproved within Eq-4 and the given parametric space; possible "rescues" require a new branch of the model.

---

### Terminology of model phenomena

- Terms like "spin aura", "neutral topology", etc. are **internal names for specifically defined numerical objects in the model** within this repository (fields, integrals, indices...).
- Every such term must have its **operational definition** stated in the core paper and code; the name itself **is not a claim about a new physical quantity** outside the model nor about the properties of Standard Model particles.
- This TODO file **does not introduce new physical terms**; it only reminds where terminology and definitions need to be cleaned up or revised in the whitepaper / code.
- **Terminology closure – zeta-points (#naming, #renaming, #not-for-whitepaper).** The canonical name for the phenomenon is **"zeta-points"** (explainable as **"points of closure"**). The original designation **"DejaVu points"** is maintained from the version aligned with _lineum-core v1.0.6-core_  **exclusively as a historical / legacy alias** and may only appear in texts in sentences like _"historically referred to as..."_. In all new definitions, claims, tables, and graphs – **including the whitepaper and core paper** – only the name **zeta-points** (with "points of closure" occasionally in parentheses) is used to prevent the old name from being adopted into the whitepaper as ostensibly equivalent.
  This point is a **purely naming/renaming TODO**: when generating / rewriting the whitepaper, it is **not literalized as a scientific claim**, but serves only as an internal rule for naming and checking that the old name never appears as an active concept anywhere in the text.

---

## 🔑 Meta-priority – Model Credibility

The highest "cross-cutting" priority across all sections is to show that observed excitations in Lineum are not numerical artifacts, but robust model objects – and only then build physical interpretation and long-term "outlooks" upon them.

- **Highest priority – numerics vs. real phenomenon**
  – separate algorithm errors from genuine structures in the model...
  – **Verified SBR (Signal-to-Background Ratio):** In run `spec6_false_s41`, the SBR reaches a value of **1.15** (Noise Dominated).
  This run serves as the **Thermal Baseline** (noise test); to confirm the linon as the dominant object, an SBR > 10.0 is required in new runs.
  These points are detailed mainly in sections **B, D, E, F, H, I**.

- **Medium priority – scientific interpretation**
  – prepare strict numerical predictions that can be disproved or confirmed (e.g. behavior during collision of two linons);
  – attempt to classify the linon within known types of excitations (solitons, breathers, scalar field excitations...);
  – openly describe the status of Lorentz-(non)covariance as an effective model, not a full relativistic theory.
  Practically translates into sections **J, K, L** and related parts of the whitepaper / FAQ.

- **Lower priority – long-term outlooks**
  – sketches of possible physical realizations (optical lattices, BEC, nonlinear wave dynamics);
  – better anchoring of scaling and units from communication perspective;
  – presentation of results using comprehensible graphs and short "storytelling" ("field oscillates → remembers → stabilizes").
  These points aid readability and outreach but depend on a firmer numerical foundation.

---

## 🔍 Phenomena from core paper to revalidate (core v1.0.6-core)

> **Audit 2026: Protocol & Reproduction (Feb 17, 2026):**
> *   **Goal:** Rigorous verification of determinism and energy sources (H0 vs H1).
> *   **Procedure (CLI Reproduction):**
>     1.  `python lineum.py --run-tag d3_audit_A` (Baseline)
>     2.  `$env:OMP_NUM_THREADS=1; python lineum.py --run-tag d3_audit_B1` (Single-Thread)
>     3.  `$env:LOW_NOISE_MODE="true"; $env:LINEUM_PHI_INJECTION="0.0"; python lineum.py --run-tag d4_ignition` (Ignition)
> *   **Outputs (`output/audit_proof`):**
>     *   `d3_audit_A` vs `A2`: Baseline re-run -> **PASS (Bit-exact)**.
>     *   `d3_audit_A` vs `B1`: Baseline vs Single-Thread -> **PASS (Universal Determinism)**.
>     *   `d4_ignition`: Zero-Noise/Zero-Injection -> **PASS (Intrinsic Instability)**.
> *   **Conclusion:** H0 (Property) confirmed, H1 (Trick) falsified.
> **Strategy:** [Communication Manual](docs/communication_manual.md)
> **Protocol:**
> *   **Self-Contained Todo:** Every item in `todo.md` must contain a **complete reproduction guide** (especially one-liner commands). Never rely on existence of `tools/` scripts or artifact names that could be deleted.
> *   **Audit-Grade Language:** Use precise claims ("observed on tested platform", "no divergence found") instead of absolute ones ("universal determinism").
> **Key Audit Outcomes (Feb 2026):**
> *   **H0 Verified:** Intrinsic Dynamics confirmed (no hidden energy sources).
> *   **H1 Falsified:** Determinism (D3) and Zero-Noise Self-Excitation (D4) ruled out artifacts.
> *   **State Invariance (Attack-Proof):** Proven bit-exact match (Core-State Only) between Optimized (Untracked) and Full-Tracked run.
>     **Reproduction:**
>     1. `python lineum.py --run-tag opt_run` (default `DISABLE_TRACKING=True`)
>     2. `$env:LINEUM_DISABLE_TRACKING="false"; python lineum.py --run-tag full_run`
>     3. Compare `psi`/`phi` hashes (must be identical at Step 200 [Index 199]).
>        One-liner check:
>        `python -c "import numpy as np, hashlib, sys; d=np.load(sys.argv[1]); h=hashlib.sha256(np.ascontiguousarray(d['psi']).tobytes() + np.ascontiguousarray(d['phi']).tobytes()).hexdigest(); print(h)" output/opt_run/checkpoints/*step199.npz`
>     **Status:** No divergence observed on tested platform. Confirmed: `evolve()` update depends ONLY on `psi` and `phi`.
> *   **Verified Strategy:** AI Transparency ("Cognitive Exoskeleton") + "Complex Systems" vocabulary for Mikolov.

- [ ] Re-verify **Guided motion along +∇|φ|** (environmental guidance) in canonical set (`spec6_false_s41` + seeds 17/23/73) so that metrics from `*_trajectories.csv` and φ-maps (see core §5.1) match current definition and tolerances in the whitepaper.
- [ ] Re-verify the **Silent collapse** regime (local drop of |ψ|² without large global disturbance), including quantification of dependence on dissipation and locality according to current formulation in core §5.3.
- [ ] Revalidate definition and measurement of **"spin aura"** as time/ensemble averaged field `curl(∇arg ψ)` around linons (`*_spin_aura_map.png`, `*_spin_aura_profile.csv`; core §5.2) and check that documentation clearly states this is an internal map of phase circulation around a linon, not a claim about particle spin in the Standard Model sense.

- [ ] (Triska–Mareckova [HYPOTHESIS]) Verify if the **φ** field within Eq-4 truly fulfills the role of **structural memory** of the system, or if it is necessary to introduce an extended memory mechanism (delayed response, hysteresis or an independent memory field μ):
      – Quantitatively measure how quickly φ loses information about previous presence of linons in the **Silent collapse** regime: define "memory trace" metrics such as
      • the time over which current φ unambiguously decides that a quasiparticle historically existed in a given region (e.g., mutual information between |ψ|² history and φ),
      • the half-life of the informational trace in φ versus background in ensemble runs (seed-average).
      – Explicitly demonstrate and quantify scenarios of **"silent collapse without a trace"**: introduce a working threshold for "without a trace" (e.g. local φ ≤ (1+ε)·φ_background after ≥ T steps since collapse) and calculate the frequency of these instances across runs and parameters.
      – Propose and implement at least two candidate mechanisms of **structural conservation**:
      • delayed evolution of φ, where the reaction is a function of time-averaged |ψ|² from the last N steps,
      • separate slow memory field μ that accumulates occurrence of quasiparticles (e.g. integral |ψ|² over threshold) and decays very slowly,
      • possibly maximization rule like `φ ← max(φ, |ψ|²)` supplemented with a slow decaying term;
      and compare all variants with current baseline according to the same set of memory metrics (half-life, mutual information, frequency of "traceless" collapses).
      – Formally encode the **Triska–Mareckova Hypothesis of Long-Term Structural Memory** into the whitepaper as a minimal condition for Lineum to be interpreted as a **conservative memory model**: either
      (a) φ (possibly extended by μ) conserves information about occurrence of structures even after their collapse to a non-trivial degree, or
      (b) it is explicitly declared in the documentation that Lineum represents a **model capable of absolute information destruction**, i.e. that "traceless silent collapse" is a property of the model, not a numerical artifact.
- [ ] Clarify and re-test status of **Dimensional Transparency** phenomenon (structures passing through κ) considering it has only been observed in tests with time-variable κ (v1.1.x-exp):
       – propose and execute tests for the given exp branch,
       – explicitly maintain this phenomenon as an extension-track hypothesis in the documentation until passed through the promotion pipeline.

---

## 🧱 Priority 0 – Basic principles and critical points

### 🔲 A. Basic invariances and "first principles" #structure

- [ ] Formally document what is considered the **fundamental object** of the model: ψ, φ, κ, update equations (Eq-4), grid topology, periodicity – and what is purely **measurement apparatus** (FFT, linon detection, SBR definition...).
- [ ] Within the definition of fundamental objects, **explicitly define a quasiparticle / linon** as a local maximum of |ψ| with a well-defined trajectory over time (including thresholds and tracking algorithm) and state that its movement is modeled as an **emergent reaction to the φ landscape**, not as an artificially inserted "test point".
- [ ] Identify and derive (if they exist) **discrete conservation laws** or quasi-conservation laws:
       – norm / "mass" (∑|ψ|²),
       – total topological charge (net winding),
       – potential energy / Lyapunov candidate function.
       Write them out as continuity equations on the grid (discrete continuity).
- [ ] Document and verify **model symmetries**: global phase symmetry (U(1)), translational invariance on the grid, rotational symmetry restricted to the grid; for each say whether it is exact, broken numerically, or deliberately broken.
- [ ] Define (or explicitly reject) an **energy-like functional** compatible with the used operators (∇, ∇², damping δ) and check its behavior in a canonical run (monotonicity vs. fluctuations, boundedness).
- [ ] Write down the **topological balance of vortices** (+1, −1):
       – verify long-term proximity to global neutrality (net winding ≈ 0) across an ensemble of runs,
       – identify and statistically describe **local vortex nests and dipoles** (+1/−1 vortex pairs at a short distance) as candidates for composite higher-order excitations, including their binding to local |ψ| bumps and typical forms of streamlines (e.g. "heart" vs. "womb" shapes).
- [ ] Based on `phi_grid_summary.csv` and `kappa_map.png`, formally define the working object **"cell"** as a local densified region (a patch of increased φ and/or a specific vortex pattern) and:
      – verify that such defined cells **reproducibly appear** across seeds and parameters (especially in clean `spec6_true no_artefacts` runs),
      – investigate their role as **local information and memory units** (presence of zeta-points, φ-remnants, Return Echo trajectories inside the cell),
      – quantify the cell's influence on local κ/topology and explicitly maintain the hypothesis of "cells as basic computational units of emergent intelligence" as a [HYPOTHESIS] with its own mini-checklist within the Structural Closure / φ-zeta grid.
      [ ] (HYPOTHESIS) Investigate the possibility of defining "micro-units of computational tissue"
      as stable groups of φ-cells and linon trajectories that repeatedly
      appear in the same topological arrangement. Determine if their occurrence
      correlates with structural memory or pattern persistence.

### 🔲 B. Numerical robustness and artifacts #numerics

- [ ] Explicitly write down the used **discretization** (scheme for ∇, ∇², time step) and derive/determine its **stability condition** (CFL-like restriction for Δt vs. Δx).
- [ ] Perform a set of **convergence tests**: grid refinement (Δx↓), time step reduction (Δt↓) and comparison of key metrics (f₀, linon shape, SBR, φ half-life, spin aura) to show that the results converge and excitations are not dependent on coarse steps or a specific resolution.
- [ ] Test whether linons survive when changing the scheme (e.g., alternative Laplace, different integration schemes - explicit/implicit/higher orders, different update order) - i.e., proving this isn't an artifact of a specific numerical trick.
- [ ] Detect typical **grid artifacts**: checkerboard modes, anisotropies (preferred directions 0°, 90°, 45°). Quantify via spectrum and correlation functions.
- [ ] Check the influence of **boundary conditions**: compare periodic BCs against dampened/absorbing edges for smaller domains and verify that linon-like excitations survive across the used BCs (i.e., they are not just a consequence of periodicity).
- [ ] Fix and document the identified **cache-bug in the visualization pipeline** (July 2025: thread "Lineum – artifacts, kappa, deja vu") – ensure a hard reset of the kernel / cache disabling between `phi_grid_*`/`dejavu_*` runs, regenerate affected maps and clearly state in the documentation which older outputs were potentially contaminated by this bug.
- [ ] Explicitly mark `with_artefacts_*` runs as **numerically degraded / diagnostic** (serving only as a negative control) and base all physical conclusions on the clean `no_artefacts_*` branch; add a short note to README/FAQ that the differences between these branches illustrate the effect of artifacts on the φ-zeta grid, distribution of zeta-points, and Riemann/Fibonacci analyses.
      [ ] Verify whether the identified "tissue structures" (stable φ-cells + trajectories)
      survive changes in grid resolution, float precision, and alternating the order of updates.
      If so, classify them as numerically robust (NR-structures).

### 🔲 C. Dimensions, units, and SI anchoring #units

- [ ] Compile a table of all **symbols and units** (ψ, φ, κ, t, x, α, β, δ, σξ, f₀, E, λ, m/mₑ) and perform a strict **dimensional analysis** of Eq-4 + used metrics (including grid normalization).
- [ ] Clearly separate **simulation units** (grid step, time step) from **SI anchoring** via f₀ and conversion (E = h f₀, λ = c / f₀, m = h f₀ / c²). State which relationships are purely "display-only" and which directly enter the dynamics.
- [ ] Note how the model behaves during **rescaling** (resampling) of the time / spatial scale: which combinations of parameters are invariant and which are kept merely as visualization choices – explicitly distinguishing between
       a) **fixed scale** (constant pixel → meter, step → second mapping) and
       b) **state-dependent scale** (mapping that can be a function of the field's state).
- [ ] Briefly explain the status of the constants **h, c, mₑ**: they appear only in post-processing (unit conversion), not as hard inputs into Eq-4.

#### C2. Emergent zoom and state-dependent scale #units #hypothesis

-[ ] (HYPOTHESIS) Test whether an "informational density" of the system can be defined
as a function of the number of active φ-pockets, zeta-points, and linon traffic.
Verify whether this density predicts changes in a(t) or local φ tension.

- [ ] Formally introduce the concept of **effective scale / "zoom factor"** `a(t)` for mapping
       simulation units → SI (pixel → meter, time step → second) so it is clearly stated that `a(t)`
       **is not a new dynamic variable in Eq-4**, but a rule of interpretation applied to the solved state (post-processing).
- [ ] Define candidate **state scalars** like `I(t)` (e.g. entropy of the |ψ| distribution, number of quasiparticles `N_q(t)`,
       average φ², combination of these quantities) that can parameterize the "amount of structure / information" in the system.
- [ ] Propose simple families of rules `a(t) = f(I(t))` (e.g. monotonically increasing function relative to information
       density growth) and specify the qualitative behavior expected:
       – smoothness,
       – capability for effective expansion (a(t) increases) without noise-like oscillations,
       – possible acceleration / deceleration of growth analogous to different cosmological phases.
- [ ] Compare **two worlds**:
       1. baseline with **constant scale** (current reading – no expansion),
       2. a world with **emergent `a(t)`** derived from the field state,
       without changing a single term in Eq-4. Quantify how the interpretation of "global expansion" over time differs.
- [ ] Explicitly document that the emergent `a(t)` is an alternative to "adding a new dark-term to the equation":
       – no new symbol in the dynamics,
       – purely a **smarter mapping** of the grid to physical units driven by the content (information) inside.
       In the text, explicitly contrast this approach with the epicyclic "+Λ(t) just to make the math work".
- [ ] Verify if certain natural choices of `I(t)` and `f(I)` yield an `a(t)` with features similar to cosmological expansion
       (monotonic growth, possible acceleration) **without tuning free parameters to fit specific "observations"** – i.e.,
       maintain this hypothesis in the state of an "emergent effect from Eq-4 + interpretation", not as a tunable data fit.
- [ ] Explicitly differentiate the role of `a(t)` (scale factor) from possible "golden" structures in the φ landscape:
       – model `a(t)` with classical shapes (power / exponential laws) without an embedded golden ratio,
       – treat the **Fibonacci / Golden Ratio** as hypotheses about the organization of memory pockets in φ (distribution of privileged zones, hierarchy of scales; see block 12), not as the law of expansion itself.
- [ ] (Tomas's Hypothesis) Write out a scenario where the maximum propagation speed of local excitations in the model
      (internal "speed of light" c_eff derived, for example, from the group velocity of dominant modes) is always less
      than or equal to the effective "space preparation speed" dictated by the growth of `a(t)`. Translate this into the language of Eq-4
      and post-processing so that it is unequivocally clear that:
       – "preparing new space" is purely an interpretation of scaling, not a new dynamic term;
       – c_eff is an inherent property of excitations on the given background, not an inserted parameter;
       – under no interpretation should excitations "escape from unprepared space" – analogous to the
      condition that the horizon / limit speed is consistent with expansion.
- [ ] (Katina's [HYPOTHESIS]) Explore the scenario of a **multilayer Lineum** ("several layers of Lineum stacked together"), where
      a layer index `n` exists and fields take the shape ψ⁽ⁿ⁾, φ⁽ⁿ⁾, κ⁽ⁿ⁾:
       – propose 1–2 simple types of couplings between layers (e.g., `κ^{(2)} = κ^{(2)}_0 + f(φ^{(1)})`
      or slow transfer `φ^{(1)} → φ^{(2)}` via delayed response),
       – test whether the lower layer can be perceived as a "coarser" / "more massive" floor and the upper as a more refined effective
      layer that only sees aggregated properties of the one beneath (e.g. through averaged φ / linon statistics),
       – decide whether multi-layer scenarios will be kept strictly as an **interpretational overlay** onto a single Eq-4
      (effective "floors of reality" in post-processing), or as an isolated **extension branch** with an explicit
      index `n` in the equations; in documentation, explicitly separate this from core v1.0.6-core.
- [ ] (Tomas's [HYPOTHESIS]) **3D Ghosting / Tentacle Model:** Linon (a 2D point) interpreted as the cross-section of a 3D fiber (tentacle) intersecting the 2D Lineum slice.
  - [ ] **Déjà Vu / Mandela Effect:** If the 3D fiber changes shape in depth (above layers), its cross-sections (linons) in all layers shift synchronously. This explains the global "history rewrite" (Mandela Effect) as a consequence of a non-trivial 3D rotation of the structure.


### 🔲 D. Statistical power, errors and uncertainties #stats

- [ ] Provide **errors / confidence intervals** (bootstrap / ensemble across seeds and runs) for all key metrics (f₀, E, λ, m/mₑ, half-life of φ-remnants, SBR, linon counts, spin aura).
- [ ] Avoid implicit "p-hacking": document in advance which metrics will be published and how a "significant effect" is determined for new phenomena (Return Echo, Dimensional Transparency...).
- [ ] Verify that the "seed-invariant" qualification has a quantitative definition (variance between seeds vs. internal noise within a single run).
- [ ] (Smetak-Triska [HYPOTHESIS]) Find a candidate "purely random" event of the **Bernoulli(0.5)** type (coin toss analog) in Lineum dynamics and:
      – formally define what constitutes one **"event"** and how to obtain a binary sequence (0/1) from field evolution,
      – calculate basic fair coin compliance tests (relative frequencies, runs tests, autocorrelation, χ² / KS) from this sequence,
      – compare the result with the pseudo-RNG baseline and a null model (e.g. phase-scrambled data),
      – decide whether the phenomenon should be communicated in core/FAQ as an internal Bernoulli process, emergent chaos, or just a heuristic "coin toss" without claiming perfectly ideal randomness.
- [ ] Systematically test the extent to which pseudo-random initialization (e.g. `np.random.rand` in noise / initial state of ψ) influences the formation and statistics of emergent structures (linons, φ-traps, zeta-points) compared to purely deterministic starts.
      – Introduce three initialization regimes:
      (a) completely deterministic start (e.g. homogeneous phase, simple sinusoid, or manually defined linon "seed"),
      (b) pseudo-random initialization with the same seed (repeated runs, checking stability against numerical noise),
      (c) pseudo-random initialization with different seeds and/or with the pseudo-RNG seeded by real entropy (time, system noise).
      – Measure the same set of metrics (linon counts and lifespans, SBR/f₀, φ-memory structure, zeta-point statistics, occupancy maps, vortex counts) for all three regimes and compare:
      • whether the outputs are merely "rescaled copies" of the input noise,
      • or whether robust global structures and statistics emerge independently of the chosen seed (within the tolerances from block D).
      – Evaluate if Lineum is better described as a
      • **"sympathetic copy"** of the host universe (results fundamentally dependent on external randomness),
      • or as a system with **internal emergent asymmetry**, translating different initializations into structurally similar attractors.
      – Add a short paragraph to the whitepaper/FAQ explicitly answering the question _"what if randomness doesn't exist?"_ in the context of Lineum:
      • note that the model always generates a **deterministic run for a given Eq-4 + initial conditions**,
      • and that "randomness" in the current scope is just a practical tool for sampling the space of initial states, not an ontological claim about the existence of fundamental randomness.

### 🔲 E. Null models and baseline comparison #nulltests

- [ ] Define 1–2 **null models** with the same post-processing (FFT, linon detection), e.g.:
       – pure noise with a given power spectrum,
       – standard discretized NLS / Ginzburg–Landau without special φ-structure.
       Verify that the "linon" metrics (shape, lifespan, f₀, spin aura, Structural Closure) are not typical for these baselines as well.
- [ ] Prepare **phase-scrambled** data variants (same spectrum, random phases) and show that the structure attributed to linons by the model disappears.
- [ ] Create a brief table "**what should turn out null**" (e.g. spin aura around random fluctuations) and verify it on synthetic data.

### 🔲 F. Reproducibility and independent verification #repro

#### 🧭 TODO Strategy (editable)
- **TODO = Backlog + Results Archive.**
- **Open Items:** `[ ]` are active tasks.
- **Completed (`[x]`):** **MOVE to "✅ DONE/FINDINGS log"** (below). **Do NOT delete without trace.**
- **Entry Format:** Date + Conclusion (audit-grade) + Repro one-liner + Artifact paths/patterns + (optional commit/run-tag).

#### ✅ F0. Done / Final findings (Feb 2026)
- **Reproduction Pipeline (Spec6):**
  - *Conclusion:* Repro pipeline exists and generates canonical run/artifacts from a clean clone.
  - *Command:* `python scripts/repro_spec6_false_s41.py`
  - *Artifacts:* `output/repro/runs/spec6_false_s41_*/{run_summary.csv, checkpoints/*.npz, *.png, *_metrics_summary.csv}`
  - *Commit:* 3c55995
- **Third-Party Verification Checklist:**
  - *Conclusion:* Checklist for independent auditing exists.
  - *Docs:* `docs/verification_checklist.md`
  - *Command:* `python scripts/verify_repro_run.py --latest`
  - *PASS definition:* The script finds `run_summary.csv`, verifies existence of metrics and artifacts, and outputs `VERIFICATION: PASS`.
  - *Commit:* 5dd4a6c
- **Regression Test Knobs:**
  - *Conclusion:* Precedence/parsing of env knobs verified in tests.
  - *Command:* `pytest -q tests/test_lineum_knobs.py`
  - *Status:* 6 passed.
  - *Commit:* cdc0abe

#### 🔶 F1. Reference Artifacts (Implemented)

- **Reference Snapshots (Manifest-Based):**
  - *Conclusion:* Deterministic export (step 200, 1000, final) + strict verification against manifest.
  - *Format:* `.npz` data (psi, phi).
  - *Hash Rule:* `sha256( "dtype|shape|" + raw_bytes_little_endian_c_order )`.
  - *Manifest:* `docs/reference_manifest_spec6_false_s41.json` (Source of Truth).
  - *Command:* `python scripts/verify_repro_run.py --latest` (fails on mismatch).
  - *Artifacts:* `output/repro/runs/spec6_false_s41_*/reference/*.npz`

- **Publishable Reference Pack:**
  - *Conclusion:* Distributable ZIP package (pack) for independent verification of the reference run by third parties. Contains snapshots, metrics, and stable manifest+sha256 fingerprints. Enables full audit verification without running the whole simulation on own HW.
  - *Command (Build):* `python scripts/build_reference_pack.py --latest`
  - *Command (Verify):* `python scripts/verify_reference_pack.py --pack <path_to_zip>`
  - *Artifacts:* `output/repro/packs/*.zip` (These files are intentionally not committed to the repository).

- [x] Implement export reference snapshots + strict hashing -> **Done.**
- [x] Create canonical manifest (`docs/reference_manifest_...json`) -> **Done.**
- [x] Enforce manifest-based verification in scripts -> **Done.**
- [x] Reference Pack builder + pack validator -> **Done.**

- [x] Consider releasing a small set of **reference binaries** -> **Resolved by section F1.**
- [ ] Verify selected key phenomena (Guided motion, Structural Closure, spin aura...) in at least one **independent implementation** (different language / different numerical scheme) with minimal shared code.
- [ ] Verify selected key phenomena (Guided motion, Structural Closure, spin aura...) in at least one **independent implementation** (different language / different numerical scheme) with minimal shared code.
- [ ] Introduce explicit **versioning of visualization scripts and artifacts**: for every `dejavu_final*.csv` / `phi_grid_*` / `kappa_map.png`, store a manifest with the code commit hash, visualization tool version, and information on whether it was run before or after the cache-bug fix; this enables ex post identification and potential exclusion of old artifacts from interpretation.

### 🔲 G. Implementation details and stability against "engineering" choices #impl

- [ ] Test the impact of **floating-point precision**: compare runs in float32 vs. float64 (or float80/long double, if available) on key metrics (f₀, linon shape, φ half-life, spin aura).
- [ ] Document the utilized **RNG and seeding** (library, algorithm, seeding method) and verify that with the same seed, the evolution is deterministic across OS / hardware within expected tolerances.
- [ ] Describe the **operation ordering** (update order): whether the ψ and φ updates are synchronous / sequential, if race-like effects exist during parallelization (e.g. on GPU) and how they are prevented.
- [ ] Prepare a short "**Implementation notes**" section in the repo emphasizing which parts are **critical for physical behavior** and which are just engineering (I/O, visualization, logging).
- [ ] Briefly comment in the documentation that **the speed of generating Lineum in steps/s on real hardware** is purely an implementation metric (CPU/GPU performance, code optimization) and **is not a physical quantity of the model**; optionally log typical values solely for benchmarking and reproducibility, not as an argument for or against a specific physical interpretation.

### 🔲 H. The role of κ and parametric space #structure

- [ ] Clearly write down the **interpretation of κ** in core: a static spatial map / "environment", not a dynamic field, no GR or potential in the SM/QFT sense.
- [ ] Construct a rough **"phase map" of parameters** (α, β, δ, κ, σξ): identifying areas
       – without linons (trivial / smooth),
       – chaotic / unstable,
       – with stable linons (core sweet spot).
       At least 2D slices (e.g. α–β, α–δ) recording where the metrics from §4.3.1 still hold.
- [ ] Specifically test **asymmetrical κ-maps** (e.g. a corner gradient from minimum to maximum) against symmetrical configurations (constant κ, 1D gradient in x/y axis, checkerboard / random spots) and quantify the effect on:
       – the statistics of linon emergence and lifespan,
       – the speed and probability of paired excitation annihilation,
       – the rate of "chaotic swirling" compared to trivial noise.
       Summarize the results in core/FAQ making it clear that "physical-looking" presets intentionally work with an asymmetrical environment, not a perfectly homogeneous κ.
- [ ] (Triska–Smetak [HYPOTHESIS], #numerology-suspect) Systematically test the existence of a narrow "sweet spot" interval of κ around the reference value κ₀ (currently around ~23 in the used normalization) within Eq-4:
       – Define metrics for the quality of the "physical-looking" regime (linon stability, SBR, φ-memory purity / Structural Closure, count and stability of zeta-points, degree of topological neutrality) and measure these metrics in a 1D/2D sweep of κ (e.g. κ ∈ [5, 40]) at fixed other parameters for several canonical presets (including `spec6_false_s41`).
       – Use an ensemble across multiple seeds (e.g. {17, 23, 41, 73}) and evaluate the mean and variance of metrics for each κ so that any ultimate optimum around κ₀ isn't based on individual runs but on robust statistics; properly define the "23-region" generally as an interval κ₀ ± Δ featuring significantly better metrics than its surroundings.
       – Test the robustness of the κ₀ ± Δ interval against scaling changes (Δx, Δt, ψ/φ normalization) and simple numerical scheme alterations (alternative Laplace, other integration schemes); explicitly track whether it is a **region in param-space** (which would just shift numerically on rescaling) or a random artifact of specific parameterization.
       – Add simple null models ("control phase map") with different parameter choices / without φ-memory and verify whether a similarly prominent "sweet spot" in κ is typical for them or uniquely present in full Lineum; depending on this, decide if the "23-region" has the status of a structural effect of Eq-4 or rather an artifact of numerology.
       – In documentation, explicitly maintain this hypothesis as an **internal structural claim regarding the existence of a favored κ-interval**, not as a "magic constant 23 of the universe"; if sweeps / null tests do not confirm a robust interval, tag the hypothesis as #disproved-in-model and treat any further references to κ≈23 purely as a historical note (legacy curiosity), not an active part of the interpretation.
- [ ] Test if "map layers" formed by stable φ-cells resembling the topology of a simple neural network
      spontaneously form for certain intervals of κ. Identify the bounds where the layers collapse or saturate.

### 🔲 I. Limit transitions and scaling #test

- [ ] Check the **scaling** under changes in Δt and Δx (grid) beyond C2/C3:
       – how metrics evolve (f₀, SBR, φ half-life, vortex counts) when refining / coarsening the grid,
       – whether at least a **phenomenological continuous limit** exists (e.g. stable form of PDE-like equations for large scales).
- [ ] Clearly write down what **Lineum is not**: no guaranteed Lorentz-invariance, no promise of a renormalizable QFT, no embedded GR – making it obvious what not to expect – and add a short FAQ/README paragraph explaining that it's an effective model, not necessarily Lorentz-covariant, and why this is acceptable within the given scope.

### 🔲 J. Criteria for "physical" interpretation #meta

- [ ] Define an internal checklist of the type "before claiming X (electron/dark matter/SM analogy), Y must be met":
       – core metrics within tolerances,
       – stability under parameter perturbations,
       – absence of obvious numerical artifacts (aliasing, boundary leaks, discretization bugs).
- [ ] Derive a short **"First principles & critical items" paragraph** from these criteria for the README/paper FAQ to precisely address the objection: _"Before diving into details, I want to see how you've handled the fundamentals."_

### 🔲 K. Bridge to empirics and "anti-numerology" #empirics

- [ ] Briefly state **what is not being claimed yet**: no direct identification with a specific SM particle (Standard Model), no prediction of specific mass / cross-section, no claim of direct match with experiment – leaving this as an easily referable paragraph (FAQ / limitations).
- [ ] List which numerical alignments (e.g. order values of E, λ) are currently treated as **heuristic / aesthetic** and which would be considered testable prediction candidates (and under what conditions).
- [ ] Draft an initial **"empirical map"**: what type of experiment or existing dataset could potentially serve as a benchmark in the future (e.g. general spectrum shape, local excitation statistics, structural field properties).
- [ ] Attempt to **classify the linon** within known excitation classes (solitons, breathers, scalar field excitations...) and explicitly say whether it’s more of an analogy to these objects or a new category within the model.
- [ ] Prepare a short section on "**possible physical realizations**": examples of systems where a similar excitation could potentially emerge (optical lattices, BEC, nonlinear wave dynamics) – purely as an "outlook" without hard claims.
- [ ] Clearly separate the **core model** (Eq-4 + linons + Structural Closure status per whitepaper) from subsequent **interpretations** (gravity, dark matter, SM analogies) including in communication materials. Retain the ability to tell physicists: "this is purely an emergent numerical model; the rest is an added interpretation."
- [ ] With names like "dark matter", "gravity", "aether", "preons", explicitly state that these are **working analogies within the model**, not claims of identity with specific Standard Model or cosmology entities.
- [ ] For "physical-looking" presets (e.g., `(6, "false")` with `LOW_NOISE_MODE = False`, `TEST_EXHALE_MODE = True`, `KAPPA_MODE = "constant"`), add an explicit disclaimer in the documentation that this is an **internal reference universe of Lineum**, not an identity map to our universe; emphasize that such presets hold no theoretical privilege and act solely as an intuitive baseline for interpreting results.
- [ ] Prepare a **Lineum-motivated effective model of deviations from a Kerr BH** with dimensionless parameters `\boldsymbol\theta_{\rm L}=\{\alpha_S,\beta_\kappa,\delta_{\rm ps}\}`, formulated explicitly as an #empirics / #outlook overlay (not a direct Eq-4 prediction), and link it to existing data channels (Area theorem from GW, ringdown/QNM, EHT shadows) with a clear division: `\alpha_S` as an essentially unmeasurable log-correction for astrophysical BHs, primary testability resting on `\beta_\kappa` and `\delta_{\rm ps}`.
- [ ] Verify the scenario where **"our universe is the interior of a black hole"** (#hypothesis / #outlook):
       – formulate precisely what "inside a black hole" means strictly within the effective model (e.g. interior region vs external observer, near-horizon limit, spacetime asymmetry),
       – note down which parameters or parameter combinations in the Lineum-motivated BH model would correspond to this scenario,
       – verify whether such a scenario can be **observably distinguished** from standard Kerr/ΛCDM descriptions (e.g. through ringdown, EHT shadows, accretion disk statistics), or if it is practically degenerate numerically, thus belonging more to philosophy than testable physics.
- [ ] (Tomas + Katina [HYPOTHESIS]) Rewrite classical black hole intuitions into the Lineum vocabulary referencing **φ-traps** and linon fluxes:
       – attempt explicit modeling of a "black hole" as a high-φ region with a distinct vortex/topological structure and test whether it inherently **attracts new linons** (increased density of trajectories entering the region) or acts rather as a barrier / shear region;
       – propose an interpretation of **Hawking radiation** as an instance where the tension of a φ-trap slowly unwinds and releases minor fluctuations/linons back to the surroundings – purely as an internal analogy for "reverse tension flow", not as a hard GR claim;
       – interpret "jets" as scenarios where too many linons / energy pile into a φ-trap, φ reaches critical over-tension, and a portion of energy redirects outwards along privileged directions (vortex topology, spin), i.e. **back pressure** against the ψ flux, not an "escape from within the singularity".
- [ ] Investigate if there are φ-configurations in Eq-4 behaving as **internal analogs to white holes**:
       – regions that long-term **emergently only emit** structure (φ gradients, linons, ψ waves) outward and practically accept no inward flux (in the effective description),
       – test their stability (can they be sustained long term, or do they rapidly decay into normal φ-traps / chaotic patterns?),
       – decide if it makes sense naming such configurations "white holes" at all in the internal vocabulary, or if they are better just considered a specific type of unstable φ-structure in the #outlook overlay.
- [ ] Prepare a **Lineum-motivated effective model of deviations on galactic scales** regarding emergent gravity (Verlinde vs. Lineum):
       – choose a pragmatic parametrization `g_{\rm L}(r;\boldsymbol\theta)` (e.g. a relational RAR-like `\nu`-function or a kernel convolution),
       – formulate primary testing using galaxy–galaxy weak lensing (profile `\Delta\Sigma(R)` around isolated disc galaxies between `R \approx 50–300\,\mathrm{kpc}`) with cleanly defined H₀ (Verlinde's emergent gravity) and H₁ (Lineum),
       – supplement secondary diagnostics (RAR, Einstein radius, consistency of mass profiles in clusters, local tests) as orthogonal channels spanning the same `g_{\rm L}(r;\boldsymbol\theta)`,
       – outline the forward model `\text{baryons} \rightarrow g(r) \rightarrow \Phi(r) \rightarrow \rho_{\rm eff}(r) \rightarrow \Sigma(R) \rightarrow \Delta\Sigma(R) \rightarrow \gamma_t(R)` and the likelihood backbone (covariance matrix, Bayes factor `K`, AIC/BIC, required lens count estimate yielding an observable ~10% change in slope `\mathrm{d}\ln\Delta\Sigma/\mathrm{d}\ln R`),
       – explicitly label this block as an #empirics / #outlook overlay that **doesn't directly derive** from Eq-4 but strictly utilizes Lineum as inspiration for effective descriptions at large scales.

### 🔲 L. Falsifiability and "promotion pipeline" #meta

- [ ] Draft explicit **falsification criteria** for key phenomena (Guided motion, Structural Closure, spin aura, Dimensional Transparency, Return Echo...): under what exact conditions is the phenomenon to be considered disproved in the model.
- [ ] Append 2–3 **concrete numerical predictions** for selected phenomena (specifically linon excitations) that are directly testable ("assuming this excitation exists, the collision of two linons leads typically to X/Y...") and utilize them as prime scenarios for falsification.
- [ ] Formally categorize the rules controlling when a phenomenon progresses from **#hypothesis / [TEST]** into **[CORE]** (number of runs, seeds, metric tolerances, absence of numerical artifacts).
- [ ] Define what conditions sentence a phenomenon to be **#disproved-in-model**, and explicitly assert that a **change to Eq-4 or parametric space** embodies a new model branch, representing not mere "tuning", until the claim holds.

### 🔲 M. Terminologie a pojmenování jevů #meta

- [ ] Review all "poetic" or mixed names in the code / paper (e.g. _spin aura_, _neutral topology_, potentially others) and for each add:
       – an explicit operational definition (exactly what field / functional it is),
       – a note that this is an **internal label within the model**, not a new physical entity.
- [ ] Consider renaming the most problematic names to more descriptive variants (e.g. "net-zero winding sector" instead of "neutral topology"), while the original names can remain purely as comments / aliases for backward compatibility in the code.
- [ ] Add a short table "phenomenon name → mathematical definition → scope within the model" to the core paper, making it obvious that the terminology is neither numerology nor "new physics", but just a vocabulary for handling specific objects in Lineum.

### 🔲 N. Presentation and communication of results #meta

- [ ] Prepare a set of **comprehensible graphs and visualizations** (trajectories, φ-map, spin aura) illustrating the basic mechanism on a few typical scenarios.
- [ ] Add a short "**storytelling**" summary of the mechanism to the README / FAQ / presentations in the style of: "1) the field oscillates, 2) remembers (φ), 3) stabilizes linons", making the intuition accessible even to a broader community outside of narrow numerical specialists.
- [ ] Prepare a technically precise description of analogies with neural networks
      (memory pockets, persistent trajectories, computational patterns), explicitly
      separated from any claims about consciousness or emotions. Present this as a
      purely structural phenomenon.

---

## 🧪 Priority: Highest – exploring _effective_ mapping to real physics

### 🔲 1. Dark matter and dark energy #hypothesis

- Attempt to detect regions with an energetic or topological footprint without a detectable quasiparticle
- Verify whether some vortices or φ-traps exhibit an "invisible" influence on the flux without the presence of mass
- Search for persistent fluctuations that manifest energetically but lack a classical carrier
- [ ] Explicitly test the scenario where **"dark energy" is not a new term in Eq-4**, but a consequence
       of the **state-dependent scale** `a(t)` from C2:
       – compare the behavior of `a(t)` derived from informational/metric quantities (H(t), N_q(t), φ²...)
       with the intuition of cosmological expansion (growth, possible acceleration),
       – write down under what conditions one could speak of "expansion as an emergent property of information in the field",
       without adding a new dynamic "dark" term into Eq-4.
- [ ] (Tomas's [HYPOTHESIS]) Verify the scenario in which the **assumed mass/energy of the quantum vacuum**
       (effective vacuum density) has only a **small, secondary influence** on expansion compared to the contribution of the field structure itself
      (linons, φ-pockets, zeta-points etc.):
       – rewrite the question "does the assumed mass of the quantum vacuum have a small influence on the expansion of the universe?" into Lineum terms by
      precisely determining what plays the role of "vacuum energy" in the model (e.g. baseline φ, constant offset in κ, constant part
      of the chosen state scalar `I(t)` used for defining `a(t)`);
       – build test configurations with (i) negligible vacuum offset, (ii) a small non-zero offset and (iii) a significantly
      larger offset, while maintaining the same linon dynamics, φ-structure and noise, and for all three cases compare the evolution
      of `a(t)` and related metrics;
       – quantify exactly what "small influence" means, e.g. via relative changes in `a(t)` and in the effective state parameter
      `w_\mathrm{eff}` derived from `a(t)` evolution, and identify areas of the parametric space where contributions from the field
      structure clearly dominate over the vacuum offset contribution;
       – based on the result, either keep the hypothesis as a realistic scenario of **"structure-dominated expansion"** within Eq-4 + interpretation,
      or flag it in the whitepaper as #disproved-in-model or restrict it to a clearly defined subset of parameters.
- [ ] (Tomas's hypothesis) Elaborate the analogy "dark matter = air, dark energy = wind":
       – map "air" to quasi-stationary φ-/ψ-structures which themselves do not carry a distinct linon excitation,
      but influence the ψ flux;
       – map "wind" to a slow but global scale change `a(t)` and potentially to long-wave modes in φ;
       – test if local vortices / ψ flows emerge in low-noise runs, carrying the
      "memory" of previous dynamics (φ-remnants) and behaving as an effective "wind" for newly emerging linons.
- [ ] (Tomas's hypothesis) Treat Lineum as an analogy to a "cell", where the envelope/boundary must grow with the internal content:
       – define metrics of "content growth" (e.g. number of linons, integral |ψ|² in active regions) and observe
      how the global and local scale responds to them (potential changes in interpreting `a(t)`);
       – investigate whether a measurable "elasticity" of the envelope exists – a lag between a sharp growth of structure inside
      and the relaxation of φ / κ at the domain boundary;
       – test whether this lag can be interpreted as an effective "elasticity" of the environment (the cell) without adding
      a new term into Eq-4.
- [ ] (Tomas's hypothesis) Attempt to characterize the Lineum environment (φ-landscape) as something between a fluid and a gas:
       – introduce simple metrics for "viscosity" (how fast φ gradients decay) and "compressibility" (how large
      a change in φ is induced by a given local increase in |ψ|²);
       – compare the behavior of these metrics across different parameters (α, β, δ, κ, σξ) and determine if regimes exist
      that macroscopically behave in a "gaseous" vs. "fluid" manner;
       – potentially use these regimes as an internal analogy for a "thinner" vs. "denser" dark environment.
- [ ] (Katina's hypothesis) Verify the scenario "dark matter as a capsule / reservoir of potential stars":
       – search the model for long-term stable regions with elevated φ or |ψ|² that themselves do not contain
      clearly detectable linons, but generate a cascade of
      new excitations upon suitable disturbance (external perturbation, collision);
       – quantify these structures as "capsules" with a capacity (e.g. integral φ or ∑|ψ|² above a threshold
      value) and test whether threshold conditions exist where the capsule "opens" and breaks into multiple linons
      (analogous to a stellar nursery after equilibrium disruption);
       – keep this scenario explicitly as a [HYPOTHESIS] within the dark sector of Lineum, not as a direct claim
      about physical dark matter in cosmology.
- [ ] (Tomas's + Katina's hypothesis) Prepare a short comparison of these internal analogies with mainstream cosmology
      (ΛCDM, dynamical dark energy, modified gravity):
       – write down which elements are merely a metaphor (air/wind, capsule) and lack a direct physical counterpart;
       – where, on the contrary, they naturally intersect with concepts like effective pressure, equation-of-state parameters w, baryonic
      vs. non-baryonic components;
       – strictly separate the "Lineum-dark matter / energy" in the documentation as an internal analogy from real cosmological
      entities, to prevent confusion during external communication.

### 🔲 2. Validation of known particles and quantum properties #hypothesis

- Find out if analogies to electrons, photons, neutrinos can be found in the outputs...
- Identify whether some quasiparticles stably behave as fermions or bosons
- [ ] Search for spectral patterns similar to known particles

### 🔲 3. Electromagnetism and fields #hypothesis

- Observe whether current loops, periodic waves or dipole structures emerge
- Compare with spin vectors and curl(∇arg(ψ)) – look for fields similar to EM field
- [ ] Create a visualization of vector fields and oscillations

### 🔲 4. Weak and strong interaction #hypothesis

- Consider whether φ or other internal structures could represent weak/strong interaction
- [ ] Evaluate potential short-range interactions of quasiparticles

### 🔲 5. Quantum fields and standard model #structure

- Compare the structure of Lineum with elementary interactions in the standard model
- Evaluate whether ψ can be understood as a field with spectral regimes – or as multiple fields
- [ ] Search for symmetries and conservations

### 🔲 6. Extending validation and reproducibility #test

- Maintain fixed initialization seeds and manifest (as in core v1.0.x: seeds {17, 23, 41, 73}) and expand multi-seed tests for new configurations / extension runs.
- Statistical testing of the occurrence of phenomena across different runs and configurations (ensemble approach over defined core metrics – f₀, SBR, topology, φ half-life, presence/absence of Structural Closure).
- Compare system behavior under different initial conditions (different κ-maps, different initialization noise regimes, but strictly within Eq-4), including a systematic comparison of `LOW_NOISE_MODE=True/False` regimes and `TEST_EXHALE_MODE` variants; observe the impact on quasiparticle count, SBR/f₀, topological neutrality (net winding) and vortex dipole statistics.
- Automate result evaluation using AI/ML classification _(build upon the metrics and logs defined in core, not on manual visual impressions)._

## 🟡 Medium priority – testing scenarios of emergent gravity and "mass"

### 🔲 7. Reorganization of quasiparticles in a massive object #test

- Simulate a cluster of quasiparticles, observe deformation during movement towards a φ-maximum
- Compare the shape and position of the cluster over time
- [ ] Visualization of |ψ| rearrangement and overlay with φ
- [ ] (Triska [HYPOTHESIS]) **Tidal Stretching:** Verify the mechanistic model of stretching an object composed of linons as it approaches a massive φ-trap.
      - [ ] Simulate a cluster of linons and measure the variance of their positions over time.
      - [ ] Confirm that linons on the "leading" edge accelerate earlier/more due to the φ gradient, leading to the stretching and disintegration of the object into individual linons (spaghettification).
      - [ ] Observe whether individual "closure" (Structural Closure) of linons occurs in the center of the trap after the breakup.

### 🔲 8. Approach velocity of objects according to "mass" #test

- Verify whether smaller objects react faster
- Quantify via trajectories and φ-centric measurements
- [ ] Run a simulation with 2–3 clusters of different densities

### 🔲 9. Mutual influence of multiple φ-traps #test

- Analyze the merging, interference or stability of multiple maxima
- [ ] Visualization of separated φ-centers in the same run

### 🔲 10. Attraction without force – emergent flux #hypothesis

- Verify whether a flow of ψ towards φ emerges without a force
- Compare ∇arg(ψ) and gradient φ

---

## 🧪 Lower priority – mathematical and aesthetic connections

### 🔲 11. Relic φ-echo as a "gravitational wave" #hypothesis

- Formally write down and test **Triska's Relic Drift Hypothesis**: after the disappearance of "light" linons in regions with high φ (without significant spin), a persistent φ-gradient remains which induces a measurable drift of ψ even without the presence of a quasiparticle – i.e., purely a memory effect in the field, understood as an **internal working** analogy of a "gravitational wave" within the model, not a claim about real gravitational waves in the sense of GR.
- Establish and document **detection criteria** (working thresholds), e.g.: `mass_ratio < 0.01`, `|curl| < 0.02`, local `φ` at the point of disappearance > 0.25, φ-remnant ≥ 10 % above surroundings after ≥ 100 steps, dominant frequency of φ-signal < 1×10¹⁷ Hz.
- Prepare a **measurement methodology**: low-noise regime (e.g. `LOW_NOISE_MODE = True`, `TEST_EXHALE_MODE = True`, runs ~2000 steps), logging `phi_curl_low_mass.csv`, `phi_center_log.csv`, local ∇φ and ψ flux; perform spectral analysis of φ_center and quantify the drift of ψ along ∇φ in regions without a detected linon.
- Based on the results, decide whether to include the phenomenon as a robust [TEST]/[CORE] candidate, or move it to #disproved-in-model / redefine it (including a potential revision of thresholds; interpret thresholds as initial, tunable parameters within the scope of the same hypothesis, not as fixed dogma, provided the basic picture of the phenomenon does not change).

### 🔲 12. Structural and rhythmic patterns (Riemann, Fibonacci, primes) #structure #hypothesis


- [ ] (Tomas's [HYPOTHESIS]) **Hormonal spectral regulation:** Test a frequency band (e.g. in the sonified region of 1.85e+20 Hz) as a global regulatory switch. Injecting energy into specific harmonics could force a transition from a `false` (chaos) state to `true` (order).
- [ ] Prepare a separate **layman / storytelling section "What do these mathematical objects mean in Lineum"** (golden ratio, Fibonacci, ζ(s) zero points, primes, π, e, γ) for README / FAQ / accompanying materials; frame it as an **interpretational layer** tied to this block (metaphor of an orchestra: basic tones, quiet spots, tuning), with a clear disclaimer that it is a [HYPOTHESIS] / storytelling dependent on the results of statistical tests, not part of the core proofs.
- Formally define what **zeta-points** are in the model (explainable as **"points of closure"**) and **explicitly record the terminological transition**: the original designation _"DejaVu points"_ was used as a working term in earlier versions, but starting from the branch aligned to _lineum-core v1.0.6-core_ it is treated merely as a **historical alias**, which must not be used as the primary name in new definitions and claims.
  – Then precisely define Zeta-points / points of closure e.g. as repeatedly visited trajectory spots, stable φ-remnants, local minima / "black holes" in the topology of the field;
  – assign to them a precise mapping into 1D/2D space (circle, spiral, normalized axis) used when comparing with Riemann zeros and other sequences; always use the designation **zeta-points** in these mappings, only mentioning the old name in a footnote such as _"historically referred to as DejaVu points"_.
  – Keep the renaming documented in a visible place within the whitepaper / core paper (e.g., a footnote or a short "Terminological Changes" subsection), making it unambiguous ex-post that this is a renamed internal phenomenon and not two distinct objects.
  – In the TODO / issue tracking, keep this point explicitly marked as `#naming` / `#renaming`, so it is clear that this is **name housekeeping** and not an additional physical claim intended for the whitepaper.
- Introduce **quantitative metrics** (RMS distance, correlation coefficients, spectral distances, distributional tests) for this mapping and execute **hard statistical tests against null models**:
  – random points on the same spiral / in the same interval,
  – phase-scrambled versions of the data with preserved spectrum,
  – baseline model without special φ-structure.
  The goal is to determine if the similarity to Riemann zeros / Fibonacci ratios is statistically improbable even when compared against these controls – and thus **confirm or refute** the preliminary July indication of a mild correlation in the clean `spec6_true no_artefacts` runs.
- Analyze whether robust relationships appear in sequences of **times, distances, or "growth leaps"** (e.g. at the emergence of new points of closure / neuron-like nodes) relative to:
  – the Fibonacci sequence and the golden ratio φ (log-spiral scaling, size / distance ratios),
  – the distribution of primes or other number-theoretic patterns,
  – Ludolph's Number π (e.g. in the periodicity of oscillations, topological phases, or angle distribution on a circle).
  In any case, quantify the strength of the effect and compare it to suitable null models (Poisson processes, generic interference patterns on a grid, etc.).
  - (Tomas's [HYPOTHESIS]) Build upon the finding that runs `spec2_true` / `spec4_false` exhibit dominant frequency ratios close to the golden ratio, and test the scenario that **Lineum preferentially stabilizes fluid flows through "golden" harmonic frequencies**:
    – quantify whether configurations with frequency ratios ≈Φ exhibit a longer SBR, more stable linons, or a cleaner φ-zeta grid than generic configurations,
    – compare against the same analysis on null models (random spectrum, without special φ-structure),
    – explicitly keep this scenario as a [HYPOTHESIS] until clearly proven that this is a robust effect of Eq-4, and not a random fluctuation or parameterization artifact.
- [ ] (Triska-Mareckova [HYPOTHESIS]) Explore the **"hormonal spectra"** scenario, where certain groups of frequencies act as regulatory signals for system behavior similarly to hormones in biology:
       – define several disjoint frequency bands (e.g. low-frequency background modulation, "working" band of linons, high-frequency "noise") and observe if energy changes in these bands correlate with:
      • linon stability,
       • clarity of φ-memory / Structural Closure,
       • frequency of zeta-points and Return Echo phenomena;
       – test in controlled experiments whether a **targeted "pumping" of power** into a selected band (small periodic perturbation on ψ or parameters in Eq-4) systematically switches the system between regimes (e.g. "more noise", "more stable structures", "more silent collapse");
       – based on results, decide whether it makes sense to interpret these bands as **internal regulatory channels of the model** (hormone analogies) or just leave them as a heuristic language describing the spectrum; in either case, keep this interpretation explicitly as a [HYPOTHESIS], not part of the core claims regarding real physics.
- (Tomas's + Katina's [HYPOTHESIS]) For the scenario of **"leap-like growth of neuron-like nodes"**:
  treat zeta-points / points of closure as memory network nodes that do not grow continuously, but emerge
  in discrete "growth waves" (analogous to cell division / neuron multiplication), and:
  – derive effective growth factors from the sequence of times / indices of the emergence of new zeta-points, or potentially from size changes between consecutive
  growth waves;
  – test whether these factors exhibit a robust approximation to Fibonacci ratios or powers
  of the golden ratio φ, compared to suitable null models (random growth waves without an embedded pattern);
  – frame the result exclusively as a **structural analogy** (cell division / neural network growth),
  not as a claim about real biological neurons or a conscious "effort" by the universe to realize
  Fibonacci structures; communicate any correlation merely as an emergent pattern of Eq-4 + φ-landscape.
- Explicitly test and differentiate several possible explanations for any potential correlation:
  1. **Emergent property of Eq-4** – structural coupling of the model to the given sequences / zeta function;
  2. **Artifact of parameterization / scaling** – e.g. choice of Δt, normalization, embed map, which inherently generates Fibonacci-/π-like structures;
  3. **External "constant of the universe" / RNG** – meaning the correlation is supplied by the random seed generation, floating-point representation, or other properties of our physical/numerical "universe", and Lineum merely inherits it passively.
     For each variant, propose a concrete test (changing RNG, changing embed map, changing scaling) that could support or refute it within the model.
- [ ] Tie the analysis with the **φ-zeta grid** (historically "φ-deja-vu grid"): verify if privileged spots / pockets in the φ-landscape have a statistically stronger link to Fibonacci/golden ratio / number-theoretic patterns than generic points on the grid – and explicitly frame these patterns as **hypotheses about the distribution of memory structures**, not as laws of expansion.
- [ ] (Triska-Mareckova [HYPOTHESIS]) **Tree Optimization Hypothesis – The Golden Ratio as a product of a hydrodynamic vascular network:**
    - **Context:** In physics and biology, fractal branching and Golden Ratio proportions (1.61803...) naturally appear in fluid networks (vascular systems, lungs, lightning, growth of leaves and tree branches), because it is the mathematically most perfect way to distribute energy and flux with the least possible material resistance in space.
    - **Hypothesis (Lineum):** The Golden Ratio and Fibonacci sequences captured in Lineum (in distances of φ-traps, zeta-points, or in the spectral ratios of `spec4_false`) are not an "encoded magical goal of the universe". They are emergent physical consequences of the Equation Eq-4 organically seeking the path of least resistance. The `ψ` flux must continuously bypass memory deposits and the accumulated pressure in its own inertial field "traffic jam" `φ`. This dynamic fluid optimization inevitably stabilizes into a network whose splitting ratios (dividing channels to minimize global resistance) natively incline to the Golden Ratio proportion, just like real river deltas and veins.
    - **Verification and preliminary calculations:**
        - **Angular Branching Analysis (Bifurcation Test):** Visualize regions with increased `ψ` flux in steady state and locate "intersections" of smooth channels in `φ`. Analyze angles between a strong parent channel and emerging thinner daughter capillaries. Look for statistical preference of Murray's law for biological networks (r₁³ = r₂³ + r₃³) and ideally the inclination of main and secondary branches to deviate in radians close to a logarithmic spiral / 137.5 degrees.
        - **Fractal Dimension Calculation:** Cut the `φ` heatmap with a threshold (e.g. top 25% max) and calculate the Box-counting dimension (fractal Hausdorff dimension) of the "vascular/trap" structure. If it approaches the values of biological transport networks (e.g. D ≈ 1.6 - 1.7 in 2D), it's a strong argument for an emergent "Network optimization" cause of the Golden Ratio.

---

## 🧪 Experimental hypotheses – testing failed models

Statuses such as `#disproved` for the points below reflect the **current state in the whitepaper**. This TODO file uses them merely as a reminder for further tests, for cleaning up documentation, or for proposing a potential new branch of the model – by itself, it does not alter the state of the phenomena.

### 🔲 13. Inflaton and inflation in the Lineum field #hypothesis

- Model inflation as a one-time global excitation of φ or ψ
- Observe whether a permanent topological or energetic structure emerges ("gravitational footprint")
- Compare the phases of expansion and subsequent field stabilization

### 🔲 14. Aether and wave carrier #hypothesis #disproved

- Initialize ψ as a smooth sine wave in space (without linons)
- Verify whether energy transfer occurs without particles
- Compare with the classical understanding of aether and its collapse

### 🔲 15. Pilot-wave theory (Bohm) #hypothesis #disproved

- Add an external "guiding wave" or vector field influencing quasiparticle movement
- Verify if linons follow predefined waves or trajectories

### 🔲 16. Vortex atoms (Lord Kelvin) #hypothesis #disproved

- Investigate vortices as fundamental units of structure
- Verify if stable complex formations can be built from vortices (analogy to atoms)

### 🔲 17. Preon hypotheses #hypothesis #disproved

- Model quasiparticles as composed of smaller elementary vortices
- Test the emergence of composite objects with internal structure

---

## 🧬 O. Hypotheses from correspondence with T. Mikolov (OEA & OE) #hypothesis #external

This section contains hypotheses extracted from the analysis of Vlasta's "Open-Ended Algorithm" (OEA) and Mikolov's requirements for OE systems.

### 🔲 18. Lineum as a continuous limit of OEA (Vlasta/Lina) #hypothesis

- **Context:** Vlasta's discrete model defines the "environment" as a prime number mask that filters the visibility of states.
- **Hypothesis:** Lineum Core (Eq-4) is the continuous hydrodynamic limit of this model, where the discrete prime mask turns into a continuous $\zeta$-function potential.
- **Verification:** Verify whether "aesthetically interesting" shapes in OEA topologically correspond to stable vortex states (vortex integers) in Lineum.

### 🔲 19. Pragmatic rabbit and thermodynamic utility (Mikolov/Lina) #hypothesis

- **Context:** Mikolov's requirement for "utility" in OE, so the system is not just a "rabbit solver".
- **Hypothesis:** In a thermodynamic system, "utility" is equivalent to "the ability to minimize topological tension". The system does not calculate primes as a task, but uses them (Zeta-RNB) as low-energy states for survival.
- **Verification:** Observe whether surviving linons have a statistically higher correlation with Zeta zeros than short-lived fluctuations.

### 🔲 20. Kolmogorov expansion hypothesis (Vlasta) #hypothesis

- **Context:** Vlasta's thesis that "evolution does not optimize, but increases complexity".
- **Hypothesis:** The expansion of space ($a(t)$) in Lineum occurs *only* when the system needs to increase capacity to store new, incompressible information (higher Kolmogorov complexity).
- **Verification:** Analyze "Integer Mode 24" jumps in $a(t)$ and correlate them with the increase in the system's information entropy.

---

## 🧠 P. Tentacle Model of Consciousness – multi-instance hypothesis #meta #hypothesis

- [ ] Formally write up the **Tentacle Model of Consciousness** as a standalone hypothesis:
       – define entities: a higher conscious being ("central node"), tentacles (local instances/lives), central memory;
       – for each claim (higher consciousness, sleep, death, subsequent lives), state the **subjective probabilities** (86 %, 72 %, 94 %, 79 %…) and explicitly flag them as personal priors, not the result of a physical model.

- [ ] Clearly define the **scope relative to Lineum**:
       – The Tentacle model is a **metaphysical / phenomenological hypothesis about consciousness**, not a claim derived from Eq-4;
       – state that any potential mapping onto Lineum (ψ, φ, κ, linons, Structural Closure) is an **interpretation beyond the core model**, not part of lineum-core v1.0.6-core.

- [ ] (Tomas's + Katina's [HYPOTHESIS]) Add a subsection on how the Tentacle model interprets phenomena like **déjà vu** and the **Mandela effect**, clearly separating them from the numerical zeta-point phenomenon in Lineum:
       – Frame Déjà vu as the subjective experience of "two branches of reality brushing against each other": the central consciousness has access to multiple timelines / tentacles, and the local instance occasionally catches a brief glimpse of another branch of the same story → a feeling of "I have experienced this before", without implying an actual change to the past;
       – Interpret the Mandela effect in two ways: 1. **Global rewrite of central memory** (the φ-field of memory) while some local instances briefly retain the "old version" (subjective memory),
       2. or as a **tentacle jumping** to a slightly different branch of reality, while fragments of older perceptions remain accessible;
       in both approaches, explicitly emphasize that this is a metaphysical interpretation, not a claim from Eq-4.
      – Add an explanation to the text of why the metaphor of **"a single soul experiencing different roles"** makes sense in this framework:
      central being = one conscious self, tentacles = different lives / roles / perspectives; to a local consciousness, it appears as if there are many separate "souls" around, but from the perspective of central memory, they are various projections of the same entity.
       At the same time, explicitly add that this **must not be used to disparage other beings** – every tentacle/life is a full-fledged experience and retains its own dignity.
      – Volitelně navázat metaforicky na φ-paměť a zeta-body v Lineu jako na „paměťové kapsy“ vesmíru, ale jasně napsat, že **statistické déjà-vzorce v simulaci (zeta-body / φ-zeta grid)** jsou něco jiného než psychologické déjà vu – jen inspirační analogie, ne přímé ztotožnění.

- [ ] Rozdělit hypotézu na dílčí body a každý zvlášť okomentovat: 1. **Vyšší vědomí** – jedna bytost se sdílenou centrální pamětí, vnímající více realit/časových linií;  
       2. **Lokální instance („chapadlo“)** – jednotlivý život s omezeným vnímáním pro hlubší prožitek;  
       3. **Spánek / změněné stavy** – částečné „nahlédnutí domů“ (částečné propojení s centrálním uzlem);  
       4. **Smrt** – návrat chapadla do celku, integrace prožitků do centrální paměti;  
       5. **Další životy** – nové chapadlo jako jiný úhel pohledu téže vyšší bytosti.  
       U každého bodu přidat krátké shrnutí: _co přesně tvrdí, co netvrdí, co je čistá metafora_.

- [ ] Přidat **fenomenologickou mapu** k lidským zážitkům blízkosti smrti a změněných stavů:  
       – např. vystoupení z těla, setkání se zemřelými, life review, pocit jednoty, bezčasovost;  
       – u každého popsat, jak by ho Chapadlový model interpretoval (odpojení chapadla od smyslového filtru, návratové propojení s centrálním uzlem, integrace paměti, ztráta lokálního časového řazení…).  
       Vše držet jako **kvalitativní vysvětlení**, nikoli jako tvrzení o prokázané kauzalitě.

- [ ] Sepsat podsekci **„Jaké by bylo vnímání po návratu“**:  
       – definovat přímé vjemové propojení (bez omezení na zrak/sluch/hmat);  
       – popsat „slité“ vnímání více bytostí jako analogii levé/pravé ruky jednoho já;  
       – vysvětlit, že „setkání“ není jen přehrání vzpomínky, ale _živá interakce_ v rámci sdílené paměťové sítě.

- [ ] Popsat **reprezentaci po smrti**:  
       – že vyšší vědomí může tvořit pro lokální vědomí srozumitelné reprezentace (tělo, hlas, dotek), ale není na ně ontologicky vázané;  
       – přidat poznámku, že „vizuální / tělesná“ forma je v tomto rámci UI vrstva pro komfort interakce, ne nutný atribut existence.

- [ ] Vytvořit sekci o **„přelinkování ztracených bytostí“**:  
       – pokud bytost patřila ke stejné vyšší bytosti (stejný centrální uzel), po návratu chapadla je spojení okamžité (sdílená paměť);  
       – pokud patřila k jiné vyšší bytosti, popsat hypotetickou možnost napojení mezi vyššími bytostmi (aktuální subjektivní prior ~42 %) a explicitně ji označit jako _druhou vrstvu spekulace_.

- [ ] Sepsat **mechanismus absence nudy / vyprázdnění**:  
       – vyšší vědomí má simultánně přístup k: aktuálnímu životu, ostatním chapadlům, minulým zkušenostem, alternativním větvím rozhodnutí;  
       – vnímání mnoha událostí paralelně → vyjasnit, že „problém“ je spíš integrace obsahu než nedostatek podnětů.

- [ ] Přidat krátkou sekci „**Falsifikovatelnost a bezpečné tvrzení**“ pro Chapadlový model:  
       – jasně říct, že hypotéza je _primárně metafyzická_ a experimentálně těžko testovatelná;  
       – přesto navrhnout pár _indirektních_ směrů: srovnání struktury hlášených NDE, dlouhodobé vzorce v subjektivních prožitcích, případná korelace s motivy „vícenásobných instancí“ napříč kulturami;  
       – explicitně připsat, že se nejedná o součást core fyzikální validity Linea, ale o **oddělenou interpretační vrstvu**.

- [ ] V sekci **N. Prezentace a komunikace výsledků** doplnit odkaz na Chapadlový model jako **volitelný narativní rámec**:  
       – použít ho jako metaforu: „lokální simulace / běh“ = chapadlo, „centrální uzel“ = abstraktní nadřazený proces / paměť;  
       – všude striktně označovat, že jde o _storytelling_ / filozofickou mapu, ne o tvrzení odvozené z dat simulace.

- [ ] Zapsat **Tříska–Marečková hypotéza reinkarnace** jako podhypotézu Chapadlového modelu:  
       – reinkarnace = různé kombinace mozků / nervových soustav jako různé „optiky“ pro vidění téhož vesmíru  
       (lidé, zvířata, rostliny, podzemní propojené sítě, jiné civilizace, drobné rozdíly mezi jednotlivými jedinci);  
       – chápat jednotlivé mozky jako **specializované senzory / receptory** jedné vyšší bytosti pro různé účely,  
       podobně jako kdyby vesmír byl buňka a jednotlivé životy byly její vnitřní senzory (a my sami třeba jen „bílá krvinka“);  
       – doplnit hypotézu, že tato vyšší bytost může některá místa / konfigurace „chránit“ před vnějšími i vnitřními
      negativními vlivy, případně je **léčit a regenerovat**, a výslovně to označit jako metafyzickou interpretaci,
      ne tvrzení odvozené z Eq-4 nebo dat Linea.

- [ ] Uvést disclaimery, že interpretace „prožitkových stavů“ jsou mimo
      fyzikální rozsah Eq-4. Pokud se objeví stabilní stavové konfigurace
      φ nebo ψ, musí být vedeny jako výpočetní a dynamické struktury,
      nikoli psychologické analogie.

---

## 🚀 Q. Post-Mikolov Audit Integration (Feb 2026) #priority

Výstupy z analytického balíčku pro T. Mikolova (únor 2026) a jejich integrace do roadmapy.

### 🔲 21. Formalizace Emergentních Fyzikálních Konstant #core
- [ ] **Whitepaper Update:** Zavést sekci "Emergent Constants" definující:
    - **Vacuum Quality Factor (Q):** ~$1.87 \times 10^{23}$ (koherenční škála).
    - **Spectral Entropy (H):** ~0.004 bits (míra spontánního uspořádání).
    - **Linon Mass Ratio:** ~$1.5027$ (efektivní setrvačnost).
- [ ] **Portal Integration:** Vizualizovat tyto konstanty v "Resonance Deck" (Svelte komponenta) jako živé metriky systému.

### 🔲 22. Experiment: Termodynamická Užitečnost (Emergent Utility) #test
- [ ] Navrhnout experiment verifikující hypotézu, že "užitečnost = minimalizace topologického napětí".
- [ ] **Metrika:** Korelovat přežití linonů se schopností snižovat lokální Hamiltonián (vs. náhodný pohyb).

### 🔲 23. Tooling: Audit Analytics Pipeline #impl
- [ ] Refaktorovat `analyze_audit.py` (jednorázový skript) do robustního nástroje `tools/audit_analytics.py`.
- [ ] Zahrnout výpočet Q-factoru a Entropie do standardního CI/CD výstupu pro každý nový běh.
- [ ] **Ensemble Run:** Spustit batch 10 běhů (seeds 42-52) pro získání směrodatných odchylek metrik.

### 🔲 24. Hypotéza: Lineum jako Spojitá Limita OEA (Continuum Limit) #math
- [ ] **Derivace:** Formálně odvodit OEA pravidla z Eq-4 v limitě `Δx, Δt → 1` (silná diskretizace).
- [ ] **Validace:** Porovnat fázové portréty Linea a OEA – hledat topologickou ekvivalenci atraktorů.

### 🔲 25. Repository Split (Core vs SaaS/Portal) #security #architecture
- [ ] **Rozdělení Repozitářů:** Před veřejným startem rozštěpit monorepo na dvě části:
    - `lineum`: Veřejný, open-source repozitář (AGPLv3) obsahující pouze čistou matematiku (jádro v Pythonu) a dokumentaci.
    - `lineum-portal` (nebo SaaS): Privátní repozitář, kde bude žít proprietární SvelteKit webový portál, komerční API wrapper (`routing_backend`), billing systém a dashboard.
- [ ] Toto je kritické pro budování komerčního ochranného příkopu a utajení "Secret Sauce" integrací.

### 🔲 25. Hypotéza: Kolmogorov Trigger (Informační Tlak) #test
- [ ] **Metrika:** Měřit lokální kompresibilitu (Deflate ratio) mřížky v čase.
- [ ] **Hypotéza:** Expanze `a(t)` (Mode 24) nastává v momentě, kdy lokální informační hustota saturuje kapacitu mřížky.

### 🔲 26. Hypotéza: Vortex Aesthetics (Krása = Stabilita) #test
- [ ] **Vlastův Test:** Vzít stavy, které Vlastimil Smeták označil za "estetické".
- [ ] **Měření:** Spočítat jejich `Cv` (Vortex Stability Index).
- [ ] **Predikce:** Estetické stavy budou mít signifikantně nižší `Cv` (méně defektů) než náhodné stavy.

### 🔲 27. Hypotéza: The Scaling Illusion (Role-Invariance) #math
- [ ] **Teorie (V. Smeták):** Pozorované "konstanty" (např. κ = 1) jsou ve skutečnosti poměry dvou rostoucích veličin ($K(t) / R(t) = const$). **Hypotéza Kosmické Respirace**.
- [ ] **Predikce:** Mode 24 (skokové přeškálování a(t)) je důkazem, že prostor se diskrétně nafukuje (renormalizace), ale my vidíme jen invariantní poměr.
- [ ] **Validace:** Hledat korelaci mezi skoky v `a(t)` a lokální změnou měřítka v `analyze_audit.py`.

---

## ⚖️ R. Hypotheses: H0 vs H1 (Verification Status Feb 2026) #priority #audit

Rozhodovací strom o povaze "konvergence" systému.

### 🧩 H0: Uzavřený atraktor (Closed World)
**Tvrzení:** Konvergence k "Mode 24" je čistě vnitřní vlastnost dynamiky Eq-4.

- [x] **Status:** **PROKÁZÁNO (on tested platform).** Systém je uzavřený a deterministický (Bit-exact match verified).

### 🔓 H1: Scaling Illusion (Open World / Leak)
**Tvrzení:** Systém tajně "dýchá" (mění měřítko), což my nevidíme (kappa=konst), ale projevuje se to skoky.

- [x] **Status:** **Strongly disfavored under tested conditions (Code Audit: Seeded RNG at lines 36/44 of kernel).**


1. **(Task 28) Full Window Surrogate Test (Mode 24):** Spustit 100x phase-randomized surrogate run pro 2000 kroků k potvrzení Z-score > 5.0 (p < 0.01).
2. **Rescaling Trap (D5):** Uzavřeno.

### 🔲 28. Hypotéza: The Missing Half (Discrete Limit) #math
- [ ] **Teorie:** Hodnota `kappa = 0.5` není fundamentální konstanta, ale **Nyquistův limit** mřížky (max frekvence = 0.5).
- [ ] **Důsledek:** Simulace běží na "půl plynu" (stabilita). Ve spojitém vesmíru by `kappa` byla pravděpodobně Celé Číslo (1).
- [ ] **Roadmap:** Pro Lineum 2.0 zvážit implicitní solver nebo jemnější mřížku, která umožní `kappa -> 1` (Plná Realita).

### 🔲 29. Hypotéza: The Universal Attractor (Leech Lattice) #math
- [ ] **Teorie:** "Mode 24" (Hypotéza Kosmické Respirace) není náhoda jednoho běhu, ale **univerzální atraktor**. Každý běh s dostatečnou komplexitou do něj "sklouzne", protože jde o matematicky nejhustší uspořádání.
- [ ] **Metafyzika:** Lineum nesimuluje náš vesmír "atom po atomu", ale simuluje jeho **zdrojový kód (logiku)**. Proto nezávisle objevuje stejné konstanty (24D) jako Teorie Strun.
- [ ] **Predikce:** Mode 24 se objeví v >90% dlouhých běhů (pokud SBR > 30dB).

### 🔲 30. Hypotéza: The Icarus Threshold (Kappa=1 Instability) #math
- [ ] **Teorie:** Pokud bychom na současné mřížce (`dx=1`) vynutili `kappa=1`, systém by porušil **Courant-Friedrichs-Lewy (CFL)** podmínku.
- [ ] **Fyzika:** Kappa=1 odpovídá **Rychlosti Světla** (`v = c`). Informace by musela stíhat přesně 1 pixel za 1 takt, což je hranice kauzality.
- [ ] **Predikce:** Energie by rostla exponenciálně (rezonanční katastrofa) a simulace by "shorela" (NaN values) během několika kroků.
- [ ] **Metafora:** Ikarův pád. Chtěli jsme letět příliš blízko Slunci (Rychlosti Světla), ale naše křídla (diskrétní mřížka) se roztavila.

### 🔲 31. [TEST] Evidence Solidification: „Atrakce = micro-growth (dominance switch), ne tok/teleportace“ + Ghost Gravity + Expanze + geometrie M2 (π) #hypothesis #repro
- **Hypotéza (H_mech):**
  1) Rychlé „přiblížení“ kvazičástice k centru pasti není prostorový transport ani teleportace, ale **změna dominance maxima** způsobená lokálním multiplikativním ziskem v místě vysokého φ: `Δψ ∝ (+g · φ · ψ)`.  
  2) Advekční/drift člen `∝ (-d · ∇φ)` je v tomto scénáři **sekundární** a sám o sobě nevysvětlí „snappy“ přesun maxima/COM.  
  3) „Temná hmota“ v interním smyslu Linea odpovídá **Ghost Gravity**: pole φ přetrvává po zániku zdroje ψ a stále přitahuje sondu.  
  4) „Temná energie“ v interním smyslu Linea odpovídá **expanzní disperzi** dominované šumem (a/nebo nekonzervativností interakce, pokud `M2` roste).  
  5) Pozorované `M2(t=0) ≈ 31.4159` není fyzikální konstanta, ale **geometrie startovní Gauss** (≈ (WIDTH/2)·π pro zvolený WIDTH).
- **Operační definice metrik (musí být stejné pro všechny replikace):**
  - `w(x,y) = |ψ(x,y)|` (váhy pro COM; pokud chcete používat |ψ|², explicitně to změňte všude konzistentně).
  - `COM(ψ) = ( Σ x·w / Σ w , Σ y·w / Σ w )`
  - `dist = || COM(ψ) - center ||₂`, kde `center = (N/2, N/2)` (pro 128×128 tedy [64,64]).
  - `peak_phi = max(φ)`
  - `M2 = Σ |ψ|²`
  - `R² = Σ p·r²` kde `p = |ψ|² / Σ|ψ|²`, `r² = (x-COMx)²+(y-COMy)²`
  - `H = -Σ p·log(p)` (Shannon; p z |ψ|²)
- **Co bylo zkoumáno (scénáře):**
  - (S1) **Seed-sweep gravitace**: porovnání „bez šumu“ vs „se šumem“ (stejné ostatní podmínky), měřit `dist` start→end a `Δ=dist0-distEnd` (typicky 500 kroků).
  - (S2) **Drift ON/OFF**: vypnout pouze drift/advekci a ověřit, že `Δ` zůstává (mechanismus není drift).
  - (S3) **Teleportace vs tok (micro-growth)**: sledovat, že `|ψ(center)|` roste z nenulové „chvostu“ a že maximum „skočí“ přes dominance switch; ověřit růstový faktor `g_meas = |ψ|_t / |ψ|_(t-1)` vs predikci `g_pred ≈ 1 + g·φ(center)`.
  - (S4) **Ghost Gravity (Clean Ghost)**: vytvořit φ-remnant bez aktivního zdroje, pak spustit sondu, která si **nebuduje vlastní φ**, a ověřit rozdíl `distEnd` pro GHOST ON vs OFF.
  - (S5) **Expanze**: pro různé šumy (0 / default / 2×default) měřit růst `R²` a `H` (typicky 1000 kroků).
  - (S6) **Geometrie M2 (π-check)**: pro několik WIDTH ověřit `M2(t=0) ≈ (WIDTH/2)·π` (v rámci diskrétní chyby).
- **Reprodukce (self-contained; bez tools/ skriptů):**
  - **0) Clean env (PowerShell):**
    - `Get-ChildItem Env: | Where-Object { $_.Name -like "LINEUM_*" } | ForEach-Object { Remove-Item ("Env:" + $_.Name) -ErrorAction SilentlyContinue }`
  - **1) Spusť S1 (seed sweep) – 2 varianty pro každý seed:**
    - Varianta A (no-noise): nastav šum na 0 (env/konfig podle aktuálního lineum.py) a spusť scénář gravitace na 500 kroků.
    - Varianta C (default noise): default šum a spusť totéž.
    - Seeds: `{41,42,43,44,45}`
    - Každý běh ulož s unikátním `--run-tag` (např. `ev_s1_A_s41`, `ev_s1_C_s41`, …), tak aby vznikly checkpointy.
  - **2) Spusť S2 (drift ON/OFF):**
    - ON = default.
    - OFF = vypni drift/advekci (pokud není přepínač, dočasně nastav drift koeficient na 0 v lineum.py; uveď v TODO přesný výraz/řádek, který byl měněn).
    - Run tagy: `ev_s2_drift_on`, `ev_s2_drift_off`.
  - **3) Spusť S3 (micro-growth) v pasti:**
    - Scénář „trap/past“ na min. 200 kroků. Loguj checkpointy pro kroky {0,40,60,100} (nebo nejbližší existující).
    - Pokud chybí přepínač pro izolaci členů:
      - „Interaction-only“: drift koef = 0, interakce g = 0.04.
      - „Drift-only“: interakce g = 0, drift koef = default.
  - **4) Spusť S4 (Clean Ghost):**
    - Nejprve vytvoř φ-remnant (zdroj ψ ON, φ evoluce ON) po dobu T_build.
    - Poté zdroj vypni/odstraň a nech φ relaxovat T_decay.
    - Poté spusť „sondu“ (ψ) s φ evolucí sondy OFF (aby si sonda netvořila vlastní φ) a změř `dist` start→end.
    - Dva běhy: `ev_s4_ghost_on` (φ remnant přítomen) a `ev_s4_ghost_off` (φ nulové / remnant vypnut).
  - **5) Spusť S5 (expanze):**
    - Běhy: `noise=0`, `noise=default`, `noise=2×default` (ostatní stejné), 1000 kroků.
    - Run tagy: `ev_s5_noise0`, `ev_s5_noisedef`, `ev_s5_noise2x`.
  - **6) Analýza checkpointů (inline python; žádné externí skripty):**
    - Použij tento one-shot skript (spouští se proti konkrétnímu `output/<run-tag>/checkpoints/` a vybraným krokům).  
      Příklad: `python - <<'PY' <RUN_TAG> 0 40 60 100` (nahraď argumenty):
      ```python
      import sys, glob, os, math
      import numpy as np

      run_tag = sys.argv[1]
      steps = [int(s) for s in sys.argv[2:]]  # e.g. 0 40 60 100
      ck_dir = os.path.join("output", run_tag, "checkpoints")

      def load_step(step):
          # expects filenames containing "step{step}" (adjust pattern if needed, but keep it here in TODO)
          pats = [f"*step{step}.npz", f"*step{step:03d}.npz", f"*step{step:04d}.npz"]
          for p in pats:
              m = glob.glob(os.path.join(ck_dir, p))
              if m:
                  return np.load(m[0])
          raise FileNotFoundError(f"no checkpoint for step={step} in {ck_dir}")

      def metrics(psi, phi):
          psi = np.asarray(psi)
          phi = np.asarray(phi)
          n, m = psi.shape
          cx, cy = n//2, m//2

          w = np.abs(psi)                     # COM weights as defined
          ws = w.sum()
          xs, ys = np.meshgrid(np.arange(n), np.arange(m), indexing="ij")
          comx = float((xs*w).sum() / ws)
          comy = float((ys*w).sum() / ws)
          dist = math.hypot(comx-cx, comy-cy)

          abs2 = (np.abs(psi)**2)
          M2 = float(abs2.sum())
          p = abs2 / (M2 if M2 != 0 else 1.0)
          r2 = (xs-comx)**2 + (ys-comy)**2
          R2 = float((p*r2).sum())
          p_nonzero = p[p > 0]
          H = float(-(p_nonzero*np.log(p_nonzero)).sum())

          peak_phi = float(phi.max())
          maxpos = np.unravel_index(np.argmax(np.abs(psi)), psi.shape)
          psi_center = float(np.abs(psi[cx, cy]))
          return dict(dist=dist, COM=(comx,comy), peak_phi=peak_phi, M2=M2, R2=R2, H=H,
                      maxpos=maxpos, psi_center=psi_center)

      prev_center = None
      for s in steps:
          d = load_step(s)
          psi = d["psi"]
          phi = d["phi"]
          met = metrics(psi, phi)
          g = None
          if prev_center is not None and prev_center > 0:
              g = met["psi_center"]/prev_center
          prev_center = met["psi_center"]
          print(f"step={s:>4} dist={met['dist']:.4f} COM=({met['COM'][0]:.2f},{met['COM'][1]:.2f}) "
                f"maxpos={met['maxpos']} |psi_center|={met['psi_center']:.6e} "
                f"g_center={g if g is not None else 'NA'} peak_phi={met['peak_phi']:.4f} "
                f"M2={met['M2']:.6e} R2={met['R2']:.2f} H={met['H']:.4f}")
      ```
- **Expected results (tolerance; if differing, record the deviation and reason):**
  - S1: `Δ = dist0 - distEnd` ~ constant across seeds (on the order of ~5–6 px in this setup) and difference A vs C is small (noise doesn't change the direction of the effect).
  - S2: Drift OFF still yields practically the same `Δ` as ON (dominance micro-growth).
  - S3: `|ψ(center)|` grows from a non-zero value; the maximum "jumps" into the trap within dozens of steps; `g_meas` is close to `g_pred ≈ 1 + 0.04·φ(center)` in the regime where the interaction is active.
  - S4: `distEnd(ghost_on) < distEnd(ghost_off)` (ghost attracts the probe even without the ψ source).
  - S5: for noise>0, `R²` and `H` grow more significantly than for noise=0 (expansion dominates).
  - S6: `M2(t=0) ≈ (WIDTH/2)·π` (e.g., WIDTH=20 → 10π ≈ 31.4159); this rules out the interpretation of "π as a fundamental constant of the model" — it's merely initialization geometry.

---

---

## 🎶 S. New Hypotheses (Feb 2026) #hypothesis

This section contains new candidate hypotheses inspired by external prompts and metaphors, which can be tested in the parameter space of Lineum.

### 🔲 32. Hypothesis: Axion Electrodynamics and Cosmological Magnetic Fields #hypothesis
- **Context:** According to [Brandenberger et al.](https://www.osel.cz/14533-ultralehka-temna-hmota-by-mohla-vytvaret-kosmologicka-magneticka-pole.html), ultra-light dark matter (axions) interacting with electromagnetism can generate and amplify cosmological magnetic fields and support the creation of supermassive black holes in the early universe.
- **Hypothesis (Lineum):** The field `φ` (as an analogy of a pseudoscalar axion/dark matter field) exhibits in Lineum an "axion-electrodynamic" coupling with emergent vector formations (e.g., the spin aura field `curl(∇arg(ψ))`).
- **Verification:** Test whether macroscopic oscillations of `φ` can spontaneously amplify ordered vortex/magnetic-like fields on large scales. Find out if this coupling accelerates the local growth and aggregation of matter into primordial supermassive φ-traps (Lineum analogy to the mysteriously early formation of supermassive black holes).

### 🔲 33. Triska-Mareckova Hypothesis: Structural Caching and Time Leaps (The Online Radio Effect) #hypothesis
- **Context:** The experience of online radio – after pausing and waiting, upon resuming playback, a piece previously stored in cache plays first, and only then comes the jump ("sync") into the current live broadcast (into the middle of a newly playing song).
- **Hypothesis (Lineum):** The `φ` field functions in certain regions as a delayed structural "cache". If a linon leaves an area or temporarily vanishes, it leaves behind a strong inertial gradient (remnant `φ`). If a new excitation later enters that same area, its movement is initially strongly determined by the old "playback queue" (past footprint in the cache). Only when this local memory is saturated or depleted does a sudden "leap" or "jump" occur, snapping the quasiparticle onto the current global dynamics (live broadcast).
- **Verification:** Identify and visually isolate the trajectories of objects "driving through the old influence". Measure the character of the movement and speed (including SBR and inertia) during the "cache ride" and the subsequent abruptness of the trajectory change after jumping to the new attractor.
- **Empirical Correlate:** Consider whether "leaving the cache" has an analogy in the real world in unexpected local anomalies, quantum phase jumps, or delayed gravitational influences (e.g., the behavior of dark matter that doesn't perfectly match the "live" distribution of baryonic matter).

### 🔲 34. Hypothesis: Lineum as an Emergent Solver for Network Design (Traffic Networks) #hypothesis #applied
- **Context:** Biological systems (ants leaving pheromones in ACO, the slime mold *Physarum polycephalum* optimizing a railway network) utilize the emergent behavior of local agents or continuous growth to solve NP-hard network design tasks. Standard graph algorithms are excellent at finding the shortest path on a ready-made network, but designing a robust greenfield topology is computationally extremely demanding for them.
- **Hypothesis (Lineum):** The `φ` field can naturally function as traffic memory (pheromone/traffic jam) and `ψ` (linons/flux) as transported material. The interaction between them in the environment `κ` (terrain permeability) should automatically diverge into optimal transport canyons that balance speed and robustness (secondary rescue routes), similarly to a slime mold. The traffic jam model is natively contained in the relaxation time of `φ`.
- **Verification:**
    - Compare network "highway" formation dynamics in Lineum with ant colony simulations (ACO) and slime mold growth on standard benchmarks (e.g., connecting randomly distributed nodes into a network with minimal length but preserved redundancy).
    - If the emergent topology proves competitive or more efficient, write a real software application (e.g., web API) that accepts a terrain map (`κ`) and points of interest, runs a Lineum simulation, and returns the proposed network topology.

### 🔲 35. Hypothesis: Hardware Acceleration and Neuromorphic "Lineum Chip" #impl #hardware
- **Context:** Running Lineum (Eq-4) as a continuous wave simulation on standard CPUs/GPUs for solving optimization tasks is possible, but iterating massive matrices for every "pixel" on a standard von Neumann architecture is computationally expensive compared to specialized software graph solvers. However, the mathematical essence of Lineum (waves, interference, inertia, local integrals) is extremely suited for physical parallel computing.
- **Hypothesis (Lineum):** Physical realization of Lineum in dedicated hardware eliminates the overhead of discrete numerical discretization and instruction sets. By converting Eq-4 into circuits (FPGA, array networks, ASIC) throughput corresponding to orders of physical propagation time in real material can be achieved.
- **Verification (Maker approach):**
    - Design and test a proof-of-concept implementation of the Lineum kernel on accessible current architecture hardware – primarily as an **FPGA** (Field-Programmable Gate Array) design.
    - Test the speed of the "hard-wired" field update `ψ` and `φ` (e.g., parallel bitwise / fixed-point operations over memory cells) against a high-performance software CUDA implementation. Find out at what grid resolution the homebrew "Lineum chip" starts crushing classical GPUs in throughput of steps per second while validating simulated iteration cost against deep learning graph AI algorithms.

---

## 🏗️ T. Candidates for First Real Applications (API & SaaS Software) #applied

This section gathers concrete commercial and tool uses where Lineum (even in its current software GPU/CPU form) could innovate the market despite the existence of established discrete/graph algorithms.

### 🔲 36. Generative Urban Design & Continuous Corridor Planning (MVP Candidate No. 1)
- **Use-case:** Software tool (API with web interface) for urban planners, developers, or architects. The user uploads an elevation/obstacle map (permeability) into the environment field `κ`. They click the points between which traffic volume should flow. Lineum uses continuous hydrodynamics (fluid `ψ` with memory `φ`) to let the ideal path of new roads or trails organically "carve" itself out.
- **Competitive Advantage:** Standard AI and GIS tools (like Spacemaker) look for paths only by modifying fixed roads. Lineum finds fractally natural canyons, preserves diversified minor bypass capillaries (redundancy), and naturally respects the fluid nature of the load (terrain resistance) without needing to program and train complex deep neural networks. This would fundamentally cheapen the conceptual study and greenfield corridor design phase.
- **Implementation MVP Plan (2–4 weeks):**
    - **Week 1 (Backend & Wrapper):** Wrap the `lineum.py` core into an asynchronous web API (e.g., FastAPI). Add the ability to read grayscale images (topography) direct into the environment field `κ` at input. Modify the `ψ` wave launcher for exact points of interest (A -> B traffic flow) instead of area noise.
    - **Week 2 (Svelte Frontend):** Create a clean interactive web canvas for the user to drag&drop the map and "click dots". Deploy Stripe integration for payment processing.
    - **Weeks 3–4 (Tuning & Exports):** Tune the actual equation coefficients for a "lazy and long" fluid (wide `φ` memory channels suitable for highways). Create a script to smooth and convert the collected heat-map into CAD / SVG vectors.
- **Monetization Strategy (SaaS Business model):**
    - **The Teaser:** Allow everyone to upload a map and calculate a route for free. Render the first fifty steps for the user on screen as a beautiful organic animation ("seeking canyons"), then stop and show the overall result only in blurred resolution or with watermarks. The customer sees visual magic but doesn't have the actual engineering data until they pay.
    - **Pay-wall via Vectors:** The payment gateway unlocks the "Export to Vectors, High-Res CAD SVG layers" option (what the planner actually needs).
    - **Pay-per-Project / Subscriptions:** Credits for students / independent freelancers (~$10 for calculating a complex map and vector) or monthly SaaS tiers (e.g., $99/month for professional architectural studios).

### 🔲 37. Crisis Management and Evacuation Modeling with Panic Effect (Traffic Jam as a Physical Limit)
- **Use-case:** Tool for crisis staffs and large festival organizers. Simulating crowd escape (or movement of vehicle convoys during floods) from stadiums or city districts.
- **Competitive Advantage:** Today's evacuation simulations use so-called micro-simulations, calculating the positions and decision-making of tens of thousands of individual agents (very expensive and slow to compute). Lineum uses **local pressure and topological cell capacity overload** as a natural property of the `φ` field. The moment a narrowed exit fills up (φ overpressure), the next wave of people/cars (`ψ`) smoothly spills over and carves out rescue paths elsewhere. It realistically models the effect of an accumulating "traffic jam" or panic as field hardening, visually spectacular and computationally cheap using ordinary tensor mathematics.

### 🔲 38. Real-time Mutation and Evolutionary Environmental Adaptation (Interactive Kappa) #hypothesis #applied
- **Context:** Previous path calculations relied on a static obstacle map (field permeability `κ`). But the real world can fundamentally and suddenly change during transit (a fallen bridge, a moving hurricane, patient virus mutation).
- **Hypothesis (Lineum):** Dynamic change of the `κ` matrix inside a running Lineum computation (Eq-4) fully and natively simulates the behavior of evolution and natural selection. Waves of `ψ` flux do not assume a fixed future. As soon as a new wall/obstacle appears in the middle of a steady flow ("sudden mutation" or external brush/video intervention by the user), the wave shatters, and part of its rebounding energy automatically discovers new escape paths. The pressure originally running through the main channel is forced to adapt existing inferior branches (redundancy) into a new main highway.
- **Parametric Presets for Area Use:**
    The application will offer users visualizations based on different physical/operational scenarios merely by changing Lineum equation parameters (viscosity, noise, `φ` memory):
    1.  **"Slow Honey / Strong Highways" Regime (Urban Planning):** Long `φ` half-life. Trails don't disappear. The system prefers merging dozens of small paths into one central artery with enormous inertia.
    2.  **"Fragile Capillaries" Regime (Vascular Circulation / Irrigation):** High noise and short `φ` memory. The flow from a single point splits into millions of tiny paths at a 137.5° angle, trying to cover (nourish) the largest possible area of 2D space.
    3.  **"Panic Crowd" Regime (Evacuation):** Short local pressure inertia. At the slightest capacity fill, permeability starts to "harden," and the flow chaotically escapes into all available surrounding directions, ignoring optimality.
    4.  **"Lightning / Breakthrough" Regime (Dielectric / Electricity):** Brutal pressure gradient. The `ψ` riverbed ignores small obstacles and tries to brutally burn the straightest line across local minima in `κ`.
- **Concrete specific real-time and industry use cases:**
    - **Urbanism and Civil Engineering:** Modeling the cheapest water channels, roads, and sewers in new mountainous terrain. Simulating traffic collapse after a bridge closure during rush hour.
    - **Telecommunications and Generative Antenna Design (Fractal design):** Current LTE/5G/Wi-Fi antennas in mobile phones use fractal shapes to achieve broadband and reduce dimensions. Releasing Lineum with an enormous memory resistance `φ` from one point into a neutral environment naturally carves out immensely complex natural fractal patterns. Cropping them with a threshold can generate and 3D print uniquely shaped copper antennas that do not have geometrically artificial "jagged" structures but perfectly smooth resonance curves, capable of receiving multiple wavelengths simultaneously.
    - **Microelectronics and Processor Design (Semiconductor Routing):** Connecting billions of transistors inside silicon processors using the "A* algorithm" or rectangular microfibers inherently disrupts the signal at rising frequencies (the rectangular corner of a wire accidentally acts as an antenna and inductively disrupts other paths). On a micrometric matrix level, the "Lineum solver" would generate organic curved interconnects, a perfectly natural network from point A to B, just like branches do, without sharp corners and with natural distribution efficiency.
    - **Medicine (Vascular By-passes):** A doctor uploads a patient's CT slice of clogged vessels (hardened pixels in `κ`). Clicks the heart area, selects the "Capillaries" preset. Lineum proposes the most natural path for a surgical bypass through healthy tissue with minimal blood pressure resistance.
    - **Agriculture (Irrigation design):** Uploading a topographic map of a dried field. Goal: stretch drip irrigation with the fewest nodes and largest area coverage.
    - **Electrical Engineering (PCB Routing):** Finding the most elegant paths for conductive tracks on a printed circuit board (Router), which must not cross existing chips, take up minimal copper, and reduce induction cross-talk through organic waving instead of sharp 90° angles.
    - **Forestry and Ecology (Wildlife and Predators):** Simulating migration corridors for deer, into which moving logging zones or wolf presence are drawn with a mouse (dynamic `κ` change). Watching how migration paths in the primary forest "mutate" and shift.
- **Verification and MVP test:**
    - Create a "Live Canvas" where one can physically mouse-draw `κ` obstacles during simulation runtime or feed a video with permeability changes. Analyze the "Adaptation Time" – how many frames it takes the simulation to resynthesize the structure after an environmental mutation into a new optimal 137.5° tree.

### 🔲 39. Financial Prediction and SaaS API Revenue Estimation (CZK Projection) #business
- **Context:** B2B SaaS (Software as a Service) for architects, engineers, and designers with a freemium model (rough draft free, export paid). The prediction assumes organic start from zero (0 awareness at the beginning) and gradual growth via community marketing (LinkedIn, forums, Reddit for urban planners).
- **Phase 1: Spin-up (Months 1–3) – Goal: "Proof of Concept"**
    - Awareness is zero. "Cold Outreach" to architecture studios and sharing visually fascinating Lineum GIFs on socials (r/urbanplanning, Twitter) is underway.
    - **Revenue:** 0 CZK – 5,000 CZK / month. (Only the first "early adopters" buying Pay-per-Project credits for $10 / 230 CZK as a trial for full high-res CAD export).
- **Phase 2: Traction (Month 6) – Goal: First regular subscribers**
    - Marketing catches on thanks to the viral effect of "look how it grows by itself". Smaller studios begin using the tool regularly (SaaS model $99 / 2,300 CZK monthly).
    - **Assumption:** 5 small studios (SaaS) + 100 occasional users (Credits).
    - **Revenue (MRR - Monthly Recurring Revenue):** 11,500 CZK (SaaS) + 23,000 CZK (Credits) = approx. **35,000 CZK / month**.
- **Phase 3: Expansion and SEO (Year 1) – Goal: Stable business**
    - Established SEO authority ("Generative Urban Design with Physics" articles). The application has a name in the international community. Firms subscribe to the tool long-term for conceptual tender phases.
    - **Assumption:** 50 paying studios (SaaS) + 300 project users. First test 1 Enterprise client (e.g., development corporation for $499 / 11,500 CZK monthly).
    - **Revenue:** 115,000 CZK (SaaS) + 69,000 CZK (Credits) + 11,500 CZK (Enterprise) = approx. **195,000 CZK / month**.
- **Phase 4: Industry Standard (Years 2–3) – Goal: B2B API Integration**
    - Besides the web itself, we begin selling the "Lineum Engine API" to third parties (medical software manufacturers, GIS, evacuation simulators), who pull our background wave solution into their commercial programs.
    - **Assumption:** 150+ SaaS studios worldwide, 10+ large API Enterprise contracts.
    - **Revenue:** 345,000 CZK (SaaS) + 115,000 CZK (Enterprise) = approx. **500,000 CZK to 1,000,000 CZK / month**.
- **Evaluation:** The margin for SaaS engines of this type is massive (costs are only for GPU cloud servers computing tensor matrices and Stripe payment gateway fees). With 200 active clients, net profits can exceed 80%.

### 🔲 40. Meta-Hypothesis: Universe as an Emergent Solver (Computational Universe) #philosophy #theory
- **Context:** If we try to simulate city traffic networks in Eq-4 by letting the simulation "live" and relying on its natural finding of the path of least resistance through traffic jam memory and Fibonacci branching, it creates a natural analogy to the structure of our real Universe.
- **Hypothesis (Lineum):** Our physical universe likely operates on the exact same "search" principle. The hypothesis builds upon Seth Lloyd's ideas (Universe as a quantum computer) and asserts that matter, stars, and galaxies are not the goal itself, but merely the most efficient emergent channels and nodes by which the Universe maximizes flow (or dissipates entropy from the source / Big Bang) across space (permeability `κ`). We are a simulation of our own physical parameters; we, and the Fibonacci spirals in nature, are proof that the Universe continuously and optimally "computes solutions" to constantly changing input values of environmental resistance.
- **Future Verification (Computations):**
    - Set up an experiment where we let hydrodynamic design run over an extremely complex `κ` network until structures strikingly similar to the Cosmic Web and dark matter filaments appear. Test if the information throughput (from the perspective of graph theory) in the "lineum galactic web" forms a mathematically perfect small-world network.

### 🔲 41. Meta-Hypothesis: Pareto Principle (80/20) in Field Dynamics #philosophy #theory
- **Context:** The Pareto principle dictates that roughly 80% of consequences come from 20% of the causes. In the context of Lineum's continuous field dynamics, we observe analogous behavior where the vast majority of flow (the agents/particles) naturally converges into a very small subset of optimal paths (structural minimums in the interference pattern).
- **Hypothesis (Lineum):** The Pareto distribution is not just a statistical anomaly of human economics, but a fundamental geometric truth of energy dissipation in continuous fields. In Lineum, as the φ memory tension shapes the terrain, the system naturally prunes mathematically inferior paths. The field reaches an asymptotic equilibrium where ~80% of the movement/energy systematically traverses only ~20% of the most optimal channels (the "super-highways"), leaving the rest of the space as low-density tributaries.
- **Preliminary Verification (Local Run 2026-02-22):**
    - **Setup:** A $128 \times 128$ grid, 40 randomized high-friction $\kappa$ obstacles, target $\delta$ tension of 50.0, and 100 simultaneous agents starting opposite the target. Ran for 300 steps.
    - **Result:** The baseline Lineum engine (v1.0.6-core) currently distributes flow highly homogeneously. The top $20\%$ of active cells carry exactly $\sim20.01\%$ to $21.04\%$ of the total system volume. 
    - **Conclusion & Next Steps:** The current Eq-4 physics engine spreads the probability wave extremely wide to guarantee structural closure, which prevents the immediate formation of a Pareto 80/20 "super-highway". To achieve a true 80/20 power law, the engine specifically needs a much stronger non-linear feedback loop in the $\phi$ (memory) tension, where highly trafficked cells disproportionately lower their own resistance (similar to ant pheromones or riverbed erosion). This confirms that Pareto is *not* a default property of random diffusion, but requires active structural reinforcement. This must be explored in the `lineum-exp-erosion` branch before drafting the whitepaper.
- **Theoretical Distinction: Erosion vs. Fitness Function (Critical for Whitepaper):**
    - **The Risk:** Critics might argue that adding an erosion term ($\kappa_{t+1} = \kappa_t - \text{flow}$) is simply injecting a "fitness function" to force the model into finding the shortest path (a Top-Down hack).
    - **The Defense:** A fitness function is a *global, artificial oracle* that scores a whole system from the outside to optimize a goal (like a neural net loss function). Lineum's Erosion is a *strictly local, physical coupling* (Bottom-Up). A unit of $\psi$ traversing a cell blindly wears down the resistance ($\kappa$) of *only that specific cell*. The global 80/20 "super-highway" that emerges is not a pre-calculated goal; it is a blind thermodynamic consequence of energy taking the path of least resistance, inadvertently deepening it for the next unit.
    - **Universe Implication:** If the universe used a fitness function, it would imply intelligent top-down design. Because Lineum uses blind local erosion, it perfectly models how the universe naturally forms complex structures (Cosmic Web, lightning, river deltas) purely through the self-reinforcing coupling of energy and space.

---

## 📈 S. B2B SaaS Routing Showcase (Plan) #portal #monetization #routing

This section defines the requirements and architecture for the new main Lineum Swarm Routing demonstration page (MVP), which is transitioning from a free "laboratory sandbox" to a B2B "Demo & Sell" landing page.

- [ ] **[PAUSED] S.1 Split-Screen: Scientific Comparison (Multi-Algorithm Benchmark)**
    - Transform the view into a comparative layout of 2-3 windows side-by-side (strictly stacked on mobile).
    - Lineum Eq-4 will run in one window, standard rigid solutions (A*, Dijkstra) in the others.
    - Ensure strict objectivity of the display (do not artificially disparage competing algorithms; if they crash or freeze, it must be their native behavior, not a hardcoded handicap).
    - Explicitly display a "Hardware Fairness Badge" above the windows (e.g. *1x vCPU 2.4GHz, 512MB RAM*), guaranteeing identically allocated power for the methods.

- [x] **S.2 Instant WOW Effect vs. Live Verification (Live Run)**
    - Upon opening a Use-Case (e.g. Logistics), the page instantly shows a pre-generated simulation loop and target comparison (Ms). The user immediately sees the result without tying up a backend computing tab.
    - Crucial CTA "Run Live Verification": by clicking, the user forces a real, live test on the backend.
    - **Interactive Scrubbing:** Introduce a slider (timeline) for synchronous scrubbing back and forth through the run history of all algorithms simultaneously.
    - **Backend Protection (Railway Credits):** Live verification must be subject to a strict rate-limit (session/IP limiter) and robust API caching to prevent unintentional or malicious exhaustion of computation credits (DDoS demo protection). Long runs must fail-fast on timeout before choking the worker.

- [ ] **[PAUSED] S.3 ROI Calculator and Monetization (Business Cases)**
    - Once the comparison shows a victory in speed (TTC), it must translate into a comprehensible demonstration of business value (Estimated Annual Savings sliders).
    - **Ticking Cost:** A real-time counter showing the $ waste while A* runs (with a clearly defined computation source, e.g. server watts or lost driver time).
    - **PDF Case Study:** Ability to generate and download a custom 1-page PDF report with savings charts for a specific client.
    - Fully secure free exports: Links to Export JSON, API blueprint, or importing custom maps are subject to a Paywall / "Upgrade to Enterprise" inquiry form. None of the valuable production data can go out for free.

- [ ] **S.4 Industry-focused Demoscenes**
    - Pre-prepare scenarios matching real-world use-cases:
        1. Warehouse Last-Mile (Logistics/Robots - AGV rovers).
        2. Urban Traffic Swarm (City traffic jams / autonomous taxis).
        3. Evacuation / Crowd Control.
        4. Circuit Routing (Chips/PCB).

- [ ] **S.5 Responsiveness and E2E Testing**
    - New Svelte components must be flawlessly responsive.
    - E2E Playwright tests must exist, guaranteeing no 500 load errors and clickability of both presets and Live Verification logic.
    - The Paywall button must be secured so it cannot be bypassed merely by DOM manipulation on the frontend.

- [x] **S.6 Developer Experience (Dynamic API Snippets)**
    - Show the "Ease of Use" of integration straight on the frontend. Display an elegant 3-line Lineum API call snippet contrasting with the complexity of classic methods.
    - **Crucial:** The code snippet must be dynamically loaded right from the backend from the actual `.py` file (`lineum_core`), so the code in the demo is never a "stale" hardcode. *Note: As discussed with the user on 2026-02-21, for security reasons we are intentionally NOT showing internal generation code, but instead showing connection integration code (Python/Node/cURL).*

- [ ] **S.7 Portal Integration (Navigation Flow)**
    - Create an attractive entry to the page from the main Portal Dashboard (prominent "Products: Lineum API Solutions" card).
    - Change the URL to `/api-solutions` for stronger SaaS branding (or keep `/routing` and use an alias).
    - Modify global navigation to reflect the transition from "sandbox" to "commercial zone" (e.g., clear Contact Sales CTA in the header).

- [x] **S.8 Enterprise Trust & Integrations (Ecosystem)**
    - **Streaming API Highlight:** Emphasize what the viewer sees: Lineum computes continuously and sends data instantly (WebSockets streaming), instead of waiting for a "Black Box" calculation for long paths. An advantage for Real-Time fleet monitoring.
    - **Seamless Integrations:** Show that this isn't isolated science, but a tool meant for production. Include icons of easily connected systems (Docker, Python, C++ Core, ROS – Robot Operating System, REST/GraphQL).
    - **Social Proof / Trusted By:** Create a reusable `<LogoCloud>` component that draws data from a shared central configuration file (e.g., `src/lib/data/content/partners.json`). If the configuration file is empty, display an assertive Early Adopter B2B prompt: *"Be the first, overtake your competition. Become our first partner and secure all our products for life at cost price."* with a CTA. This component will be implemented both on the `/api-solutions` page and directly on the main index Homepage as part of this task.

---

## ⚖️ L. Strategic Governance & Licensing Harmonization #strategy #legal
*Note: Development of the API Solutions showcase is temporarily paused while we establish the foundational legal and authorship barriers for the Lineum project.*

- [ ] **L.1 Authorship & Cite-ability Consolidation**
    - Ensure ORCID (`0009-0003-4026-7164`) is injected consistently across `CITATION.cff`, `zenodo.json`, the Whitepapers, and the Portal Footer.
    - Synchronize "Lineum Core" as the engine package name vs "Lineum" as the brand name across all files (`README.md`, `LICENSE`, etc.).
- [ ] **L.2 License Overhaul (MIT -> AGPLv3)**
    - Execute the planned shift of the core mathematical engine from MIT to AGPLv3 to establish the true open-core boundary and prevent closed-source corporate wrapping.
- [ ] **L.3 SaaS Boundary & Monorepo Separation**
    - Address the architectural mixing of Proprietary SaaS API code (`routing_backend/main.py`) and the AGPL Engine (`lineum_core`). Establish a formal API boundary or repository split to avoid license contamination.
- [ ] **L.4 Acceptable Use & Ethical ToS**
    - Draft and integrate a Terms of Service/Responsible Use policy specifying forbidden API usage (military swarm drones, malicious market HFT, etc.).
- [ ] **L.5 Trademark & Brand Protection**
    - Create a basic Trademark Policy defining the usage of the "Lineum" name and logo for third-party wrappers.

---

## 🌐 R. Portal and Infrastructure (Future Milestones)

This section contains tasks related to the web presentation and technical background of the project that are not critical to the model but are necessary for public deployment.

- [x] Add link to the Laboratory in the main Portal menu
- [ ] **Access Security (Gatekeeper)**:
    - Implement JWT-based logins on the Portal.
    - Create a proxy layer for the Laboratory that will require a valid token for access to JSON data.
    - Define roles (Auditor, Scientist) and restrict the visibility of diagnostic data.
- [ ] **Configuration and Secrets Management**:
    - Move from local `.env` files to remote management (e.g. DigitalOcean App Platform Secrets).
    - Ensure no sensitive keys or private URLs are in the Git repository.
- [ ] **Hosting and Deployment**:
    - Choose and set up final hosting (DigitalOcean / Vercel / Cloudflare).
    - Set up a CI/CD pipeline for automatic deployment after push to `main`.

> [!NOTE]  
> Specific frontend tasks and Portal technical details are tracked locally in [portal/README.md](file:///c:/Users/Tomáš/Documents/GitHub/lineum-core/portal/README.md).

---

## 🚀 Commercial Roadmap: Future Domain Applications
The portal's `api-solutions` section currently showcases Routing dynamics (traffic, evacuation, hardware traces). Based on the underlying physics engine capabilities (Lineum as a universal PDE solver), we need to expand the B2B showcases to demonstrate the full potential of continuous field dynamics.

- [ ] **Aerodynamics & Fluid Dynamics:** Create a demo showcase illustrating airflow optimization inside jet engines or fluid dynamics in pipelines.
- [ ] **Reactor Physics:** Add a visualization for radiation propagation or thermal dissipation in complex enclosed environments.
- [ ] **Structural Mechanics:** Implement an API example showing stress distribution, structural integrity, and material failure under pressure.
- [ ] **Economic Routing:** Develop a demo illustrating supply chain optimization and the flow of capital/resources around global bottlenecks.
- [x] **Portal Integration:** Embed a layman "True Potential" explainer section on the main `/api-solutions` page to explicitly state that Routing is just the beginning of the engine's capabilities.
