# Lineum Orchestration Rules

## 1. Audit Run (Generation)
- **Objective:** Generate fresh simulation data and evidence.
- **Trigger:** Explicit request to run a new simulation or update audit evidence.
- **Workflow:** Use `lineum.py` with `LINEUM_AUDIT_PROFILE="whitepaper_core"`.
- **Target:** Always writes to `output_wp/runs/` in a new timestamped folder.
- **Constraint:** NEVER modify or overwrite existing run folders in `output_wp`.

## 2. Whitepaper Output Update (Orchestration)
- **Objective:** Update the verification suite and metrics for documentation based on *existing* audit runs.
- **Trigger:** Request to "regenerate whitepaper outputs" or "update whitepaper metrics".
- **Workflow:** Use `tools/whitepaper_contract.py` (often via `tools/whitepaper_check.py`).
- **Target:** Updates `output_wp/runs/_whitepaper_contract/whitepaper_contract_suite.json`.
- **Constraint:** 
    - NEVER run a new simulation (`lineum.py`).
    - NEVER copy files to `output/` unless explicitly asked for a physical export.
    - Treat existing data in `output_wp/runs/<TAG>_<TS>/` as read-only.

## 3. Directory Purposes
- `output_wp/`: Canonical audit repository. Contains raw evidence.
- `output_wp/runs/_whitepaper_contract/`: Verification suite reports.
- `output/`: (Legacy/Export only) Used for web-previews or CI snapshots. DO NOT use as primary target.
- `contracts/`: Ground truth for metric acceptance bands.
