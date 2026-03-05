# Lineum Lab UX Canon: The "Dual-Audience" Principle

**Core Rule:** The Lab must be instantly comprehensible to a layperson within 10 seconds, while simultaneously providing unambiguous technical depth for researchers, preventing any conflation of concepts.

Every major concept in the Lab MUST feature two distinct layers of explanation, plus a usage context:

1.  **"Human" Layer:** 1 sentence, completely accessible, everyday language.
2.  **"Scientific" Layer:** 1 sentence, technically precise, physically rigorous.
3.  **"When to use":** 1 short line indicating the practical application.

## Application in UI

### 1. Operation Modes (Ultra-Clear Distinction)
*   **VALIDATE (Safe Presets):**
    *   *Human:* "Technická kontrola — reprodukovatelné výsledky."
    *   *Scientific:* "Locked presets + manifest + validation-grade."
    *   *When:* "Use when you compare changes."
    *   *UI Requirement:* Always display badge **"Validation-grade (reproducible)"**.
*   **EXPLORE (Unlocked):**
    *   *Human:* "Hřiště — můžeš rozbít stabilitu."
    *   *Scientific:* "Free params + warnings, not validation-grade."
    *   *When:* "Use when hunting phenomena."
    *   *UI Requirement:* Always display watermark **"Exploratory (not validation)"**.

### 2. Scenario Nomenclature
Must display all 3 lines in the UI picker:

*   **Wave Sanity (T0/T1)**
    *   *Human:* "Zkontroluj, že 'Wave motor' je zdravý."
    *   *Scientific:* "Unitary/norm conservation sanity vs diffusion."
    *   *When:* "After any physics/core change."
*   **Hydrogen Validation Mini**
    *   *Human:* "Dokáže to udržet 'atomový mrak' kolem jádra?"
    *   *Scientific:* "ITP ground state + unitary hold (2D soft Coulomb analog)."
    *   *When:* "To confirm bound-state capability."
*   **μ Regression Snapshot**
    *   *Human:* "Nezblázní se paměť (μ) v wave režimu?"
    *   *Scientific:* "Compare μ dynamics: diffusion vs wave_projected_soft."
    *   *When:* "After any ψ physics change."
*   **Single-particle Bound-state Analogs**
    *   *Human:* "Hřiště na tvary 'jednoho mraku' v potenciálu."
    *   *Scientific:* "Single-particle Schr analogs (NOT multi-electron chemistry)."
    *   *When:* "For exploration and hypothesis testing."

### 3. Progressive Disclosure (Tooltips)
*   Tooltips must start short and jargon-free.
*   Must include a visual "Learn more" (e.g., a dropdown arrow or secondary hover state) to reveal advanced mathematical/technical definitions.
