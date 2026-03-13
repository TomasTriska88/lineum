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

        // Find the Japanese switcher element
        const jaButton = page.locator('.lang-dropdown a[hreflang="ja"]').first();

        // Click to switch language (Must expand the dropdown first)
        const dropdownToggle = page.locator('.lang-dropdown .dropdown-toggle');
        await dropdownToggle.click();
        await page.waitForTimeout(300); // Wait for CSS opacity transition
        await jaButton.click();

        // The URL should now include the /ja/ prefix
        await expect(page).toHaveURL(/\/ja/);

        // The HTML lang attribute should reflect the new language
        await expect(page.locator('html')).toHaveAttribute('lang', 'ja');

        // Switch back to English
        const enButton = page.locator('.lang-dropdown a[hreflang="en"]').first();
        await dropdownToggle.click();
        await page.waitForTimeout(300);
        await enButton.click();

        // English is the default language, so the URL should not have /ja
        await expect(page).toHaveURL(/^(?!.*\/ja).*$/);
        await expect(page.locator('html')).toHaveAttribute('lang', 'en');
        await expect(page.locator('.lang-dropdown a[hreflang="en"]').first()).toHaveClass(/active/);

        // Test "every other right/left" skip bug
        // Switch to Czech
        const csButton = page.locator('.lang-dropdown a[hreflang="cs"]').first();
        await dropdownToggle.click();
        await page.waitForTimeout(300);
        await csButton.click();
        await expect(page).toHaveURL(/\/cs/);
        await expect(page.locator('html')).toHaveAttribute('lang', 'cs');
        await expect(page.locator('.lang-dropdown a[hreflang="cs"]').first()).toHaveClass(/active/);

        // Switch to Deutsch immediately after Czech
        const deButton = page.locator('.lang-dropdown a[hreflang="de"]').first();
        await dropdownToggle.click();
        await page.waitForTimeout(300);
        await deButton.click();
        await expect(page).toHaveURL(/\/de/);
        await expect(page.locator('html')).toHaveAttribute('lang', 'de');
        await expect(page.locator('.lang-dropdown a[hreflang="de"]').first()).toHaveClass(/active/);
    });

});
