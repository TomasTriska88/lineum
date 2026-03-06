import { chromium } from 'playwright';

(async () => {
    const browser = await chromium.launch({ headless: true });
    const page = await browser.newPage({ viewport: { width: 1280, height: 800 } });

    await page.goto('http://localhost:5174/');
    await page.click("text='RA-2: Stable Bound State'");
    await page.click("text='RUN SCENARIO'");

    // Wait for the img to appear (meaning backend finished)
    await page.waitForSelector('img[alt="Validation Mathplot"]', { timeout: 30000 });

    await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
    await page.waitForTimeout(1000);

    const canvas = await page.$('.interactive-chart-wrapper canvas');
    if (canvas) {
        const box = await canvas.boundingBox();
        if (box) {
            // Move to the center of the chart
            await page.mouse.move(box.x + box.width / 2, box.y + box.height / 2);
            await page.waitForTimeout(500); // Wait for tooltip animation

            const wrapper = await page.$('.interactive-chart-wrapper');
            await wrapper.screenshot({ path: '../chart_tooltip_proof.png' });
            console.log('Screenshot saved to chart_tooltip_proof.png');
        } else {
            console.log('Canvas box not found');
        }
    } else {
        console.log('Canvas not found');
    }

    await browser.close();
})();
