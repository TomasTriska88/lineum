import { test, expect } from '@playwright/test';

test.use({
    baseURL: 'http://localhost:5174',
    viewport: { width: 1280, height: 720 },
    testIdAttribute: 'id'
});

test.describe('Lab UI Persistence Tests', () => {

    test('Persists main section after reload', async ({ page }) => {
        await page.goto('/');

        // Wait for hydration
        await page.waitForSelector('.tab-nav', { state: 'visible' }).catch(() => { });

        // Navigate to Whitepaper Claims via URL Hash directly to test the new functionality
        await page.goto('/#whitepaper');

        // Verify Whitepaper Claims is visible
        await expect(page.locator('.claims-container')).toBeVisible({ timeout: 10000 });

        // Reload the page
        await page.reload();

        // Ensure we didn't jump back to the simulator
        await expect(page.locator('.claims-container')).toBeVisible({ timeout: 10000 });
        // The canvas should be dimmed because the mainMode is not simulator
        await expect(page.locator('.canvas-container')).toHaveClass(/dimmed/);
    });

    test('Persists WhitepaperClaims selected claim and filters', async ({ page }) => {
        // Clear localStorage first to ensure clean state
        await page.goto('/');
        await page.evaluate(() => localStorage.clear());

        // Go to whitepaper claims
        await page.goto('/#whitepaper');
        await expect(page.locator('.claims-container')).toBeVisible({ timeout: 10000 });

        // Set filters (2nd select is Testability)
        const selectors = page.locator('.tag-select');
        await selectors.nth(1).selectOption('TESTABLE_NOW');

        // Select a claim (just click the first one that appears)
        await page.locator('.claim-item').first().click();

        // Check local storage directly before reload to confirm our script works
        const storedSelectedClaimBefore = await page.evaluate(() => localStorage.getItem('wc_selected_claim'));
        expect(storedSelectedClaimBefore).not.toBeNull();

        // Reload
        await page.reload();

        // Ensure filters persisted
        const testabilityValue = await page.locator('.tag-select').nth(1).inputValue();
        expect(testabilityValue).toBe('TESTABLE_NOW');

        // Check local storage directly after reload
        const storedSelectedClaim = await page.evaluate(() => localStorage.getItem('wc_selected_claim'));
        expect(storedSelectedClaim).not.toBeNull();
        expect(storedSelectedClaim).toBe(storedSelectedClaimBefore);
    });

});
