---
description: How to execute a canonical whitepaper audit run for Lineum Core
---

To ensure a deterministic and audit-proof whitepaper run, follow these rules exactly:

# // turbo-all

## 1. Clean Environment
Before execution, ALWAYS clear all LINEUM variables to prevent leakage from previous sessions:
   ```powershell
   Get-ChildItem Env: | Where-Object { $_.Name -like "LINEUM_*" } | ForEach-Object {
       Remove-Item ("Env:" + $_.Name) -ErrorAction SilentlyContinue
   }
   ```

## 2. Canonical Settings
Set these exact variables (and NO others) to lock the audit profile:
   - `LINEUM_BASE_OUTPUT_DIR = "output_wp"` (Strictly for audit/whitepaper runs)
   - `LINEUM_RUN_ID = "6"` (Canonical audit profile)
   - `LINEUM_RUN_MODE = "false"` (Core audit mode)
   - `LINEUM_SEED = "41"` (Deterministic seed)
   - `LINEUM_STEPS = "2000"` (Explicit step lock)
   - `LINEUM_RESUME = "false"` (Always fresh from step 0)

## 3. The "Latest" Rule
> [!IMPORTANT]
> **NEVER** set any version or commit-related environment variables (e.g., `LINEUM_VERSION`) manually. 
> The system must automatically capture code fingerprints and git metadata from the source code itself to ensure provenance.

## 4. Execution
   ```powershell
   python lineum.py
   ```
