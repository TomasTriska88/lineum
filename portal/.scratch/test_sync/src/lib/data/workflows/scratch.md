---
description: Convention for temporary/diagnostic scripts — always use .scratch/ directory
---

# Scratch Directory Convention

## Rules

1. **All temporary helper scripts** (diagnostics, one-off analysis, debug tools, verification scripts) MUST be created in `.scratch/` — **never in the project root**.

2. **Examples of scratch files**: `inspect_checkpoint.py`, `find_max.py`, `smoke_test.py`, `verify_*.py`, `debug_*.py`, `extract_*.py`, any ad-hoc script that isn't part of the permanent codebase.

3. **At the end of a task** (before the final `notify_user`), check if `.scratch/` contains any files and **offer to clean them up**.

4. **Permanent test files** like `test_output_structure.py` do NOT go in `.scratch/` — only throwaway helpers.

5. `.scratch/` is in `.gitignore`, so even if cleanup is forgotten, nothing leaks to the repo.

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
Remove-Item -Path .scratch/* -Force -ErrorAction SilentlyContinue
```
