---
description: How to debug hanging and failing Playwright tests, and rules for test reliability
---

When a Playwright test hangs or times out without a clear error in the Lineum repo, follow these rules:

## 1. Rules for Stable Locators
- **Avoid Text-Only Locators:** Text can be dynamic, subject to i18n changes, or split across HTML nodes. Instead of `page.locator('text=VALIDATE')`, use explicit robust structure based locators with testing attributes or roles, like `page.getByRole('button', { name: 'Validation Core' })` or CSS classes that map directly to the element's container (`.mode-switcher`).
- **Use Actionability Checks:** Rely on auto-waiting. Actions like `.click()` automatically wait for the element to be visible, stable, enabled, and to receive events. Do not use `.click({ force: true })` unless the UI is purposefully hidden but functioning.
- **Provide Explicit Timeouts for Heavy Renders:** 
  If you expect a major UI change or heavy render (like the 3D simulator loading), provide an explicit timeout to the assertion rather than hanging the default timeout:
  `await expect(page.locator('.canvas-container > canvas')).toBeVisible({ timeout: 15000 });`
- **Wait for Canvas:** When testing the 3D Engine, always ensure the canvas is fully mounted *before* triggering evaluation hooks (`page.evaluate`), otherwise, you are testing a suspended or non-existent context.

## 2. Debugging Heuristics (When Things Break)
1. **Use the HTML report or JSON reporter over raw stdout logs**
   If a background test fails or hangs on the terminal, do not pipe the output into a `.txt` file (`> log.txt`), as ANSI escape codes make it unreadable.
   Use the JSON reporter: `npx playwright test tests/your-test.spec.js --reporter=json > .scratch/playwright-report.json`, then investigate the JSON file.
2. **Never leave zombie processes**
   If a Playwright test hangs, make sure to terminate the running processes explicitly to free up ports and memory before proceeding with other tasks.
3. **Use the Playwright Inspector when possible**
   If tests are failing silently or timing out:
   `npx playwright test --debug tests/your-test.spec.js`
