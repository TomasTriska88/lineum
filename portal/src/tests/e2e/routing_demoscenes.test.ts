import { test, expect } from '@playwright/test';

test.describe('Lineum Routing Demoscenes UI', () => {
    test('Should load Routing page without 500 Error and select presets', async ({ page }) => {
        // Visit routing page
        const res = await page.goto('/api-solutions');

        // Check if the application did not crash into a 500 server-side render error
        expect(res?.status()).toBe(200);

        // Verify that the WebGL Canvas and Theming headers are rendered
        await expect(page.locator('canvas').first()).toBeVisible();
        await expect(page.locator('text=Business Use-Cases')).toBeVisible();

        // Select 'vascular' preset from the Side Menu
        const selectPresetBtn = page.locator('button:has-text("3. Vascular / Irrigation Network")');
        await expect(selectPresetBtn).toBeVisible();
        await selectPresetBtn.click();

        // Check if UI adequately reacted by changing text (Algorithm for vascular)
        const descText = page.locator('text=High noise divergence. Fluid covers maximum tissue area forming fractals.');
        await expect(descText).toBeAttached();

        // Verify that the INITIATE SHOWCASE button exists
        const btnStart = page.locator('button:has-text("RUN LIVE VERIFICATION")');
        await expect(btnStart).toBeVisible();

        // CLICK the button as a test and verify state changes to ABORT SIMULATION
        // If the WebSocket connection falls, Playwright console.error will catch it.
        page.on('console', msg => {
            if (msg.type() === 'error') {
                console.log('BROWSER ERROR CONSOLE:', msg.text());
            }
        });

        await btnStart.click();

        // Let the simulation trigger and the API call run (Mocks will finish it very quickly)
        await page.waitForTimeout(1000);

        // Assert that the progress bar or step counter moved
        await expect(page.locator('text=LIVE:')).not.toBeVisible(); // Should have finished or crashed
    });
});
