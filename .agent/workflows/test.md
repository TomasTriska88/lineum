---
description: How to run the test suite after code changes
---

# Running Tests

This project follows a strict **"No Temporary Tests"** policy. All tests must be integrated into the permanent test suites defined below.

## 1. Lineum (Python)
Located in the root directory. Tests cover physics, simulation logic, and output structure.
// turbo
```bash
pytest tests/ -v
```

## 2. Portal (Frontend/Wiki)
Located in the `portal/` directory. Tests cover Wiki loaders, metadata extraction, and asset routing.

**CRITICAL COMPONENT TESTING POLICY**: For testing Svelte UI components (especially interactive ones with DOM changes, Canvas, or complex `bind:value` reactivity), **always use Playwright over Vitest/JSDOM**. JSDOM has severe limitations with Svelte lifecycle rendering and `IntersectionObserver`. You should run end-to-end tests via Playwright instead of struggling with mocked unit tests.

> [!IMPORTANT]
> **Playwright E2E tests (`npm run test:e2e`) are now fully automated in GitHub Actions CI**.
> They will run against a headless Chromium browser instance upon every Push/PR to the `main` branch. If the E2E tests fail, the deployment to production is automatically aborted. You should run them locally before pushing if you made significant UI changes.

// turbo
```bash
cd portal
npm run test
npm run test:e2e
```

## 3. Simulacrum (Lab)
Located in the `lab/` directory. Tests cover visualization components and harmonic analysis.
// turbo
```bash
cd lab
npm run test
```

## When to run
- **Always** after any code changes.
- **Always** before committing.
- After adding new features (you MUST add a permanent test in the corresponding `tests/` or `src/.../*.test.ts` file).

## Policy: Reusable Tests
Never use temporary "scratch" or diagnostic scripts for verification if they can be implemented as a test case in the suites above. Using `.scratch/` is allowed for quick exploration ONLY, not for final verification of a task.
