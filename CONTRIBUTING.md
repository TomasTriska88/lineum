# Contributing to Lineum Core

> **🤖 AI AGENT NOTICE:** Before engaging in communication tasks (emails, reports, posts), YOU MUST READ `docs/communication_manual.md`.

## Research Integrity
Lineum Core is a rigorous scientific project. All contributions must adhere to the following principles:

1.  **Reproducibility:** No code changes without verifying reproducible seeds.
2.  **No Temporary Tests:** Use `pytest` or persistent validation scripts. Diagnostic scripts should be kept in `.scratch/`.
3.  **Clean Code:** Follow the existing style. Type hints are mandatory for core physics logic.

## Workflow
1.  **Fork & Branch:** Create feature branches.
2.  **Test:** Run `pytest tests/` before pushing.
3.  **PR:** Describe your changes and the hypothesis being tested.

## Legal & IP Protection (DCO / CLA)
Lineum Core is currently under strict intellectual property control. **At this time, we do NOT accept any external Pull Requests that fail to include a valid Developer Certificate of Origin (DCO) or Contributor License Agreement (CLA).**

While technical enforcement (e.g., automated CI blocks) is not yet universally active on this repository, this rule applies legally to all code, documentation, and assets submitted. If you plan to submit a contribution, you must be prepared to assert that you have the right to submit the work and agree to license it under the inbound terms required by the project.

To comply with the DCO, simply use the `-s` flag when committing your code via git:
```bash
git commit -s -m "feat: added emergent memory bounds"
```
