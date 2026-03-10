import { chromium } from 'playwright';

(async () => {
    const browser = await chromium.launch();
    const context = await browser.newContext({
        viewport: { width: 1280, height: 800 }
    });
    const page = await context.newPage();

    await page.goto('http://localhost:5173/');
    await page.waitForTimeout(1000); // Let CSS load

    // Hover Ecosystem to open mega dropdown
    const ecoBtn = page.getByRole('button', { name: /Ecosystem/ });
    await ecoBtn.hover();
    await page.waitForTimeout(500);
    await page.screenshot({ path: 'mega_dropdown_desktop.png', fullPage: false });

    // Hover Language toggle
    const langBtn = page.locator('.lang-toggle');
    await langBtn.hover();
    await page.waitForTimeout(500);
    await page.screenshot({ path: 'lang_dropdown_desktop.png', fullPage: false });

    console.log("Screenshots taken.");
    await browser.close();
})();
