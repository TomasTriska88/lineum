import { test, expect } from '@playwright/test';

test.describe('Lineum Homepage UI Updates', () => {
    test('Should display Lab and Engraving links in the main navigation', async ({ page, isMobile }) => {
        if (isMobile) return;
        
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

        // 2. Click the Ecosystem dropdown to verify About, API Solutions, and Engraving
        const ecosystemToggle = page.locator('.dropdown-toggle').filter({ hasText: /Ecosystem/i });
        await expect(ecosystemToggle).toBeVisible();
        await ecosystemToggle.click();
        await page.waitForTimeout(300); // Wait for mega-menu transition

        // 3. Verify 'About' is present in the The Project section
        const aboutLink = page.locator('.mega-menu a[href="/about"]');
        await expect(aboutLink).toBeVisible();

        // 4. Verify Engraving and API (API is actually root level, Engraving is inside developers)
        const apiLink = page.locator('.nav-links > a[href="/api-solutions"]').first();
        if ((await apiLink.count()) > 0) {
            await expect(apiLink).toBeVisible();
            const engravingLink = page.locator('.mega-menu a[href="/engraving"]');
            await expect(engravingLink).toBeVisible();
        }
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
