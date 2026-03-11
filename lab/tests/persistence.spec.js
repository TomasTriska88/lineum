import { test, expect } from '@playwright/test';

test.use({
    baseURL: 'http://127.0.0.1:5174',
    viewport: { width: 1280, height: 720 },
    testIdAttribute: 'id'
});

test.describe('Lab UI Persistence Tests', () => {

    test('Defaults to #simulator on empty hash', async ({ page }) => {
        // Clear localStorage first to ensure clean state
        await page.goto('/');
        await page.evaluate(() => localStorage.clear());
        
        // Go to root explicitly with no hash
        await page.goto('/');
        
        // Wait for hash to automatically change to #simulator
        await expect(async () => {
            const url = page.url();
            expect(url).toContain('#simulator');
        }).toPass({ timeout: 5000 });
        
        // Verify simulator canvas is NOT dimmed (meaning it is active)
        await expect(page.locator('.canvas-container')).not.toHaveClass(/dimmed/);
    });

    test('Persists main section after reload', async ({ page }) => {
        await page.goto('/');
        page.on('console', msg => console.log('BROWSER:', msg.text()));

        // Wait for hydration
        await page.waitForSelector('.top-nav', { state: 'visible' }).catch(() => { });

        // Navigate to Whitepaper Claims via UI button to ensure SvelteKit state triggers
        await page.locator('nav').getByRole('button', { name: 'Claims' }).click();

        // Verify Whitepaper Claims is visible
        await expect(page.locator('.claims-container')).toBeVisible({ timeout: 10000 });

        // Log state before reload
        const stateBefore = await page.evaluate(() => {
            return {
                hash: window.location.hash,
                storage: localStorage.getItem('lab_main_mode')
            };
        });
        console.log("PLAYWRIGHT BEFORE RELOAD:", stateBefore);

        // Reload the page
        await page.reload();

        // Ensure we didn't jump back to the simulator
        await expect(page.locator('.claims-container')).toBeVisible({ timeout: 10000 });
        // The canvas should be hidden because the mainMode is not simulator
        await expect(page.locator('.canvas-container')).not.toBeVisible();
    });

    test('Persists WhitepaperClaims selected claim and filters', async ({ page }) => {
        // Clear localStorage first to ensure clean state
        await page.goto('/');
        await page.evaluate(() => localStorage.clear());

        // Go to whitepaper claims
        await page.goto('/#whitepaper');
        await expect(page.locator('.claims-container')).toBeVisible({ timeout: 10000 });

        // Set filters (3rd select is Testability)
        const selectors = page.locator('.tag-select');
        await selectors.nth(2).selectOption('TESTABLE_NOW');

        // Select a claim (just click the first one that appears)
        await page.locator('.claim-item').first().click();

        // Check local storage directly before reload to confirm our script works
        const storedSelectedClaimBefore = await page.evaluate(() => localStorage.getItem('wc_selected_claim'));
        expect(storedSelectedClaimBefore).not.toBeNull();

        // Reload
        await page.reload();

        // Ensure filters persisted
        const testabilityValue = await page.locator('.tag-select').nth(2).inputValue();
        expect(testabilityValue).toBe('TESTABLE_NOW');

        // Check local storage directly after reload
        const storedSelectedClaim = await page.evaluate(() => localStorage.getItem('wc_selected_claim'));
        expect(storedSelectedClaim).not.toBeNull();
        expect(storedSelectedClaim).toBe(storedSelectedClaimBefore);
    });

});
