import { test, expect } from '@playwright/test';

test.describe('Language Content Rendering', () => {

    test('should render translated German text on /de without falling back to Czech', async ({ page, isMobile }) => {
        // Go straight to the German homepage
        await page.goto('/de');

        // Wait for page to hydrate
        await expect(page.locator('h1').first()).toBeVisible();

        // The title MUST contain German words, not Czech phrases like 'Věda o polích' or 'Dýchej'
        const headingText = await page.locator('h1').first().textContent();
        expect(headingText).toContain('Die Wissenschaft von Feldern');
        expect(headingText).toContain('atmen');

        // Assert it explicitly does not contain the old Czech cached phantom string
        expect(headingText).not.toContain('Dýchej');
        expect(headingText).not.toContain('Věda o polích');
    });

    test('should render correct Japanese text on /ja', async ({ page }) => {
        // Japanese text test
        await page.goto('/ja');
        await page.waitForLoadState('networkidle');
        await page.waitForTimeout(1000);

        // --- Added: Open the Resonance Deck first ---
        await page.locator('.deck-main').click();
        await expect(page.locator('h1').first()).toBeVisible();
        const headingText = await page.locator('h1').first().textContent();
        expect(headingText).toContain('場の科学');

        // Japanese Chat Test
        await page.locator('.deck-main').click();

        // Wait until any of the expected JP text segments appear in the chat bubble using CSS has-text, as DOM animations break standard expect matchers
        await page.waitForSelector('.msg.model:has-text("Lineumの概念について説明する準備ができました")', { timeout: 15000 });
    });

    test('should render translated German chat HUD and tooltips', async ({ page }) => {
        await page.goto('/de');
        await page.waitForLoadState('networkidle');
        await page.waitForTimeout(1000);
        await page.locator('.deck-main').click();

        // 1. Tooltip test
        const badge = page.locator('.token-badge');
        await expect(badge).toBeVisible();
        await expect(badge).toHaveAttribute('data-tooltip', 'TÄGLICHES SICHERHEITSBUDGET VERBRAUCHT');

        // 2. Greeting Test
        await page.waitForSelector('.msg.model:has-text("Ich bin bereit, die Konzepte von Lineum zu erklären")', { timeout: 15000 });
    });
});
