---
description: How to release a new version of Lineum Core and sync versions
---
This workflow describes how to properly bump the version, synchronize it across the repository, and create a git release tag. 

When the user asks `/release [version]` or just `/release`, follow these steps:

0. **If the user did not specify a version**: Read the current version from `CITATION.cff`, determine the next logical patch, minor, and major version numbers, and stop to ask the user which one they want to proceed with. Once confirmed, proceed to step 1.
1. Validate that the `[version]` conforms to semver and format it to always start with `v` (e.g., `v1.1.0`).
// turbo
2. Execute the version synchronization script to update all references:
   `python tools/sync_version.py [version]`
// turbo
3. Verify the changes using `git diff`. Ensure `CITATION.cff`, `todo.md`, and any other config files have been correctly updated to the new version.
// turbo
4. Stage the modified files:
   `git add CITATION.cff todo.md tools/sync_version.py`
// turbo
// turbo
5. Commit the version bump and push `dev`:
   ```bash
   git commit -m "chore: bump version to [version]"
   git push origin dev
   ```
// turbo
6. Checkout `main` and merge `dev` into it:
   ```bash
   git checkout main
   git merge dev
   ```
// turbo
7. Create the Git tag on `main` with an annotation for the release:
   `git tag [version] -m "Release [version]"`
// turbo
8. Push the merged `main` branch and the release tags to the remote:
   ```bash
   git push origin main
   git push --tags
   ```
// turbo
9. Finally, checkout back to `dev` to ensure future work conforms to the Git Policy:
   `git checkout dev`

Finally, inform the user that the release has been successfully merged to `main`, tagged, and pushed to the remote repository, and that we are safely back on the `dev` branch.
