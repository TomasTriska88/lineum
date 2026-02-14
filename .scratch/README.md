# Scratch Directory

This directory is designated for **temporary**, **diagnostic**, and **reproduction** scripts.

## Rules for AI Agents
1.  **ALWAYS** create temporary reproduction scripts (e.g., `repro_issue.py`) in this directory, NOT in the project root.
2.  **ALWAYS** write temporary output logs (e.g., `debug_output.txt`) to this directory.
3.  **NEVER** commit files from this directory to version control (ensured by `.gitignore` in root or here).
4.  Reference files in this directory using relative paths, e.g., `python .scratch/repro_issue.py`.

## Maintenance
Files in this directory are transient and may be deleted at any time to clean up the workspace.
