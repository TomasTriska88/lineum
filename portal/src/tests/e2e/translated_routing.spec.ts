import { test, expect } from '@playwright/test';

test.describe('Translated Routing (SEO URLs)', () => {

    test('should properly translate SvelteKit URLs using pathnames mapping', async ({ page, isMobile }) => {
        // Ignore mobile breakpoints for this test as we are primarily testing API routing
        if (isMobile) {
            test.skip();
            return;
        }

        // Start on English api-solutions
        await page.goto('/api-solutions');

        // Wait for page to load
        await expect(page.locator('h1').first()).toBeVisible();

        // Currently in EN, URL must be base (unless EN prefix is enforced)
        await expect(page).toHaveURL(/.*\/api-solutions/);

        // Switch to Czech, click CS button in switcher
        const csButton = page.locator('.lang-switcher .lang-btn', { hasText: 'CS' }).first();
        await csButton.click();

        // Verify URL transformed into translated sub-directory routing (! not canonical route /cs/api-solutions !)
        await expect(page).toHaveURL(/\/cs\/api-reseni/);
        await expect(page.locator('html')).toHaveAttribute('lang', 'cs');

        // Switch to German from Czech (cross-navigate on a translated route)
        const deButton = page.locator('.lang-switcher .lang-btn', { hasText: 'DE' }).first();
        await deButton.click();

        // Validate German translated route (api-loesungen)
        await expect(page).toHaveURL(/\/de\/api-loesungen/);
        await expect(page.locator('html')).toHaveAttribute('lang', 'de');

        // Back to Japanese (which has no explicit translation mapping, retains /api-solutions)
        const jaButton = page.locator('.lang-switcher .lang-btn', { hasText: 'JA' }).first();
        await jaButton.click();

        // Validate Japanese URL (but prefix must appear)
        await expect(page).toHaveURL(/\/ja\/api-solutions/);
        await expect(page.locator('html')).toHaveAttribute('lang', 'ja');
    });

});
