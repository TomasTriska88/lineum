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
        await expect(page.getByText('Live Research / Documentation Gap')).toBeVisible();

        // 2. Test "Ask Lina" Action
        const linaBtn = page.getByRole('button', { name: '✨ Ask Lina Instead' });
        await expect(linaBtn).toBeVisible();

        await linaBtn.click();

        // Modal should run away
        await expect(modal).not.toBeVisible();

        // Deck should be expanded
        const deck = page.locator('.deck-container');
        await expect(deck).toHaveClass(/expanded/);
    });

    test('should allow standard acknowledgement', async ({ page }) => {
        await page.goto('/wiki');
        await page.getByRole('button', { name: 'I Understand, Continue' }).click();
        await expect(page.locator('.dialog-window')).not.toBeVisible();
    });

    test('should reappear on reload (always show)', async ({ page }) => {
        // 1. Visit and Ack
        await page.goto('/wiki');
        await page.getByRole('button', { name: 'I Understand, Continue' }).click();
        await expect(page.locator('.dialog-window')).not.toBeVisible();

        // 2. Reload (Simulate via goto to ensure clean state)
        await page.goto('/wiki');

        // 3. Should see modal again
        await expect(page.locator('.dialog-window')).toBeVisible();
    });

    test('should block interaction with content (backdrop)', async ({ page }) => {
        await page.goto('/wiki');

        // Backdrop should be visible
        const backdrop = page.locator('.dialog-backdrop');
        await expect(backdrop).toBeVisible();
        await expect(backdrop).toHaveCSS('pointer-events', 'auto');
    });
});
