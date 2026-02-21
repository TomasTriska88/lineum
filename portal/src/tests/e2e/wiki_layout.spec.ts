import { test, expect } from './base';

test.describe('Wiki Layout', () => {
    test.beforeEach(async ({ page }) => {
        // Clear sessionStorage to avoid modal interference
        await page.goto('/wiki/lineum-core');
        await page.evaluate(() => sessionStorage.clear());
        await page.reload();

        // Acknowledge the warning modal if present
        const modal = page.locator('.dialog-window');
        if (await modal.isVisible()) {
            await page.getByRole('button', { name: 'I Understand, Continue' }).click();
            await expect(modal).not.toBeVisible();
        }
    });

    test('should not overflow viewport width horizontally', async ({ page }) => {
        // Wait for the prose content to render
        await expect(page.locator('.prose')).toBeVisible();

        // Evaluate scrollWidth vs clientWidth on the body to ensure no horizontal scrolling
        const hasHorizontalOverflow = await page.evaluate(() => {
            return document.documentElement.scrollWidth > document.documentElement.clientWidth;
        });

        // The layout should fit within the screen without horizontal scrolling
        expect(hasHorizontalOverflow).toBe(false);
    });

    test('card element should be constrained within wrapper', async ({ page, isMobile }) => {
        // Wait for the card content to render
        const card = page.locator('.card');
        await expect(card).toBeVisible();

        // Check the width of the card versus the visual viewport
        const cardBoundingBox = await card.boundingBox();
        const viewportSize = page.viewportSize();

        // The card must not be wider than the viewport width (with a small margin of error)
        if (cardBoundingBox && viewportSize) {
            console.log("Card Width:", cardBoundingBox.width, "Viewport:", viewportSize.width);
            expect(cardBoundingBox.width).toBeLessThanOrEqual(viewportSize.width);
        }
    });
});
