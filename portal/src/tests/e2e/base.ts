import { test as base } from '@playwright/test';

export const test = base.extend({
    page: async ({ page }, use) => {
        // Strict Network Blocking
        await page.route('**/*', async (route) => {
            const url = route.request().url();

            // Allow 127.0.0.1 (vite server) and data URIs (inline assets)
            if (url.includes('127.0.0.1') || url.startsWith('data:')) {
                await route.continue();
                return;
            }

            // Allow Google Fonts (as requested)
            if (url.includes('fonts.googleapis.com') || url.includes('fonts.gstatic.com')) {
                await route.continue();
                return;
            }

            // Block everything else
            console.error(`Blocked external request to: ${url}`);
            await route.abort();
        });
        await use(page);
    }
});

export { expect } from '@playwright/test';
