---
description: Convention for temporary/diagnostic scripts — always use .scratch/ directory
---

# Scratch Directory Convention

## 🚨 HARD ENFORCEMENT FOR THE AGENT 🚨
You (the AI Agent) are strictly forbidden from placing ANY non-source-code files in the project root paths (`repo/`, `portal/`, `lab/`, `marketing/`, `docs/`). 
1. **Tool Parameter Block:** Before executing the `run_command` tool, if your `CommandLine` string contains a redirect operator (`>` or `>>`) or an output flag (`-o`, `--output`, `--reporter=json`), you MUST prepend `.scratch/` to the target file path.
2. **Mental Check:** "Is this a `.txt`, `.json`, `.log`, `.zip`, `.py` diagnostic script or output? Yes -> it goes in `.scratch/`."
3. **No Exceptions:** Do not apologize later for forgetting. Intercept your own tool parameters before execution.

## Rules

1. **All temporary helper scripts** (diagnostics, one-off analysis, debug tools, verification scripts) MUST be created in `.scratch/` — **never in the project root**.

2. **Examples of scratch files**: `inspect_checkpoint.py`, `find_max.py`, `smoke_test.py`, `verify_*.py`, `debug_*.py`, `extract_*.py`, any ad-hoc script that isn't part of the permanent codebase.

3. **At the end of a task** (before the final `notify_user`), check if `.scratch/` contains any files and **offer to clean them up** or run the turbo cleanup script below.

4. **Permanent test files** like `test_output_structure.py` do NOT go in `.scratch/` — only throwaway helpers.

5. `.scratch/` is in `.gitignore`, so even if cleanup is forgotten, nothing leaks to the repo.

6. **Terminal Logs**: When running diagnostic terminal commands (e.g. `pytest > fail.log` or `vitest --reporter=json > out.json`), NEVER output the result into the project root. Always route it to the scratch directory:
   - ✅ Correct: `pytest > .scratch/fail_log.txt`
   - ❌ Wrong: `pytest > fail_log.txt`

## How to use

```python
# When creating a temp script:
# ✅ Correct
write_to_file(".scratch/inspect_checkpoint.py", ...)

# ❌ Wrong
write_to_file("inspect_checkpoint.py", ...)
```

## Cleanup

// turbo
```powershell
# At end of task, clean up:
Remove-Item -Path .scratch/* -Force -Recurse -ErrorAction SilentlyContinue
```
