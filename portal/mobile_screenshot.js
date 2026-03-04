import { chromium, devices } from 'playwright';

(async () => {
    console.log("Starting mobile diagnostic trace...");
    const mobile = devices['Pixel 5'];

    const browser = await chromium.launch({ headless: true });
    const context = await browser.newContext({
        ...mobile
    });
    const page = await context.newPage();

    page.on('console', msg => console.log('BROWSER:', msg.text()));

    await page.goto('http://127.0.0.1:5173/');
    console.log("Loaded homepage.");

    await page.waitForTimeout(1000);

    const mobileToggle = page.locator('.mobile-toggle').first();
    if (await mobileToggle.isVisible()) {
        console.log("Hamburger visible. Clicking.");
        await mobileToggle.click();
    }

    console.log("Waiting for menu to animate or open...");
    await page.waitForTimeout(1000);

    console.log("Taking screenshot to see where scientistLink is...");
    await page.screenshot({ path: 'mobile_scratchpad.jpg', fullPage: true });

    const scientist = page.locator('.nav-links a:has-text("For Researchers")').first();
    const isVis = await scientist.isVisible();
    const box = await scientist.boundingBox();
    console.log("Scientist Link Visible:", isVis, "Box:", box);

    await browser.close();
})();
