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
   - `LINEUM_AUDIT_PROFILE = "whitepaper_core"` (Locked canonical profile)
   - `LINEUM_BASE_OUTPUT_DIR = "output_wp"` (Strictly for audit/whitepaper runs)
   - `LINEUM_RUN_ID = "6"` (Canonical audit run ID)
   - `LINEUM_RUN_MODE = "false"` (Standard run mode)
   - `LINEUM_SEED = "41"` (Deterministic seed)
   - `LINEUM_STEPS = "2000"` (Explicit step lock)
   - `LINEUM_TEST_EXHALE_MODE = "true"` (Active trace analytics)
   - `LINEUM_RESUME = "false"` (Always fresh from step 0)

## 3. Optional Data Lock
To verify kappa map integrity, you may set:
   - `LINEUM_EXPECTED_KAPPA_MAP_HASH = "..."` 

## 4. Execution
   ```powershell
   python lineum.py
   ```
