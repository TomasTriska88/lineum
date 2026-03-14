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

        await page.route('/api/lab/history', async route => { await route.fulfill({ status: 200, contentType: 'application/json', body: '[]' }); });
        await page.route('/data/manifest.json', async route => { await route.fulfill({ status: 200, contentType: 'application/json', body: '[]' }); });

        // Navigate to the Lab portal
        await page.goto('/');
        await page.waitForTimeout(1000); // 1 second buffer just in case
        
        // Validation Dashboard lives under the Validation Core tab
        await page.locator('text=Validation Core').first().click();

        // Wait a small bit for Svelte to catch the 500 error and update state
        await page.waitForTimeout(1000);

        // Instead of 'loading...', it should explicitly show the API UNAVAILABLE state
        // We only check for the primary status badge
        await expect(page.locator('.badge-status').filter({ hasText: 'API UNAVAILABLE' }).first()).toBeVisible();
    });

});
