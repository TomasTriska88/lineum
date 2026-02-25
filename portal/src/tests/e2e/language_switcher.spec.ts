import { test, expect } from '@playwright/test';

test.describe('Language Switcher', () => {

    test('should navigate to the correct localized URL when language is changed', async ({ page }) => {
        await page.goto('/');

        // Wait for the main page to load
        await expect(page.locator('h1').first()).toBeVisible();

        // Find the Japanese switcher element
        const jaButton = page.locator('.lang-btn', { hasText: 'JA' }).first();

        // Click to switch language (forcing in case hidden behind hamburger)
        await jaButton.click({ force: true });

        // The URL should now include the /ja/ prefix
        await expect(page).toHaveURL(/\/ja/);

        // The HTML lang attribute should reflect the new language
        await expect(page.locator('html')).toHaveAttribute('lang', 'ja');

        // Switch back to English
        const enButton = page.locator('.lang-btn', { hasText: 'EN' }).first();
        await enButton.click({ force: true });

        // English is the default language, so the URL should not have /ja
        await expect(page).toHaveURL(/^(?!.*\/ja).*$/);
        await expect(page.locator('html')).toHaveAttribute('lang', 'en');
    });

});
