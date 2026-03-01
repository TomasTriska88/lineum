import { test, expect } from './base';

test.describe('Wiki Table of Contents (TOC)', () => {
    test.beforeEach(async ({ page }) => {
        // Clear sessionStorage to handle modal uniformly
        await page.goto('/wiki/01-core-lineum');
        await page.evaluate(() => sessionStorage.clear());
        await page.reload();

        // Acknowledge the warning modal to access the page content
        const modal = page.locator('.dialog-window');
        if (await modal.isVisible()) {
            await page.getByRole('button', { name: 'I Understand, Continue' }).click();
            await expect(modal).not.toBeVisible();
        }
    });

    test('should render dynamic table of contents based on markdown headers', async ({ page, isMobile }) => {
        const toc = page.locator('aside.toc');

        // On mobile, the TOC sidebar should be hidden via CSS
        if (isMobile) {
            await expect(toc).not.toBeVisible();
            return;
        }

        // The TOC should be visible
        await expect(toc).toBeVisible();

        // It should contain the "On this page" header
        await expect(toc.locator('h3', { hasText: 'On this page' })).toBeVisible();

        // It should contain links to sections extracted from the markdown
        const tocLinks = toc.locator('ul li a');
        const count = await tocLinks.count();
        expect(count).toBeGreaterThan(0);

        // Explicitly check for an H1 header ("1. Abstract")
        const h1Link = tocLinks.filter({ hasText: '1. Abstract' });
        await expect(h1Link).toBeVisible();

        // Explicitly check for an H2 header ("2. Motivation")
        const h2Link = tocLinks.filter({ hasText: '2. Motivation' });
        await expect(h2Link).toBeVisible();

        // Explicitly check for an H4 header ("4.3.1 Cross-Implementation Replication (advisory)")
        const h4Link = tocLinks.filter({ hasText: '4.3.1 Cross-Implementation Replication (advisory)' });
        await expect(h4Link).toBeVisible();

        // Verify that the first link correlates to an actual heading in the prose
        const firstLink = tocLinks.first();

        // Click the link to test navigation
        await firstLink.click();

        // Wait for potential smooth scroll
        await page.waitForTimeout(500);

        // The URL hash should update
        const currentUrl = page.url();
        expect(currentUrl).toContain('#');
    });
});
