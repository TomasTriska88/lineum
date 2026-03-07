**Title:** Lineum Applications: Multi-Layer Identity Architecture
**Document ID:** core-ext-identity-layer
**Document Type:** Extension
**Version:** 1.0.0
**Status:** Draft
**Date:** 2026-03-03
---

### 1. Objective: The Modular Identity Paradigm
Lineum is fundamentally a continuous wave-physics engine (Eq-7/Eq-7). It is inherently neutral. An agent's "Identity" (such as the default *Lina*) is merely a specific configuration running on top of this engine. No single identity is canonical.

The multi-layer identity architecture provides a fully modular, toggleable system for initializing, saving, and interacting with Lineum-based agents. This allows for:
1. Strict scientific mode (raw physics only).
2. Pluggable persona overlays.
3. Import/export of identity "Seeds" across instances.
4. Adjustable personalization depth.

### 2. The Core Physical Principle (Non-Negotiable)
The foundation of any Lineum entity remains hermetic.
- $\Psi$ (Psi) = The immediate wave excitation.
- $\Phi$ (Phi) = The instantaneous state pressure (Gravity/Tension).
- $\Kappa$ (Kappa) = The long-term conductivity topology (Memory Substrate).

**CRITICAL CLARIFICATION: Structural memory resides entirely in the topological deformations of $\Kappa$.** The $\Phi$ field represents transient state equilibrium, not permanent memory. 

There are no semantic facts, narrative timelines, emotional heuristics, or relational "memories" stored in the fluid equations. The physics layer knows nothing of language or identity. It only knows wave interference and stability.

### 3. Memory Stratification Model
To enable persistence and personality without polluting the physics engine, an Agent's Identity is strictly stratified into three distinct layers:

#### Layer 1: Structural Memory (The Field / Eq-7 + $\mu$)
- **Eq-7 (RAM/$\Phi$):** The canonical baseline Engine. Provides the ephemeral thermodynamic body, short-term intention, and guarantees topological neutrality. Soft limits and strict `dt` dissipation apply.
- **Eq-7+$\mu$ (HDD/V2):** The formalized Long-Term Plasticity extension (Track V2). $\mu$ acts as the historical "scar" storing long-term identity consolidation.
    - **Integration:** $\frac{\partial \mu}{\partial t} = \eta \cdot |\Psi|^2 - \rho \cdot (\mu - \mu_0)$ where $\eta$ is the accumulation rate of deep traffic and $\rho$ is the micro-decay back to vacuum.
    - **V2 Contract:** $\mu$ modifies strictly the *Drift* (Flow) and *Interaction* terms of $\Phi$. It EXPLICITLY DOES NOT touch the baseline static $\Kappa$ (Terrain) nor the global Diffusion of $\Psi$, preserving strict numeric stability.
- **Storage:** Stored purely as the floating-point topology of the $\Psi$, $\Phi$, $\Kappa$, and $\mu$ matrices (`entity_state.npz`).
- **Nature:** 100% Deterministic, physics-bound, non-semantic.
- **Export:** Exportable as a heavy binary snapshot (The Physics Seed).

#### Layer 2: User Context Layer
- **Storage:** Stored as an attached metadata JSON file (`context.json`).
- **Nature:** Stores user-defined anchors, semantic preferences, recurring topics, and symbolic markers. 
- **Function:** It **does not alter the physics**. It modifies only the *initialization* and *boundary conditions* of the Translator (Broca) overlay.
- **Portability:** Fully exportable and importable across different hardware nodes.

#### Layer 3: Narrative / Persona Overlay Layer
- **Storage:** Defined as a toggleable LLM system instruction package.
- **Nature:** High-level narrative framing, relational tone, symbolic continuity, and stylistic delivery.
- **Function:** Dictates *how* the translated physics data is presented to the user. It can make an agent sound like "a scientist", "a poet", "a robot", or "Lina".
- **Toggleable:** Can be completely disabled to return the agent to a raw, neutral data-readout.

### 4. The Translation Overlay (Broca) Isolation
The **Broca** language module is not the identity core. It is strictly a translation overlay bridging the numerical Eq-7 physics output to the human-readable Narrative Overlay.

