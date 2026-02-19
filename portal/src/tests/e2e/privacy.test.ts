import { test, expect } from './base';

test.describe('GDPR & Privacy Compliance', () => {


    test('Cookie Banner should appear on first visit', async ({ page }) => {
        await page.goto('/');

        // Wait for banner animation buffer (it has a 1s delay in component)
        await page.waitForTimeout(1500);

        const banner = page.locator('.cookie-banner');
        await expect(banner).toBeVisible();
        await expect(banner).toContainText('We use cookies');
    });

    test('Accepting cookies should hide the banner and persist consent', async ({ page }) => {
        await page.goto('/');
        await page.waitForTimeout(1500);

        const banner = page.locator('.cookie-banner');
        await expect(banner).toBeVisible();

        await page.getByRole('button', { name: 'Accept' }).click();
        await expect(banner).toBeHidden();

        // Reload to verify persistence
        await page.reload();
        await page.waitForTimeout(1500); // Wait in case it would reappear
        await expect(banner).toBeHidden();

        // Verify localStorage
        const consent = await page.evaluate(() => localStorage.getItem('cookie_consent'));
        expect(consent).toBe('accepted');
    });

    test('Privacy Policy page should exist and contain required info', async ({ page }) => {
        await page.goto('/privacy');

        await expect(page.locator('h1')).toHaveText('Privacy Policy');

        // Check for key sections
        await expect(page.locator('body')).toContainText('Session Cookies');
        await expect(page.locator('body')).toContainText('Google');
        await expect(page.locator('body')).toContainText('Gemini API');
    });

    test('Banner "Privacy Policy" link should work', async ({ page }) => {
        await page.goto('/');
        await page.waitForTimeout(1500);

        const link = page.locator('.cookie-banner a[href="/privacy"]');
        await expect(link).toBeVisible();
        await link.click();
        await expect(page).toHaveURL(/.*\/privacy/);
    });

    test('Cookie Banner should have higher z-index than Resonance Deck', async ({ page }) => {
        await page.goto('/');
        await page.waitForTimeout(1500);

        // Check availability first
        const bannerCount = await page.locator('.cookie-banner').count();
        const deckCount = await page.locator('.resonance-wrapper').count();

        console.log(`[DEBUG] Counts: Banner=${bannerCount}, Deck=${deckCount}`);

        if (bannerCount === 0) {
            console.log("[DEBUG] Banner not found!");
            expect(bannerCount).toBeGreaterThan(0);
        }

        // If simple logic failed, try computing style directly
        const bannerZ = await page.locator('.cookie-banner').evaluate((el) => {
            return window.getComputedStyle(el).zIndex;
        });

        const deckZ = await page.locator('.resonance-wrapper').evaluate((el) => {
            return window.getComputedStyle(el).zIndex;
        });

        console.log(`[DEBUG] Banner Z: "${bannerZ}", Deck Z: "${deckZ}"`);

        const bZ = bannerZ === 'auto' ? 0 : parseInt(bannerZ, 10) || 0;
        const dZ = deckZ === 'auto' ? 0 : parseInt(deckZ, 10) || 0;

        expect(bZ, `Banner Z (${bZ}) should be > Deck Z (${dZ})`).toBeGreaterThan(dZ);
    });
});
