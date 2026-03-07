# Lineum Lab UX Canon: The "Dual-Audience" Principle

**Core Rule:** The Lab must be instantly comprehensible to a layperson within 10 seconds, while simultaneously providing unambiguous technical depth for researchers, preventing any conflation of concepts.

Every major concept in the Lab MUST feature two distinct layers of explanation, plus a usage context:

1.  **"Human" Layer:** 1 sentence, completely accessible, everyday language.
2.  **"Scientific" Layer:** 1 sentence, technically precise, physically rigorous.
3.  **"When to use":** 1 short line indicating the practical application.

## Application in UI

### 1. Operation Modes (Ultra-Clear Distinction)
*   **VALIDATE (Safe Presets):**
    *   *Human:* "Technical check — reproducible results."
    *   *Scientific:* "Locked presets + manifest + validation-grade."
    *   *When:* "Use when you compare changes."
    *   *UI Requirement:* Always display badge **"Validation-grade (reproducible)"**.
    *   **PASS/FAIL verdict** shown after every run (machine-checked expectations).
*   **EXPLORE (Unlocked):**
    *   *Human:* "Sandbox — you might break stability."
    *   *Scientific:* "Free params + warnings, not validation-grade."
    *   *When:* "Use when hunting phenomena."
    *   *UI Requirement:* Always display watermark **"Exploratory (not validation)"**.

### 2. Scenario Nomenclature
Must display all 3 lines in the UI picker:

*   **Wave Sanity (T0/T1)**
    *   *Human:* "Check if the 'Wave engine' is healthy."
    *   *Scientific:* "Unitary/norm conservation sanity vs diffusion."
    *   *When:* "After any physics/core change."
*   **Hydrogen Validation Mini**
    *   *Human:* "Can it sustain the 'atomic cloud' around the nucleus?"
    *   *Scientific:* "ITP ground state + unitary hold (2D soft Coulomb analog)."
    *   *When:* "To confirm bound-state capability."
*   **μ Regression Snapshot**
    *   *Human:* "Does the memory (μ) stay sane in wave mode?"
    *   *Scientific:* "Compare μ dynamics: diffusion vs wave_projected_soft."
    *   *When:* "After any ψ physics change."
*   **Single-particle Bound-state Analogs**
    *   *Human:* "Playground for tracing 'single cloud' shapes in a potential."
    *   *Scientific:* "Single-particle Schr analogs (NOT multi-electron chemistry)."
    *   *When:* "For exploration and hypothesis testing."

### 3. Expectation Checker (P3 Gate)
Every VALIDATE scenario carries `expectations[]` objects (defined in `validation_core.py`):
```json
{ "metric": "edge_mass_cells", "op": "<", "value": 0.10, "label": "Edge mass below 10%" }
```
After execution: `evaluate_expectations()` → `expectation_results[]` + `overall_pass`.
Frontend renders checklist only. **0% math in frontend.**

### 4. Particle Presets (Safe Defaults + FIX Policy)
| Preset | Z | dt | eps | Grid | FIX Policy |
|--------|---|----|-----|------|------------|
| H-like | 1.0 | 0.05 | 0.1 | 64 | Auto-halve dt |
| He-like | 2.0 | 0.02 | 0.1 | 64 | Auto-halve dt |
| C-like | 6.0 | 0.005 | 0.1 | 64 | Auto-halve dt |
| O-like | 8.0 | 0.002 | 0.1 | 64 | Auto-halve dt |

### 5. Progressive Disclosure (Tooltips)
*   Tooltips must start short and jargon-free.
*   Must include a visual "Learn more" to reveal advanced technical definitions.

### 6. Run History
*   Every run saved with full manifest (config, git, seed, expectations, overall_pass).
*   **Load** = view past results. **Rerun** = re-execute with same config, fresh run_id.
*   PASS/FAIL badges visible in history cards without loading full data.
