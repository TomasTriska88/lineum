import { test } from '@playwright/test';
import path from 'path';

test('screenshot comprehensive mockups', async ({ page }) => {
    const htmlPath = path.resolve('../.scratch/social-mockups.html');
    await page.goto(`file://${htmlPath}`);
    await page.setViewportSize({ width: 800, height: 2600 }); // Taller to fit everything

    // Wait to ensure all bulky local images are fully painted by the engine
    await page.waitForTimeout(2000);

    await page.screenshot({ path: '../.scratch/mockup-results-extended.png', fullPage: true });
});
