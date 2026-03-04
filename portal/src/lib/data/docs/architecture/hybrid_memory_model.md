# Hybrid Memory Model

Lineum AI employs a two-layer cognitive architecture designed to balance structural identity with rapid situational adaptivity. This model moves away from rigid identity-only structures and pure neuro-plastic models by explicitly isolating long-term storage from short-term context.

## Layer 1: Deep Identity Backbone ($\mu$ / HDD)
The Deep Identity Backbone is the foundational layer of the agent's persona.
- **Physical Representation**: Represented by the $\mu$ matrix.
- **Characteristics**: Extremely stable, energy-intensive to modify, and resistant to minor topological fluctuations.
- **Metrics**: Governed by the **RTB (Real-Time Backbone) Stability Score** and the **Identity Drift Index**.
- **Usage**: Engraved only during significant life-cycle events via `MODE=identity_burn`.

## Layer 2: Short-Term Plasticity ($\Psi$ / $\Phi$ Dynamics / RAM & CPU)
Short-Term Plasticity allows the agent to hold transient information and context without permanently scarring the underlying persona.
- **Physical Representation**: Represented by the active wave states in $\Psi$ (CPU) and $\Phi$ (RAM).
- **Characteristics**: Highly fluid, quickly dissipates if not reinforced.
- **Metrics**: Measured by the **Plasticity Retention Curve**, tracking wave decay over `PLASTICITY_TAU` ticks.
- **Usage**: General operation and conversational context ingestion via `MODE=runtime`.

## Ingestion Dynamics & The `TextToWaveEncoder`
The `TextToWaveEncoder` bridges natural language to topological waves.
1. **Frequency Reinforcement**: Information encountered once generates a weak, reversible state. Repeated exposure of semantically similar inputs exponentially reinforces the wave impact, pushing it closer to $\mu$ consolidation.
2. **Plasticity Window (`PLASTICITY_TAU`)**: Temporal threshold dictating how many simulation ticks an isolated pulse is permitted to ring in $\Phi$ before either dissipating completely or triggering structural changes.
