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

## 5. Permission Protocol
- **Strict Permission for Git**: The agent MUST NEVER perform `git push` or `git commit` without explicit permission from the USER for each specific set of changes.
- **Auto-run Permission**: The agent is encouraged to use `SafeToAutoRun: true` for non-destructive commands (e.g., `npm test`, `python script.py`, `ls`, `git status`) to minimize user interruptions. User approval is still required for Git mutations unless specified otherwise.
- **Verification First**: Before requesting permission to commit, the agent should verify the changes via automated tests and provide a clear summary of what will be committed.

## 6. Task Tracking Protocol (TODO Sync)
- **Dual Context Check**: Any agent working on the project MUST check both the **central** `todo.md` in the root directory and **local** project READMEs/TODOs (e.g., `portal/README.md`, `lab/README.md`).
- **Central vs. Local**: 
    1. **Central `todo.md`**: High-level milestones (Epics) and cross-component dependencies.
    2. **Local documentation**: Granular technical tasks, UI/UX bugs, and specific implementation details for that directory.
- **Cross-linking**: Always ensure that relevant sections in the central `todo.md` link to the corresponding local documentation for deeper details.

## 7. Architecture Synchronization
- **Living Document**: The `portal/ARCHITECTURE.md` is a living document.
- **Mandatory Update**: Whenever infrastructure (hosting, domains, automation) or core architectural patterns change, the agent MUST immediately update `portal/ARCHITECTURE.md` to reflect the new state.
- **Bilingual Context**: While the interaction language may be Czech, the architecture documentation must be maintained in **English** for technical clarity.
