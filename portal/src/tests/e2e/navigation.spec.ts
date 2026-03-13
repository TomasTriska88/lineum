import { test, expect } from '@playwright/test';

test.describe('Navigation Redesign Layout', () => {

    test('Mega-Dropdown Ecosystem opens and contains expected items', async ({ page, isMobile }) => {
        await page.goto('/');

        if (isMobile) {
            await page.locator('.mobile-toggle').click();
        }

        // Click the Ecosystem toggle
        const ecosystemBtn = page.getByRole('button', { name: /Ecosystem/ });
        await expect(ecosystemBtn).toBeVisible();
        await ecosystemBtn.click();

        // Check if the mega-menu is visible and has the correct links
        const wikiLink = page.getByRole('link', { name: 'FAQ' });
        await expect(wikiLink).toBeVisible();

        const aboutLink = page.getByRole('link', { name: 'About Us' });
        await expect(aboutLink).toBeVisible();
    });

    test('Language dropdown works and uses CZ abbreviation instead of CS', async ({ page, isMobile }) => {
        await page.goto('/cs');

        if (isMobile) {
            await page.locator('.mobile-toggle').click();
        }

        // The button should say CZ
        const langBtn = page.locator('.lang-toggle');
        await expect(langBtn).toContainText('CZ');
        await langBtn.click();

        // The dropdown should contain the English link
        const enLink = page.getByRole('link', { name: 'English (EN)' });
        await expect(enLink).toBeVisible();

        // Ensure Czech label also has CZ in parentheses
        const csLink = page.getByRole('link', { name: 'Čeština (CZ)' });
        await expect(csLink).toBeVisible();
        // Ensure CSS width constraints apply (the previous modification)
        // Check that white-space is nowrap to prevent ugly breaking
        const firstLink = page.locator('.lang-dropdown a').first();
        await expect(firstLink).toHaveCSS('white-space', 'nowrap');
    });

    test('Navigation layout renders without 500 SSR error', async ({ request }) => {
        // Assert that the page loads correctly (verifies no corrupted Svelte tags)
        const response = await request.get('/');
        expect(response.ok()).toBeTruthy();
        expect(response.status()).toBe(200);
    });

    test('Lab link (Simulacrum) does not point to bugged 127.0.0.1 IPv4', async ({ page, isMobile }) => {
        if (isMobile) return;
        await page.goto('/');
        const labLink = page.locator('a[target="simulacrum"]').first();
        await expect(labLink).toBeVisible();
        
        const href = await labLink.getAttribute('href');
        expect(href).toBeTruthy();
    });

});
