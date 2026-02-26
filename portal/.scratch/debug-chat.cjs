const { chromium } = require('playwright');

(async () => {
    const browser = await chromium.launch();
    const page = await browser.newPage();

    // Test Japanese
    console.log("Testing JA...");
    await page.goto('http://localhost:5173/ja');
    await page.waitForTimeout(2000);
    await page.locator('.deck-main').click();
    await page.waitForTimeout(1000);

    const messages = await page.locator('.msg.model').allInnerTexts();
    console.log("JA Messages:", messages);

    // Test German
    console.log("\nTesting DE...");
    await page.goto('http://localhost:5173/de');
    await page.waitForTimeout(2000);
    await page.locator('.deck-main').click();
    await page.waitForTimeout(1000);

    const de_messages = await page.locator('.msg.model').allInnerTexts();
    console.log("DE Messages:", de_messages);

    await browser.close();
})();
