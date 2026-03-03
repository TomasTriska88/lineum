import { test, expect } from '@playwright/test';

test.describe('Lineum Routing Demoscenes UI', () => {
    test('Should load Routing page and trigger Urban and Evac simulations', async ({ page }) => {
        // Visit routing page
        const res = await page.goto('/api-solutions');
        expect(res?.status()).toBe(200);

        // Verify that the WebGL Canvas components are rendered
        await expect(page.locator('canvas').first()).toBeVisible();

        // Test Urban Routing
        const urbanBtn = page.getByRole('button', { name: /Optimize Fleet Routes/i });
        await urbanBtn.scrollIntoViewIfNeeded();
        await page.waitForTimeout(1000); // Wait for IntersectionObserver and Svelte WebGL mount
        await expect(urbanBtn).toBeVisible({ timeout: 15000 });
        await urbanBtn.click();
        await expect(page.getByRole('button', { name: /Calculating Tensor...|New Iteration/i })).toBeVisible({ timeout: 10000 });

        // Test Evacuation Routing
        const evacBtn = page.getByRole('button', { name: /Calculate Exit Routes/i });
        await evacBtn.scrollIntoViewIfNeeded();
        await page.waitForTimeout(1000); // Wait for IntersectionObserver and Svelte WebGL mount
        await expect(evacBtn).toBeVisible({ timeout: 15000 });
        await evacBtn.click();
        await expect(page.getByRole('button', { name: /Simulating Crowd...|Reset Drill/i })).toBeVisible({ timeout: 10000 });
    });
});
