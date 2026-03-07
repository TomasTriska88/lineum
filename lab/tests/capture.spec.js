import { test, expect } from '@playwright/test';

test('Capture Lab Screenshots', async ({ page }) => {
    // 1) Validation Core
    await page.goto('/');
    await page.click('text="Validation Core"');
    await page.waitForTimeout(3000);
    await page.screenshot({ path: '../.scratch/val_core_screenshot.png', fullPage: true });

    // 2) Claims List
    await page.click('text="Claims"');
    await page.waitForTimeout(3000);

    const claimItems = await page.locator('.claim-item').count();
    console.log(`Rendered claims in UI: ${claimItems}`);

    await page.screenshot({ path: '../.scratch/claims_list_screenshot.png', fullPage: true });

    // 3) Claim Detail
    const firstClaim = page.locator('.claim-item').first();
    if (await firstClaim.count() > 0) {
        await firstClaim.click();
        await page.waitForTimeout(2000);
        await page.screenshot({ path: '../.scratch/claim_detail_screenshot.png', fullPage: true });
    }
});
