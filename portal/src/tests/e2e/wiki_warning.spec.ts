import { test, expect } from './base';

test.describe('Wiki Warning Modal', () => {
    test.beforeEach(async ({ page }) => {
        // Clear sessionStorage to force the modal to appear
        await page.goto('/');
        await page.evaluate(() => sessionStorage.clear());
    });

    test('should appear when navigating to wiki', async ({ page }) => {
        // Navigate to Wiki
        await page.goto('/wiki');

        // Check if modal exists
        const modal = page.locator('.dialog-window');
        await expect(modal).toBeVisible();

        // Check content
        await expect(page.getByText('Documentation Under Revision')).toBeVisible();

        // Click confirm
        await page.getByRole('button', { name: 'I Understand, Continue' }).click();

        // Modal should run away
        await expect(modal).not.toBeVisible();
    });

    test('should persist acknowledgement', async ({ page }) => {
        // 1. Visit and Ack
        await page.goto('/wiki');
        await page.getByRole('button', { name: 'I Understand, Continue' }).click();

        // CHECK STORAGE
        const ackBefore = await page.evaluate(() => sessionStorage.getItem('lineum_whitepaper_warning_acknowledged'));
        expect(ackBefore).toBe('true');

        // 2. Reload (Simulate via goto to ensure clean state)
        await page.goto('/wiki');

        // CHECK STORAGE
        const ackAfter = await page.evaluate(() => sessionStorage.getItem('lineum_whitepaper_warning_acknowledged'));
        expect(ackAfter).toBe('true');

        // 3. Should not see modal
        await expect(page.locator('.dialog-window')).not.toBeVisible();
    });

    test('should block interaction with content (backdrop)', async ({ page }) => {
        await page.goto('/wiki');

        // Backdrop should be visible
        const backdrop = page.locator('.dialog-backdrop');
        await expect(backdrop).toBeVisible();
        await expect(backdrop).toHaveCSS('pointer-events', 'auto');
    });
});
