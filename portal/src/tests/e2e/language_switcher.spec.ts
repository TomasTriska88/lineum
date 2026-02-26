import { test, expect } from '@playwright/test';

test.describe('Language Switcher', () => {

    test('should navigate to the correct localized URL when language is changed', async ({ page, isMobile }) => {
        // Skip mobile testing here since Playwright struggles with SvelteKit SPA clicks via display: none
        if (isMobile) {
            test.skip();
            return;
        }

        await page.goto('/');

        // Wait for the main page to load
        await expect(page.locator('h1').first()).toBeVisible();

        // Ensure the language switcher block protects against browser auto-translators
        await expect(page.locator('.lang-switcher')).toHaveAttribute('translate', 'no');

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
        await expect(page.locator('.lang-btn', { hasText: 'EN' }).first()).toHaveClass(/active/);

        // Test "every other right/left" skip bug
        // Switch to Czech
        const csButton = page.locator('.lang-btn', { hasText: 'CS' }).first();
        await csButton.click({ force: true });
        await expect(page).toHaveURL(/\/cs/);
        await expect(page.locator('html')).toHaveAttribute('lang', 'cs');
        await expect(page.locator('.lang-btn', { hasText: 'CS' }).first()).toHaveClass(/active/);

        // Switch to Deutsch immediately after Czech
        const deButton = page.locator('.lang-btn', { hasText: 'DE' }).first();
        await deButton.click({ force: true });
        await expect(page).toHaveURL(/\/de/);
        await expect(page.locator('html')).toHaveAttribute('lang', 'de');
        await expect(page.locator('.lang-btn', { hasText: 'DE' }).first()).toHaveClass(/active/);
    });

});
