import { test, expect } from '@playwright/test';

test.describe('Lineum Homepage UI Updates', () => {
    test('Should display Lab and Engraving links in the main navigation', async ({ page }) => {
        await page.goto('/');

        // Ensure the layout has loaded
        await expect(page.locator('.nav-logo').first()).toBeVisible();

        // 0. Handle mobile viewport if necessary
        const mobileToggle = page.locator('.mobile-toggle');
        if (await mobileToggle.isVisible()) {
            await mobileToggle.click();
        }

        // 1. Check if the Lab link is visible (i18n safe)
        const labLink = page.locator('.nav-links a[target="simulacrum"]');
        await expect(labLink).toBeVisible();

        // 1.5 & 2 Check if API Solutions and Engraving are visible (only if enabled via env)
        const apiLink = page.locator('a[href="/api-solutions"]').first();
        if ((await apiLink.count()) > 0) {
            await expect(apiLink).toBeVisible();
            const engravingLink = page.locator('a[href="/engraving"]').first();
            await expect(engravingLink).toBeVisible();
        }

        // 3. Check if 'For Scientists' is visible directly via href (i18n safe)
        const scientistLink = page.locator('a[href="/#scientist"]');
        await expect(scientistLink).toBeVisible();

        // 4. Click the Docs dropdown and verify 'About' is present
        const docsToggle = page.locator('.dropdown-toggle');
        await expect(docsToggle).toBeVisible();
        await docsToggle.click();

        const aboutLink = page.locator('a[href="/about"]');
        await expect(aboutLink).toBeVisible();
    });

    test('Should display the new Physics Equation with the Mu term', async ({ page }) => {
        await page.goto('/');

        // The equation inline should show up on the hero section
        // We look for the literal text `μ` in the span
        const eqBlock = page.locator('.equation-inline');
        await expect(eqBlock).toBeVisible();

        // We check if it contains the continuous limit 1 + μ term text
        await expect(eqBlock).toContainText('μ');

        // Check the System Equation block further down as well
        const mathSystemBlock = page.locator('.equation-system-block');
        await expect(mathSystemBlock).toBeVisible();
        await expect(mathSystemBlock).toContainText('μ');
    });
});
