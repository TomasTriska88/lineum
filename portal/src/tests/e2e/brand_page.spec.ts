import { test, expect } from '@playwright/test';

test.describe('Brand Page SSR & Rendering', () => {

    const paths = [
        { url: '/brand', lang: 'en', expectedText: 'Brand Assets' },
        { url: '/cs/brand', lang: 'cs', expectedText: 'Značka a Press Kit' },
        { url: '/de/brand', lang: 'de', expectedText: 'Markenwerte & Press Kit' },
        { url: '/ja/brand', lang: 'ja', expectedText: 'ブランドアセット＆プレスキット' }
    ];

    for (const { url, lang, expectedText } of paths) {
        test(`loads brand page in ${lang} without 500 errors`, async ({ page }) => {
            // Wait until networkidle to ensure all SSR hydration is successful
            const response = await page.goto(url, { waitUntil: 'networkidle' });

            // Assert we did not get a 500 error
            expect(response?.status()).toBe(200);

            // Verify the specific H1 text is visible in the DOM
            const heading = page.locator('h1').first();
            await expect(heading).toContainText(expectedText);

            // Verify the Color Palette grid rendered correctly
            const cyanCard = page.locator('.tech-card').first();
            await expect(cyanCard).toBeVisible();

            // Verify download links exist
            const downloadLink = page.locator('a[download]').first();
            await expect(downloadLink).toHaveAttribute('href', /.*lineum-logo-static\.svg/);
        });
    }

});
