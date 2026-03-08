import { chromium } from 'playwright';
import path from 'path';
import fs from 'fs';

(async () => {
    const browser = await chromium.launch();
    const page = await browser.newPage({ viewport: { width: 1200, height: 900 } });

    console.log("Navigating to Lab...");
    await page.goto('http://localhost:5174/');
    await page.waitForTimeout(3000); // 3 seconds to let API load

    console.log("Opening Claims Tab...");
    await page.click('text=CLAIMS');
    await page.waitForTimeout(1000);

    console.log("Waiting for claims...");
    await page.waitForSelector('.claim-item', { timeout: 10000 });

    console.log("Clicking CL-CORE-001...");
    await page.click('text=CL-CORE-001');
    await page.waitForTimeout(1000);

    console.log("Scrolling to traceability box...");
    await page.evaluate(() => {
        const box = document.querySelector('.traceability-box');
        if (box) box.scrollIntoView();
    });

    await page.waitForTimeout(500);

    const captureDir = process.env.LINEUM_UI_CAPTURE_DIR || path.join(process.cwd(), '.scratch', 'screenshots');
    if (!fs.existsSync(captureDir)) {
        fs.mkdirSync(captureDir, { recursive: true });
    }
    const screenshotPath = path.join(captureDir, 'verified_traceability_table.png');
    await page.screenshot({ path: screenshotPath });
    console.log("Screenshot saved at:", screenshotPath);

    await browser.close();
})();
