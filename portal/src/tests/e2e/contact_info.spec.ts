import { test, expect } from '@playwright/test';
import { config } from '../../lib/config';

test.describe('Legal Contact Information', () => {

    test('should display legal info on About page based on config', async ({ page }) => {
        await page.goto('/about');

        // Wait for page to render
        await page.waitForSelector('.content-block');

        // Locate all text in content-blocks
        const contents = await page.locator('.content-block').allTextContents();
        const textContent = contents.join(' ');

        // Assert that the text includes config info
        expect(textContent).toContain(config.brand.legalName);
        expect(textContent).toContain(config.brand.ic);
        expect(textContent).toContain(config.brand.address);

        // Ensure phone is displayed
        if (config.brand.phone) {
            expect(textContent).toContain(config.brand.phone);
        }
    });
});
