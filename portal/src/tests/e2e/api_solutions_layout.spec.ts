import { test, expect } from './base';

test.describe('API Solutions Layout', () => {

    test('Hero section should not be obscured by the global navigation on the main page', async ({ page }) => {
        await page.goto('/api-solutions');

        // Wait for the main heading and the global header
        const heading = page.locator('h1', { hasText: 'Continuous routing API' });
        await expect(heading).toBeVisible();

        const nav = page.locator('nav');
        await expect(nav).toBeVisible();

        // Get their bounding boxes
        const headingBox = await heading.boundingBox();
        const navBox = await nav.boundingBox();

        expect(headingBox).not.toBeNull();
        expect(navBox).not.toBeNull();
        console.log("MAIN PAGE BOXES:", { headingBox, navBox });

        // Assert that the top of the heading is BELOW the bottom of the header
        if (headingBox && navBox) {
            const navBottom = navBox.y + navBox.height;
            expect(headingBox.y).toBeGreaterThanOrEqual(navBottom);
        }
    });

    test('Hero section should not be obscured by the global navigation on subdomain pages', async ({ page }) => {
        await page.goto('/api-solutions/urban-logistics');

        // Wait for the domain heading and the global header
        const heading = page.locator('h1', { hasText: 'Urban Traffic & Logistics' });
        await expect(heading).toBeVisible();

        const nav = page.locator('nav');
        await expect(nav).toBeVisible();

        // Get their bounding boxes
        const headingBox = await heading.boundingBox();
        const navBox = await nav.boundingBox();

        expect(headingBox).not.toBeNull();
        expect(navBox).not.toBeNull();
        console.log("SUBPAGE BOXES:", { headingBox, navBox });

        // Assert that the top of the heading is BELOW the bottom of the header
        if (headingBox && navBox) {
            const navBottom = navBox.y + navBox.height;
            expect(headingBox.y).toBeGreaterThanOrEqual(navBottom);
        }
    });

});
