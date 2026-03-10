import { test, expect } from '@playwright/test';

test.describe('Validation Dashboard Fallback', () => {

    test('UI renders API OFFLINE instead of infinite loading when backend crashes', async ({ page }) => {
        // Intercept the /api/lab/health call and mock a 500 Internal Server Error
        await page.route('/api/lab/health', async route => {
            await route.fulfill({
                status: 500,
                contentType: 'text/plain',
                body: 'Internal Server Error'
            });
        });

        // Navigate to the Lab portal
        await page.goto('http://127.0.0.1:5174/');
        await page.waitForTimeout(1000); // 1 second buffer just in case
        
        // Validation Dashboard lives under the Validation Core tab
        await page.locator('text=Validation Core').first().click();

        // Wait a small bit for Svelte to catch the 500 error and update state
        await page.waitForTimeout(1000);

        // Instead of 'loading...', it should explicitly show the API UNAVAILABLE state
        await expect(page.locator('text=API ERROR').first()).toBeVisible();
        await expect(page.locator('text=API UNAVAILABLE').first()).toBeVisible();
    });

});
