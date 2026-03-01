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
        await expect(urbanBtn).toBeVisible();
        await urbanBtn.click();
        await expect(page.getByRole('button', { name: /Calculating Tensor...|New Iteration/i })).toBeVisible();

        // Test Evacuation Routing
        const evacBtn = page.getByRole('button', { name: /Calculate Exit Routes/i });
        await expect(evacBtn).toBeVisible();
        await evacBtn.click();
        await expect(page.getByRole('button', { name: /Simulating Crowd...|Reset Drill/i })).toBeVisible();
    });
});
