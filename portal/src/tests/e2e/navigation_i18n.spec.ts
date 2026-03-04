import { test, expect } from '@playwright/test';

test.describe('Navigation i18n Localization', () => {

    // We assume Paraglide routing uses language prefixes like /en/ and /cs/, 
    // or standard browser headers/cookies depending on Lineum's exact config.
    // For many SvelteKit + Paraglide setups, the base language is at `/` 
    // and the alternate is at `/cs` or another prefix. 
    // Let's test by setting the `Accept-Language` header if routing is header-based,
    // or we will just check the text content directly if it's based on path.

    test('Should display English navigation on the root path', async ({ page }) => {
        // According to our i18n file, English is the default language tag mapped to '/'
        await page.goto('http://127.0.0.1:5173/');
        await expect(page.locator('.nav-logo').first()).toBeVisible();

        const mobileToggle = page.locator('.mobile-toggle').first();
        if (await mobileToggle.isVisible()) await mobileToggle.click();

        const labLink = page.locator('.nav-links a:has-text("Laboratory")').first();
        await expect(labLink).toBeVisible();

        const scientistLink = page.locator('.nav-links a:has-text("For Researchers")').first();
        await expect(scientistLink).toBeVisible();

        // Check Docs Dropdown
        const docsToggle = page.locator('.dropdown-toggle').first();
        await docsToggle.click();

        const aboutLink = page.locator('.dropdown-menu a:has-text("About Us")').first();
        await expect(aboutLink).toBeVisible();
    });

    test('Should display Czech navigation on the /cs/ path', async ({ page }) => {
        // According to our i18n file, Czech localized paths are prefixed normally with /cs
        await page.goto('http://127.0.0.1:5173/cs/');
        await expect(page.locator('.nav-logo').first()).toBeVisible();

        const mobileToggle = page.locator('.mobile-toggle').first();
        if (await mobileToggle.isVisible()) await mobileToggle.click();

        // Check if the Lab link text is Czech
        const labLink = page.locator('.nav-links a:has-text("Laboratoř")').first();
        await expect(labLink).toBeVisible();

        const scientistLink = page.locator('.nav-links a:has-text("Pro výzkumníky")').first();
        await expect(scientistLink).toBeVisible();

        // Check Docs Dropdown
        const docsToggle = page.locator('.dropdown-toggle').first();
        await docsToggle.click();

        const aboutLink = page.locator('.dropdown-menu a:has-text("O Nás")').first();
        await expect(aboutLink).toBeVisible();
    });

    test('Should display language names in their native localized form (Čeština, Deutsch, etc) regardless of current UI language', async ({ page }) => {
        await page.setViewportSize({ width: 1280, height: 720 });
        await page.goto('http://127.0.0.1:5173/');

        // Wait for hydration
        await expect(page.locator('.nav-logo').first()).toBeVisible();

        // 0. Handle mobile viewport if necessary (ensures lang-switcher is visible)
        const mobileToggle = page.locator('.mobile-toggle').first();
        if (await mobileToggle.isVisible()) {
            await mobileToggle.click();
        }

        // Check language tooltip labels are native
        const csButton = page.locator('a[hreflang="cs"]').first();
        await expect(csButton).toHaveAttribute('data-tooltip', 'Čeština');

        const deButton = page.locator('a[hreflang="de"]').first();
        await expect(deButton).toHaveAttribute('data-tooltip', 'Deutsch');

        const jaButton = page.locator('a[hreflang="ja"]').first();
        await expect(jaButton).toHaveAttribute('data-tooltip', '日本語');

        const enButton = page.locator('a[hreflang="en"]').first();
        await expect(enButton).toHaveAttribute('data-tooltip', 'English');

        // Switch to German and ensure the Czech button STILL says "Čeština"
        await deButton.click({ force: true });
        await page.waitForTimeout(500);

        // Wait again for header to re-appear
        await expect(page.locator('.nav-logo').first()).toBeVisible();

        // Re-query locator after page reload
        const csButtonAfter = page.locator('a[hreflang="cs"]').first();
        await expect(csButtonAfter).toHaveAttribute('data-tooltip', 'Čeština');
    });

});
