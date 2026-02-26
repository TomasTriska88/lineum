---
description: How to manage git branches and commits
---

# Git Policy (STRICT)

**# Git Policy (STRICT)

**CRITICAL RULE:** NEVER WORK DIRECTLY ON `main`.

1.  **BEFORE YOU WRITE ANY CODE:** Check the current branch:
    ```bash
    git branch
    ```
2.  **Switch to DEV:** If you are on `main`, STOP. Switch to `dev` immediately:
    ```bash
    git checkout dev
    ```
    (Create it if it doesn't exist: `git checkout -b dev`)

3.  **Commit & Push:** Only when you are safely on `dev` (or a feature branch), you may proceed with `git add`, `git commit`, and `git push origin dev`.
4.  **No Chaining on Windows:** DO NOT use the `&&` operator to chain Git commands together (e.g. `git add . && git commit`). Older versions of PowerShell (v5.1 and below) do not support `&&` and will throw syntax errors. ALWAYS execute commands on separate lines:
    ```bash
    git add .
    git commit -m "..."
    git push origin dev
    ```

**Correction Protocol:**
If you accidentally commit to `main` locally:
1.  `git reset --soft HEAD~1` (undo commit, keep changes)
2.  `git checkout dev`
3.  `git commit`
4.  `git push origin dev`

// turbo
5.  Check status to confirm everything is clean on dev.
