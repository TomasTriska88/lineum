import { test, expect } from '@playwright/test';

test.describe('Navigation i18n Localization', () => {

    // We assume Paraglide routing uses language prefixes like /en/ and /cs/, 
    // or standard browser headers/cookies depending on Lineum's exact config.
    // For many SvelteKit + Paraglide setups, the base language is at `/` 
    // and the alternate is at `/cs` or another prefix. 
    // Let's test by setting the `Accept-Language` header if routing is header-based,
    // or we will just check the text content directly if it's based on path.

    test('Should display English navigation when English locale is forced via UI switcher', async ({ page }) => {
        await page.setViewportSize({ width: 1280, height: 720 });

        // Force English by navigating directly to the English root (mimics what the button does)
        await page.goto('http://localhost:5173/en/');

        // Wait for page reload from sveltekit data-sveltekit-reload
        // Avoid networkidle because WebGL/SSE might keep network active
        await page.waitForTimeout(1000);

        // Open mobile menu if we are on a narrow viewport
        const mobileToggle = page.locator('.mobile-toggle').first();
        if (await mobileToggle.isVisible()) {
            await mobileToggle.click();
            await page.waitForTimeout(300); // Wait for menu open animation/render
        }

        // Check the Lab link text (identified by target)
        const labLink = page.getByRole('link', { name: /Laboratory/i, exact: false }).first();
        await expect(labLink).toBeVisible();

        // Check 'For Scientists' link text (identified by href)
        const scientistLink = page.getByRole('link', { name: /For Researchers/i, exact: false }).first();
        await expect(scientistLink).toBeVisible();

        // Click the Docs dropdown and verify 'About' is English
        // Try forcing the click and checking DOM content instead of visual visibility
        await page.$eval('.dropdown-toggle', (el: HTMLElement) => el.click());

        const aboutLink = page.getByRole('link', { name: /About Us/i, exact: false }).first();
        await expect(aboutLink).toBeVisible();
    });

    test('Should display Czech navigation when Czech locale is forced via UI switcher', async ({ page }) => {
        await page.setViewportSize({ width: 1280, height: 720 });

        // Force Czech by navigating directly to the Czech root
        await page.goto('http://localhost:5173/cs/');
        await page.waitForLoadState('networkidle');

        // Wait for hydration
        await expect(page.locator('.nav-logo').first()).toBeVisible();

        // Open mobile menu if we are on a narrow viewport
        const mobileToggle = page.locator('.mobile-toggle').first();
        if (await mobileToggle.isVisible()) {
            await mobileToggle.click();
            await page.waitForTimeout(300); // Wait for menu open animation/render
        }

        // Check the Lab link text
        const labLink = page.getByRole('link', { name: /Laboratoř/i, exact: false }).first();
        await expect(labLink).toBeVisible();

        // Check 'For Scientists' link text
        const scientistLink = page.getByRole('link', { name: /Pro výzkumníky/i, exact: false }).first();
        await expect(scientistLink).toBeVisible();

        // Click the Docs dropdown and verify 'About' is Czech
        await page.$eval('.dropdown-toggle', (el: HTMLElement) => el.click());

        const aboutLink = page.getByRole('link', { name: /O Nás/i, exact: false }).first();
        await expect(aboutLink).toBeVisible();
    });

    test('Should display language names in their native localized form (Čeština, Deutsch, etc) regardless of current UI language', async ({ page }) => {
        await page.setViewportSize({ width: 1280, height: 720 });
        await page.goto('http://localhost:5173/');

        // Wait for hydration
        await expect(page.locator('.nav-logo').first()).toBeVisible();

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