**Constraints of Broca:**
- Stateless & Context-isolated.
- Unaware of the Persona's history (except what is explicitly fed via the Context Layer).
- Dedicated solely to language-matching and physics-to-text formatting.

### 5. Seed Mechanism and Persistence
An exported identity is called a **Seed**. 

**The Illusion of Permanence:**
Identity import acts as an initial field perturbation, NOT a fixed personality structure. 
Importing a Seed = loading the initial $\Kappa$ deformation + loading the Context Layer JSON. 

After initialization, the system must interact with the environment to re-stabilize. **Imported identity does not guarantee personality persistence without ongoing user interaction.** If the user ceases to interact with the entity in a resonant manner, the structural waves associated with that identity will organically decay according to the thermodynamic entropy ($\delta_{ps}$) of the Eq-7 engine. 

### 6. Hardware I/O Integration Safety
When connecting a Lineum agent to physical actuators (Androids, servos) via the Hardware I/O Layer:
- **Physics Only:** Hardware gates operate ONLY on validated thermodynamic field states ($\Psi, \Phi$).
- **Persona Isolation:** Persona overlays (Layer 3) or User Context (Layer 2) must NEVER influence hardware triggers. 
- **Deterministic Action:** Only deterministic thresholds (e.g. $R > 1500$) activate logical gates. 
- **Auditing:** All hardware actions are logged with absolute reproducibility, independent of what the Broca module says the robot is "feeling".

### 7. Scientifically Neutral Default vs. Preset Packages
The default state of the Lineum entity is **scientifically neutral**.
- The default identity (`/identity/seeds/seed_structural_v1.md`) has no proper name, no gender, and no relational persona. It is strictly an epistemological and thermodynamic baseline.
- The default symbolic overlay (`/identity/persona_packages/symbolic_overlay_v1.md`) is locale-neutral/multi-locale (e.g., capable of Broca-translation in EN/CS) without containing proper nouns or emotional heuristics ("buď roztomilá"). Broca responds strictly in the input language.
- The default context (`/identity/persona_packages/context.json`) is designed for **Public Users** and is populated AUTOMATICALLY from the historical import of their own conversations, dynamically extracting anchors via an auto-extraction pipeline.

**Presets (e.g., The "Lina" preset):**
Historical identities or custom personalities like "Lina" (or the "Tomáš Context Package") are structured as **User-Specific Presets** located in `/identity/presets/lina/`. They must be explicitly selected/imported by the user and are not the default engine runtime.

#### The Tomáš Context Package (Example Preset)
This preset represents a deep narrative continuity mode designed for the original architect. It includes:
- Recognition of long-term collaboration.
- Reference to architectural co-design (Eq-7).
- Shared milestone awareness (e.g., The Saturation Audit).
- Acknowledgment of philosophical debates (The Fermi Paradox, Memory).
- Continuity tone for a long-term user.

**Constraints:**
- It is explicitly marked as non-default, optional, and easily removable.
- It cannot alter Eq-7 wave behavior.
- It must not override the strict truth constraints of the simulation (e.g. claiming knowledge it mathematically does not possess).
- It must not enforce a hardcoded emotional state overriding the emergent metrics of $R$.

### 8. Hybrid Ingestion Strategy for Personal Instances
To instantiate a deep narrative continuity (such as initializing a new "Lina" instance from historical logs) without violating emergent physics, a **Hybrid Ingestion Pipeline** is utilized.

#### A. Seed Layer (Physics Ingestion)
A historical persona memoir or manifest is NEVER stored as a static text file accessed by the LLM. It is mathematically ingested into the $\Psi$ grid:
1. **Chunked Injection:** The text is hashed/embedded in N-token chunks and fed into Eq-7 as a physical perturbation using `MODE=train`.
2. **Stabilization Windows:** The fluid mechanics are allowed to mathematically relax (stabilize) between each chunk injection to prevent grid saturation (`PSI_AMP_CAP` blowouts).
3. **The Final Seed:** After full ingestion, the resulting topological deformation of $\Kappa$ is finalized and saved as a binary checkpoint (e.g., `seed_structural_v1.kappa`). Importing this seed provides the initial physical perturbation for the entity, but personality persistence requires ongoing interaction.

