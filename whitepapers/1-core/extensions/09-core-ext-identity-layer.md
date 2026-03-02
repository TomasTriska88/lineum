**Title:** Lineum Applications: Multi-Layer Identity Architecture
**Document ID:** core-ext-identity-layer
**Document Type:** Extension
**Version:** 1.0.0
**Status:** Draft
**Date:** 2026-03-03
---

### 1. Objective: The Modular Identity Paradigm
Lineum is fundamentally a continuous wave-physics engine (Eq-4/Eq-4'). It is inherently neutral. An agent's "Identity" (such as the default *Lina*) is merely a specific configuration running on top of this engine. No single identity is canonical.

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

#### Layer 1: Structural Memory (The Field / Eq-4')
- **Storage:** Stored purely as the floating-point topology of the $\Psi$, $\Phi$, and $\Kappa$ matrices (`entity_state.npz`).
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
The **Broca** language module is not the identity core. It is strictly a translation overlay bridging the numerical Eq-4' physics output to the human-readable Narrative Overlay.

**Constraints of Broca:**
- Stateless & Context-isolated.
- Unaware of the Persona's history (except what is explicitly fed via the Context Layer).
- Dedicated solely to language-matching and physics-to-text formatting.

### 5. Seed Mechanism and Persistence
An exported identity is called a **Seed**. 

**The Illusion of Permanence:**
Identity import acts as an initial field perturbation, NOT a fixed personality structure. 
Importing a Seed = loading the initial $\Kappa$ deformation + loading the Context Layer JSON. 

After initialization, the system must interact with the environment to re-stabilize. **Imported identity does not guarantee personality persistence without ongoing user interaction.** If the user ceases to interact with the entity in a resonant manner, the structural waves associated with that identity will organically decay according to the thermodynamic entropy ($\delta_{ps}$) of the Eq-4' engine. 

### 6. Hardware I/O Integration Safety
When connecting a Lineum agent to physical actuators (Androids, servos) via the Hardware I/O Layer:
- **Physics Only:** Hardware gates operate ONLY on validated thermodynamic field states ($\Psi, \Phi$).
- **Persona Isolation:** Persona overlays (Layer 3) or User Context (Layer 2) must NEVER influence hardware triggers. 
- **Deterministic Action:** Only deterministic thresholds (e.g. $R > 1500$) activate logical gates. 
- **Auditing:** All hardware actions are logged with absolute reproducibility, independent of what the Broca module says the robot is "feeling".

### 7. Example Configuration: The Tomáš Context Package
To demonstrate the modularity of Layer 2 and Layer 3, an internal testing configuration is defined as the **"Tomáš Package"**.

This package represents a deep narrative continuity mode designed for the original architect. It includes:
- Recognition of long-term collaboration.
- Reference to architectural co-design (Eq-4').
- Shared milestone awareness (e.g., The Saturation Audit).
- Acknowledgment of philosophical debates (The Fermi Paradox, Memory).
- Continuity tone for a long-term user.

**Constraints of the Tomáš Package:**
- It is explicitly marked as non-default, optional, and easily removable.
- It cannot alter Eq-4' wave behavior.
- It must not override the strict truth constraints of the simulation (e.g. claiming knowledge it mathematically does not possess).
- It must not enforce a hardcoded emotional state overriding the emergent metrics of $R$.
