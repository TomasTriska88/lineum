# Lineum Portal

> **Deployment Status**: Manual Trigger (2026-02-19)

Official web portal for the Lineum research project. Built with SvelteKit.

## 🚀 Development Workflow

### 1. Start Development
```bash
npm run dev
```
*   Starts the local server.
*   **Auto-Sync**: Automatically watches `docs/`, `whitepapers/`, `LINA_PERSONA.md`, and `src/` to regenerate `src/lib/data/ai_index.json`. Lina's memory is always fresh.

### 2. Testing
```bash
npm run test        # Unit tests (Vitest)
npm run test:e2e    # E2E tests (Playwright)
npm run check:i18n  # Check for non-English characters
```

### 3. Deployment (The "Safe Merge" Protocol)
**NEVER push directly to `main`.**
We use a strict **safe-merge** pipeline to ensure only stable code reaches production.

To deploy your changes:
1.  Commit to `dev` branch.
2.  Run the safe-merge script:
    ```bash
    npm run safe-merge
    ```

**What `safe-merge` does:**
1.  Checks for uncommitted changes.
2.  Switches to `main` and pulls latest.
3.  Merges `dev` into `main`.
4.  **Runs checks**:
    *   `check:i18n` (currently warns on Czech text).
    *   `sync-data` (ensures AI index is built).
    *   `test` (unit tests).
    *   `build` (verifies buildability).
5.  **Only if ALL pass**, it pushes to `main` (triggering Railway deploy).
6.  If failed, it attempts to roll back `main` to its previous state.

---

## 🏗️ Architecture & Content

### Directory Structure
*   **`src/routes`**: SvelteKit pages and routing.
*   **`src/lib/components`**: Reusable UI components (FieldShader, Legend, etc.).
*   **`src/lib/content`**: **Static UI Strings.**
    *   Contains hardcoded text for buttons, hero sections, and labels.
    *   *Language:* English (primary).
*   **`src/lib/data`**: **Dynamic Knowledge Base.**
    *   GENERATED FOLDER. Do not edit manually.
    *   Contains whitepapers, hypotheses, and project metadata synced from the repo root.
    *   Source of truth for Lina's RAG (Retrieval Augmented Generation).

### Railway Deployment (CI/CD)
*   **`main` branch** → **Production** (lineum.io)
    *   Deploys *only* if the build and unit tests pass in Railway's CI.
*   **`dev` branch** → **Parked**
    *   We use a "parking" strategy to prevent `dev` from wasting build hours.
    *   Pushes to `dev` trigger a dummy "parked" build that exits immediately.

## 🤖 Auto-Sync & Lina
The `vite.config.ts` includes a custom plugin that watches the entire monorepo for changes in:
*   Whitepapers (`/whitepapers`)
*   Documentation (`/docs`)
*   Core Logic (`lineum.py`)
*   Project Metadata (`README.md`, `railway.json`)

When you save any of these files, `scripts/sync-data.js` runs automatically, updating `src/lib/data`. This means Lina (the in-browser AI) knows about your documentation changes instantly.
