// @ts-check
import { test, expect } from '@playwright/test';

test.describe('3D Simulator Optimization', () => {
    test('Animation loop stops when switching away from Simulator tab', async ({ page }) => {
        // Navigate to the lab page
        await page.goto('/');

        // Ensure we are on the Simulator tab initially
        await expect(page.locator('text=SIMULACRUM')).toBeVisible();

        // 1. Wait for canvas and verify engine is NOT paused
        const canvasContainer = page.locator('.canvas-container');
        await expect(canvasContainer.locator('canvas')).toBeVisible({ timeout: 15000 });

        await expect(canvasContainer).toHaveAttribute('data-engine-paused', 'false');

        // 2. Switch to Validation Core
        await page.getByRole('button', { name: 'Validation Core' }).click({ force: true });

        // Ensure we are in Validation Dashboard by waiting for a core scenario card
        await expect(page.locator('text=Wave Sanity: T0/T1')).toBeVisible({ timeout: 10000 });

        // Give it a tiny bit of time to settle the state change
        await page.waitForTimeout(200);

        // 3. Verify the engine is now paused
        await expect(canvasContainer).toHaveAttribute('data-engine-paused', 'true');

        // 4. Switch back to Simulator
        await page.getByRole('button', { name: '3D Simulator' }).click();
        await page.waitForTimeout(200);

        // 5. Measure frames again to ensure it resumed
        await expect(canvasContainer).toHaveAttribute('data-engine-paused', 'false');
    });
});
