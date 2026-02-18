# Contributing to Lineum Core

> **🤖 AI AGENT NOTICE:** Before engaging in communication tasks (emails, reports, posts), YOU MUST READ `docs/communication_manual.md`.

## Research Integrity
Lineum is a rigorous scientific project. All contributions must adhere to the following principles:

1.  **Reproducibility:** No code changes without verifying reproducible seeds.
2.  **No Temporary Tests:** Use `pytest` or persistent validation scripts. Diagnostic scripts should be kept in `.scratch/`.
3.  **Clean Code:** Follow the existing style. Type hints are mandatory for core physics logic.

## Workflow
1.  **Fork & Branch:** Create feature branches.
2.  **Test:** Run `pytest tests/` before pushing.
3.  **PR:** Describe your changes and the hypothesis being tested.
