import { test, expect } from '@playwright/test';

test.describe('App Initialization Smoke Test', () => {

    test('App loads without fatal console errors and renders main UI', async ({ page }) => {
        let pageErrors = [];
        let consoleErrors = [];

        // Listen for unhandled page errors (e.g., variable not defined)
        page.on('pageerror', exception => {
            pageErrors.push(exception.message);
        });

        // Listen for console errors specifically
        page.on('console', msg => {
            if (msg.type() === 'error') {
                consoleErrors.push(msg.text());
            }
        });

        await page.goto('/');

        // Wait a small amount to allow JS execution/mounting
        await page.waitForTimeout(2000);

        // Fail the test if there are any fatal JS exceptions
        if (pageErrors.length > 0) {
            console.error("PAGE ERRORS CAUGHT:", pageErrors);
        }
        expect(pageErrors, 'There should be no unhandled page exceptions').toHaveLength(0);

        // Verify the main app wrapper renders successfully
        const mainEl = page.locator('main');
        await expect(mainEl).toBeVisible({ timeout: 5000 });

        const brandEl = page.locator('.nav-brand h1');
        await expect(brandEl).toHaveText(/SIMULACRUM/i);
    });

    test('Navigation menu layout avoids vertical regression (Flex layout check)', async ({ page }) => {
        await page.goto('/');

        // Wait for initial data load overlay to dismiss so menu is fully visible
        await expect(page.locator('.loader')).toBeHidden({ timeout: 10000 });

        // Wait for nav to mount
        const nav = page.locator('.top-nav');
        await expect(nav).toBeVisible();

        // Check computed CSS to assure it is rendering as a flex row, not vertically stacked blocks
        const navDisplay = await nav.evaluate((el) => window.getComputedStyle(el).display);
        expect(navDisplay).toBe('flex');

        // Ensure nav-modes (the buttons overlay) is also flexing horizontally
        const navModes = page.locator('.nav-modes');
        await expect(navModes).toBeVisible();
        const modesDisplay = await navModes.evaluate((el) => window.getComputedStyle(el).display);
        expect(modesDisplay).toBe('flex');
    });
});
