import { test, expect } from './base';

test.describe('Global Layout Safeties', () => {

    test('Critical content elements must not overlap with the persistent navigation menu', async ({ page }) => {

        // Function to check overlap on a given page
        async function checkOverlap(path: string, contentSelector: string) {
            await page.goto(path);

            // Wait for both the nav and the content element to be rendered
            // We measure the visible `.nav-content` rather than `<nav>` because the `<nav>` wrapper 
            // legally contains hidden dropdown menus that stretch hundreds of pixels into the document mathematically.
            const nav = page.locator('.nav-content').first();
            await expect(nav).toBeVisible();

            const contentElement = page.locator(contentSelector).first();
            await expect(contentElement).toBeVisible();

            // Give layout engines a moment to settle
            await page.waitForTimeout(500);

            // Fetch the bounding box coordinates
            const navBox = await nav.boundingBox();
            const contentBox = await contentElement.boundingBox();

            expect(navBox).not.toBeNull();
            expect(contentBox).not.toBeNull();

            // The bottom of the navigation bar (y + height) must be geographically 
            // HIGHER on the screen (lower number) than the top (y) of the content
            const navBottomEdge = navBox!.y + navBox!.height;
            const contentTopEdge = contentBox!.y;

            // We allow a tiny subpixel tolerance, but strictly require content > nav
            expect(contentTopEdge).toBeGreaterThanOrEqual(navBottomEdge - 1);
        }

        // Test the internal page standard flow where global layout padding matters
        await checkOverlap('/', '.hero-content h1');
        await checkOverlap('/about', 'h1');
        await checkOverlap('/wiki', 'h1');
        await checkOverlap('/brand', 'h1');
        await checkOverlap('/api-solutions', 'h1');

    });

});
