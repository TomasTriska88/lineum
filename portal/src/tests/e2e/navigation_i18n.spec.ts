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
        await page.goto('/');
        await expect(page.locator('.nav-logo').first()).toBeVisible();

        const mobileToggle = page.locator('.mobile-toggle').first();
        if (await mobileToggle.isVisible()) await mobileToggle.click();

        const labLink = page.locator('.nav-links a[target="simulacrum"]').first();
        await expect(labLink).toBeVisible();

        const scientistLink = page.locator('.nav-links a[href$="#scientist"]').first();
        await expect(scientistLink).toBeVisible();

        // Check Docs Dropdown
        const docsToggle = page.locator('.dropdown-toggle').first();
        await docsToggle.click();

        const aboutLink = page.locator('.dropdown-menu a:has-text("About Us")').first();
        await expect(aboutLink).toBeVisible();
    });

    test('Should display Czech navigation on the /cs/ path', async ({ page }) => {
        // According to our i18n file, Czech localized paths are prefixed normally with /cs
        await page.goto('/cs/');
        await expect(page.locator('.nav-logo').first()).toBeVisible();

        const mobileToggle = page.locator('.mobile-toggle').first();
        if (await mobileToggle.isVisible()) await mobileToggle.click();

        // Check if the Lab link is visible
        const labLink = page.locator('.nav-links a[target="simulacrum"]').first();
        await expect(labLink).toBeVisible();

        const scientistLink = page.locator('.nav-links a[href$="#scientist"]').first();
        await expect(scientistLink).toBeVisible();

        // Check Docs Dropdown
        const docsToggle = page.locator('.dropdown-toggle').first();
        await docsToggle.click();

        const aboutLink = page.locator('.dropdown-menu a:has-text("O Nás")').first();
        await expect(aboutLink).toBeVisible();
    });

    test('Should display language names in their native localized form (Čeština, Deutsch, etc) regardless of current UI language', async ({ page }) => {
        await page.setViewportSize({ width: 1280, height: 720 });
        await page.goto('/');

        // Wait for hydration
        await expect(page.locator('.nav-logo').first()).toBeVisible();

        // 0. Handle mobile viewport if necessary (ensures lang-switcher is visible)
        const mobileToggle = page.locator('.mobile-toggle').first();
        if (await mobileToggle.isVisible()) {
            await mobileToggle.click();
        }

        // Check language labels are native. Since they are inside a dropdown, we open it first.
        await page.locator('.lang-toggle').click();

        const csButton = page.locator('.lang-dropdown a[hreflang="cs"]').first();
        await expect(csButton).toContainText('Čeština');

        const deButton = page.locator('.lang-dropdown a[hreflang="de"]').first();
        await expect(deButton).toContainText('Deutsch');

        const jaButton = page.locator('.lang-dropdown a[hreflang="ja"]').first();
        await expect(jaButton).toContainText('日本語');

        const enButton = page.locator('.lang-dropdown a[hreflang="en"]').first();
        await expect(enButton).toContainText('English');

        // Switch to German and ensure the Czech button STILL says "Čeština"
        await deButton.click();
        await page.waitForTimeout(500);

        // Wait again for header to re-appear
        await expect(page.locator('.nav-logo').first()).toBeVisible();

        // 0. Handle mobile viewport if necessary (ensures lang-switcher is visible)
        if (await mobileToggle.isVisible()) {
            await mobileToggle.click();
        }

        // Open dropdown again
        await page.locator('.lang-toggle').click();

        // Re-query locator after page reload
        const csButtonAfter = page.locator('.lang-dropdown a[hreflang="cs"]').first();
        await expect(csButtonAfter).toContainText('Čeština');
    });

});
