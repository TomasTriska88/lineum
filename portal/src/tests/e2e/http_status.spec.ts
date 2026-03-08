import { test, expect } from '@playwright/test';

test.describe('HTTP Status Code Guards', () => {

    const routes = [
        '/',
        '/about',
        '/api-solutions'
    ];

    for (const route of routes) {
        test(`Route ${route} should not return an HTTP 500 error`, async ({ page }) => {
            const response = await page.goto(route);

            // Note: Since this is often static/client-routed in SvelteKit for fallback pages,
            // we primarily want to ensure it isn't an explicit 500 and the page doesn't show a 500 error component.
            expect(response?.status()).toBeLessThan(500);

            // Double check there's no visible internal server error message
            const pageText = await page.locator('body').innerText();
            expect(pageText).not.toContain('Internal Error');
            expect(pageText).not.toContain('500');
        });
    }
});
