import { test, expect } from '@playwright/test';

// This test ensures that the SvelteKit framework successfully compiles the SSR build
// and doesn't crash with a "500 Internal Error" due to Paraglide or Vite dependency mismatch.
test.describe('SSR Compilation & 500 Error Guard', () => {

    test('English homepage should return valid SSR rendered HTML without 500 error', async ({ page, request }) => {
        // First check the raw HTTP status
        const response = await request.get('/');
        expect(response.ok()).toBeTruthy();
        expect(response.status()).not.toBe(500);

        // Then check if the page actually loads in the browser
        await page.goto('/');
        
        // Ensure "Internal Error" from Vite is not present on the page
        const bodyText = await page.locator('body').innerText();
        expect(bodyText).not.toContain('Internal Error');

        // Verify the Paraglide translation variables are rendering correctly
        await expect(page.locator('html')).toHaveAttribute('lang', 'en');
        await expect(page.locator('h1').first()).toBeVisible();
    });

    test('Japanese translated route should compile and render correctly', async ({ page, request }) => {
        // Check raw HTTP status
        const response = await request.get('/ja');
        expect(response.ok()).toBeTruthy();
        expect(response.status()).not.toBe(500);

        await page.goto('/ja');
        
        // Ensure not crashed
        const bodyText = await page.locator('body').innerText();
        expect(bodyText).not.toContain('Internal Error');

        // Check if correct language is injected by Paraglide into the HTML tag
        await expect(page.locator('html')).toHaveAttribute('lang', 'ja');
    });

});
