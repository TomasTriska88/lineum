import { chromium } from 'playwright';

(async () => {
    console.log("Starting diagnostic trace...");
    const browser = await chromium.launch({ headless: true });
    const page = await browser.newPage();

    page.on('console', msg => console.log('PAGE LOG:', msg.text()));
    page.on('pageerror', err => console.log('PAGE ERROR:', err.message));

    await page.route(/\/entity\/.*\/memory\/imprints/, async route => {
        console.log("-> INTERCEPTED REQUEST:", route.request().method(), route.request().url());

        if (route.request().method() === "OPTIONS") {
            return await route.fulfill({
                status: 200,
                headers: {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET, OPTIONS, DELETE',
                    'Access-Control-Allow-Headers': '*'
                }
            });
        }

        const mockImprint = {
            status: "success",
            imprints: [
                {
                    imprint_id: "test-hash-12345",
                    ts: Date.now() / 1000,
                    grid: 64,
                    dt: 1.0,
                    seed: 99,
                    delta_mu_path: "C:\\path\\mock.npz",
                    stats: { l1: 15.2, max: 2.1, ratio_tau: 0.05 },
                    affect_v0: { arousal: 1000.5, certainty: 0.95, valence: 0.1, resonance: 0.0 }
                }
            ]
        };

        return await route.fulfill({
            status: 200,
            contentType: 'application/json',
            headers: { 'Access-Control-Allow-Origin': '*' },
            body: JSON.stringify(mockImprint)
        });
    });

    console.log("Navigating to http://localhost:5173/journal...");
    await page.goto('http://localhost:5173/journal', { waitUntil: 'domcontentloaded' });

    console.log("Waiting 2s for Reactivity frame...");
    await page.waitForTimeout(2000);

    console.log("Extracting main document body...");
    try {
        const content = await page.locator('.journal-container').innerHTML();
        require('fs').writeFileSync('dump.html', content);
        console.log("HTML RENDERED to dump.html");
    } catch (e) {
        console.log("Locator failed:", e.message);
    }

    await browser.close();
})();
