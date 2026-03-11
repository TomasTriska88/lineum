import { test, expect } from '@playwright/test';

test.describe('Root Cause Diagnostics', () => {

    test('Trace Console and Network during Audit Generation', async ({ page }) => {
        const consoleLogs = [];
        const networkLogs = [];

        page.on('console', msg => {
            consoleLogs.push(`[CONSOLE ${msg.type()}] ${msg.text()}`);
            console.log(`[CONSOLE ${msg.type()}] ${msg.text()}`);
        });

        page.on('response', response => {
            networkLogs.push(`[NET] ${response.status()} ${response.url()}`);
        });

        page.on('framenavigated', frame => {
            consoleLogs.push(`[NAV] Frame navigated to ${frame.url()}`);
            console.log(`[NAV] Frame navigated to ${frame.url()}`);
        });

        await page.goto('http://127.0.0.1:5174/#whitepaper');
        await page.waitForSelector('.claims-container', { state: 'visible', timeout: 10000 });

        // Trigger audit generation
        await page.click('button:has-text("Generate Audit Contract")');

        // It might ask for CPU confirmation due to ExecutionPolicy
        try {
            await page.click('button:has-text("Continue on CPU")', { timeout: 3000 });
        } catch (e) {
            // Might not need confirmation or we missed it
        }

        // Wait for generation
        // Wait up to 300s since this takes 2-5 minutes
        try {
            await page.waitForTimeout(30000); // 30s pause
            console.log("Checking logs after 30s");
        } catch (e) {
            console.log("Timeout waiting for audit");
        }

        const fs = require('fs');
        fs.writeFileSync('diagnostics.txt', consoleLogs.join('\n') + "\n\n" + networkLogs.join('\n'));
    });
});
