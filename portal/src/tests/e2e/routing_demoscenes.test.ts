import { test, expect } from '@playwright/test';

test.describe('Lineum Routing Demoscenes UI', () => {
    test('Should load Routing page without 500 Error and select presets', async ({ page }) => {
        // Visit routing page
        const res = await page.goto('/routing');

        // Check if the application did not crash into a 500 server-side render error
        expect(res?.status()).toBe(200);

        // Verify that the WebGL Canvas and Theming headers are rendered
        await expect(page.locator('canvas.webgl-canvas')).toBeVisible();
        await expect(page.locator('text=Business Use-Cases')).toBeVisible();

        // Select 'vascular' preset from the Demoscenes dropdown
        const selectPreset = page.locator('select.holo-select');
        await expect(selectPreset).toBeVisible();
        await selectPreset.selectOption('vascular');

        // Check if UI adequately reacted by changing text (Algorithm for vascular)
        await expect(page.locator('text=High noise divergence. Fluid covers maximum tissue area forming fractals.')).toBeVisible();

        // Verify that the INITIATE SHOWCASE button exists
        const btnStart = page.locator('button.btn-initiate');
        await expect(btnStart).toBeVisible();
        await expect(btnStart).toContainText('INITIATE SHOWCASE');

        // CLICK the button as a test and verify state changes to ABORT SIMULATION
        // If the WebSocket connection falls, Playwright console.error will catch it.
        page.on('console', msg => {
            if (msg.type() === 'error') {
                console.log('BROWSER ERROR CONSOLE:', msg.text());
            }
        });

        await btnStart.click();
        await expect(page.locator('button.btn-abort')).toBeVisible();
    });
});
