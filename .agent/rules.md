# Project Rules and Intent

These rules govern agent behavior and documentation standards for the Lineum Core project.

## 1. Interaction Language
- **Mirror User Language**: If the user addresses the agent in Czech, the agent must respond in Czech.
- **Bilingual Context**: While interaction may be in Czech, technical implementation details and instructions should remain clear and professional.

## 2. Documentation Standards
- **English-Only Whitepapers**: All content in the `whitepapers/` directory must be strictly in **English**. 
- **Reasoning**: To maintain international auditability and academic consistency.
- **Naming Consistency**: Use canonical file names as referenced in the documentation (e.g., `tools/whitepaper_contract.py`).

## 3. Audit Integrity
- **Frozen Core**: The canonical simulation settings (RUN_ID=6, etc.) are frozen for v1.0.x. Any changes to the audit gate logic must be reflected in both `lineum.py` and the whitepapers.
- **Full Audit Trail**: For all audit runs (output in `output_wp/`), the agent MUST commit the **full content** of the run directory. Manual filtering of log or data files is strictly forbidden to ensure total audit transparency. Always use `git add output_wp/` before committing audit evidence.
## 4. Laboratory Protocol
- **Non-binding Hypothesis testing**: All work within the `lab/` directory is strictly for testing hypotheses and is not considered part of the core production codebase until audited.
- **Hypothesis Sources**: Hypotheses can be drawn from `todo.md` and `whitepaper-old/` (note: `whitepaper-old/` is legacy documentation and may be unreliable).
- **Sources of Truth**: All binding decisions and actual system state must be based on:
    1. The current whitepaper in the `whitepapers/` folder.
    2. The most recent audit runs located in the `output_wp/` folder.
- **Cross-Thread Awareness**: The agent must maintain this protocol even when switching between different conversation threads or laboratory tasks.
