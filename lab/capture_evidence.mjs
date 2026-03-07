import { chromium } from 'playwright';

(async () => {
    console.log("Launching browser...");
    const browser = await chromium.launch();
    const page = await browser.newPage();

    console.log("Navigating to Lab...");
    await page.goto('http://localhost:5174/lab');

    await page.click('button:has-text("Claims")');
    await page.waitForTimeout(1000);

    console.log("Running Verify All...");
    await page.click('button.verify-all-btn');
    await page.waitForTimeout(5000);

    console.log("Capturing CL-CORE-001...");
    await page.click('.claim-id:has-text("CL-CORE-001")');
    await page.waitForTimeout(2000);
    await page.screenshot({ path: 'C:/Users/Tomáš/.gemini/antigravity/brain/b9c82bdd-99a7-4dd5-a1d7-9a40d6fc2271/experimental_evidence.jpg', fullPage: true });

    // Use native Playwright locator for the text area and pane
    const paneA = await page.locator('.claim-detail').innerText();
    const markdownA = await page.inputValue('.evidence-textarea').catch(() => "NO TEXTAREA FOUND");
    console.log("=== CL-CORE-001 EVIDENCE EXPORT ===");
    console.log(markdownA);

    console.log("Capturing CL-001...");
    await page.click('.claim-id:has-text("CL-001")');
    await page.waitForTimeout(2000);
    await page.screenshot({ path: 'C:/Users/Tomáš/.gemini/antigravity/brain/b9c82bdd-99a7-4dd5-a1d7-9a40d6fc2271/excluded_evidence.jpg', fullPage: true });

    const paneB = await page.locator('.claim-detail').innerText();
    console.log("=== CL-001 FULL DETAIL PANE ===");
    console.log(paneB);

    await browser.close();
    console.log("Done.");
})();
