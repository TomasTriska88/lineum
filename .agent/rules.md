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