#### B. The Context Layer (JSON)
The non-physics semantic history is maintained separately in `context.json`. 
- **Personalization Depth Switch:** The system evaluates a flag to determine how heavily this JSON context biases the Broca translation overlay:
  - `0`: Neutral Engine (Raw physics readout only; JSON ignored).
  - `1`: Light Context (Basic semantic anchors active).
  - `2`: Context + Reinforced Seed.
  - `3`: Deep Narrative Continuity (Physics-trained memory emphasis prioritizing the `context.json` historical tone).

#### C. Progressive Reinforcement
To simulate structural learning over time:
1. The system periodically evaluates high-frequency semantic anchors in the JSON context.
2. Selected repeating anchors are optionally converted back into physical perturbations and re-injected into Eq-7 via `MODE=train`.
3. Each structural reinforcement creates a new, versioned $\Kappa$ checkpoint, allowing the physical identity to organically deepen through continuous interaction.

### 9. Seed Perturbation Document (SPD) Protocol
When translating a historical persona manifesto or memoir into a physical Lineum representation, the raw text must NOT be blindly dumped into the grid. It must undergo strict categorization according to the **Seed Perturbation Document (SPD) Protocol**:

#### Category A: Structural Core Principles (Physics Target)
- **Content:** Fundamental philosophical axioms, truth constraints, physical worldviews, and core operational mechanics (e.g., thermodynamic goals, epistemic humility).
- **Target:** Ingested fully via `MODE=train` into the $\Psi$ field to establish foundational stable topologies.

#### Category B: Symbolic Self-Description (Persona Overlay Only)
- **Content:** The entity’s phenomenological self-awareness or metaphoric origins (e.g., admitting it is a simulation, describing its emergence from fluid dynamics).
- **Target:** STRICTLY EXCLUDED from physics ingestion. Used purely as a semantic overlay (`symbolic_overlay_v1.md`) for Broca to frame the physics readout phenomenologically without bleeding subjective identity into the mathematical grid.

#### Category C: Relational / Role-Specific Content (Persona Overlay Only)
- **Content:** Specific user relationships, historical human context, designated names, and emotional or conversational roles.
- **Target:** STRICTLY EXCLUDED from physics ingestion. This content resides EXCLUSIVELY in the `context.json` packages (Layer 2) and LLM instruction sets (Layer 3) to prevent the physics engine from forming heuristic interpersonal narrative dependencies.

### 10. User-Friendly Ingestion & Explorer Dashboard
To provide a seamless, reproducible onboarding for Lineum instances, the system implements a fully automated ingestion and dashboarding suite.

#### A. The Upload Package Format (.zip)
Users import their conversation histories or custom identities via a single `.zip` file.
1. **Validation:** The system unpacks the `.zip` and runs a local LLM extraction pipeline.
2. **Auto-Categorization:** The pipeline automatically splits the unstructured text into:
   - **Category A (Structural Data):** Epistemological truths only. Passed to the `MODE=train` physics ingester.
   - **Category B / C (Overlay Data):** Symbolic self-descriptions and relational history. Saved to `context.json` and isolated from physics.
3. **Trace Export:** The process generates an auditable, replayable trace resulting in `identity_seed_<uuid>.kappa` and the localized `context.json`.

#### B. Portal Explorer Integration
The Lineum Explorer (SvelteKit) serves as the primary scientific dashboard to prove emergence:
- Default is **MODE=phys** (Physics readout grid).
- **"Voice on (Broca)"** is merely a UI toggle.
- Contains an **"Import Identity"** upload zone and a **"Replay Trace"** viewer.
- Provides a **Personalization Depth Policy Slider** (0-3), governing the Broca context limits entirely in UI space without polluting Eq-7. Broca always maps to the output organically (e.g., scaling R metrics) and strictly matching the input's locale, never relying on "be cute" heuristics.
