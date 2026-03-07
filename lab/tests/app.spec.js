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

    test('Clicking top navigation buttons changes the main view mode and canvas visibility', async ({ page }) => {
        await page.goto('/');
        await expect(page.locator('.loader')).toBeHidden({ timeout: 10000 });

        // Ensure we are initially in 3D Simulator mode and canvas is visible
        const canvasContainer = page.locator('.canvas-container');
        await expect(canvasContainer).toBeVisible();
        await expect(canvasContainer).toHaveCSS('opacity', '1');

        // Click the Validation Core button
        const validationBtn = page.locator('button:has-text("Validation Core")');
        // Ensure the button isn't covered by retrieving its bounding box or throwing if obstructed
        await validationBtn.click();

        // The simulator overlay should hide, and the fullscreen-mode should appear containing the ValidationDashboard layout
        await expect(page.locator('.layout')).toBeVisible({ timeout: 5000 });

        // The canvas should be hidden
        await expect(canvasContainer).toBeHidden();

        // Click the Claims button
        const claimsBtn = page.locator('button:has-text("Claims")');
        await claimsBtn.click();

        // Wait for WhitepaperClaims to load (its container uses layout too, but check a specific header or element inside)
        await expect(page.locator('.claims-container')).toBeVisible({ timeout: 5000 });

        // The canvas should still be hidden
        await expect(canvasContainer).toBeHidden();

        // Click the 3D Simulator button again to verify it reappears
        const simBtn = page.locator('button:has-text("3D Simulator")');
        await simBtn.click();

        // The canvas should be visible again
        await expect(canvasContainer).toBeVisible();
        await expect(canvasContainer).toHaveCSS('opacity', '1');
    });

    test('Fullscreen mode containers do not overlap with the top navigation bar', async ({ page }) => {
        await page.goto('/');
        await expect(page.locator('.loader')).toBeHidden({ timeout: 10000 });

        // Navigate to a mode that uses fullscreen-mode, e.g., Validation Core
        const validationBtn = page.locator('button:has-text("Validation Core")');
        await validationBtn.click();

        // Wait for fullscreen-mode to be visible
        const fullscreenMode = page.locator('.fullscreen-mode');
        await expect(fullscreenMode).toBeVisible({ timeout: 5000 });

        // Get bounding boxes
        const nav = page.locator('.top-nav');
        const navBox = await nav.boundingBox();
        const fullBox = await fullscreenMode.boundingBox();

        expect(navBox).not.toBeNull();
        expect(fullBox).not.toBeNull();

        // The top of the fullscreen mode should be greater than or equal to the bottom of the nav bar
        expect(fullBox.y).toBeGreaterThanOrEqual(navBox.y + navBox.height);
    });
});

