import { chromium, devices } from 'playwright';

(async () => {
    const browser = await chromium.launch();

    // Setup for iPhone 13 viewport
    const context = await browser.newContext({
        ...devices['iPhone 13']
    });
    const page = await context.newPage();

    await page.goto('http://localhost:5173/');
    await page.waitForTimeout(1000); // Let CSS load

    // Click Hamburger
    await page.getByRole('button', { name: 'Toggle Menu' }).click();
    await page.waitForTimeout(500);

    // Expand Ecosystem
    await page.getByRole('button', { name: 'Ecosystem ▼' }).click();
    await page.waitForTimeout(500);

    await page.screenshot({ path: 'new_mobile_nav_test.png', fullPage: true });

    console.log("Screenshot taken: new_mobile_nav_test.png");
    await browser.close();
})();
