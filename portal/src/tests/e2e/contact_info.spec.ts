import { test, expect } from '@playwright/test';
import { config } from '../../lib/config';

test.describe('Legal Contact Information', () => {

    test('should display legal info on About page based on config', async ({ page }) => {
        await page.goto('/about');

        // Wait for page to render
        await page.waitForSelector('.content-block');

        // Verify Legal Entity links are present and correct
        const justiceLink = page.locator(`a[href*="or.justice.cz/ias/ui/rejstrik-$firma?nazev="]`);
        await expect(justiceLink).toBeVisible();

        const icLink = page.locator(`a[href*="or.justice.cz/ias/ui/rejstrik-$firma?ico="]`);
        await expect(icLink).toBeVisible();

        const mapsLink = page.locator(`a[href*="maps.google.com/?q="]`);
        await expect(mapsLink).toBeVisible();

        if (config.brand.phone) {
            const phoneLink = page.locator(`a[href*="tel:"]`);
            await expect(phoneLink).toBeVisible();
        }

        const mailtoLink = page.locator(`a[href*="mailto:"]`);
        await expect(mailtoLink).toBeVisible();
    });

    test('should display persistent contact footer containing company and phone', async ({ page }) => {
        await page.goto('/');

        // The footer should be present on the home page (and all others via layout)
        const footer = page.locator('.contact-footer');
        await expect(footer).toBeVisible();

        // Should contain the basic components
        await expect(footer).toContainText(config.brand.name);
        await expect(footer).toContainText(config.brand.phone);
    });
});
