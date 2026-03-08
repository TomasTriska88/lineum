// import { chromium } from '@playwright/test';
import fs from 'fs';

(async () => {
    const browser = await chromium.launch();
    const context = await browser.newContext();
    const page = await context.newPage();

    page.on('console', msg => console.log('BROWSER LOG:', msg.text()));

    await page.route('**/health', async route => {
        route.fulfill({
            json: { active_contract: "LNC-AUDIT-TEST", contract_id: "LNC-AUDIT-TEST", audit_status: "AUDITED" }
        });
    });

    await page.route('**/api/lab/claim_results', async route => {
        const payload = {
            results: {
                "CL-CORE-001": {
                    resolved_claim_status: "SUPPORTED",
                    manifest_id: "manifest-success",
                    contract_id: "LNC-AUDIT-TEST",
                    audit_status: "AUDITED",
                    overall_pass: true,
                    is_stale: false,
                    traceability: {
                        overall_pass: true,
                        metrics: [
                            { metric_name: "f0_mean_hz", actual_value: 432.1, comparison_operator: "min:", threshold_rule: 430 }
                        ]
                    }
                }
            }
        };
        console.log("NODE: Fulfilling route with json:", JSON.stringify(payload));
        route.fulfill({ json: payload });
    });

    await page.goto('http://localhost:5174/');
    await page.click('text=Claims');
    await page.locator('.claim-item:has(span.claim-id:text-is("CL-CORE-001"))').click();
    await page.waitForTimeout(2000);
    await page.evaluate(() => {
        window._clipboardText = "";
        navigator.clipboard.writeText = async (text) => {
            window._clipboardText = text;
            return Promise.resolve();
        };
    });

    const assistantBtn = page.locator('button.agent-handoff');
    await assistantBtn.click();
    await page.waitForTimeout(500);

    const val = await page.evaluate(() => window._clipboardText);
    fs.writeFileSync('../.scratch/clipboard_dump.txt', val);
    console.log("Wrote to clipboard_dump.txt");

    await browser.close();
})();
