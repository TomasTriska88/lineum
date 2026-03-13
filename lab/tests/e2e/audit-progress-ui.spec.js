import { test, expect } from '@playwright/test';

test.describe('Audit Progress Panel UI Constraints', () => {
    test.beforeEach(async ({ page }) => {
        // Intercept foundational API routes to prevent ECONNREFUSED when FastAPI is offline
        await page.route('/api/lab/health', async route => {
            await route.fulfill({
                status: 200,
                contentType: 'application/json',
                body: JSON.stringify({ status: "online", version: "mocked" })
            });
        });

        await page.route('/api/lab/statistics', async route => {
            await route.fulfill({
                status: 200,
                contentType: 'application/json',
                body: JSON.stringify({ total_claims: 0, verified_claims: 0 })
            });
        });

        await page.route('/api/lab/claim_results', async route => {
            await route.fulfill({
                status: 200,
                contentType: 'application/json',
                body: JSON.stringify({
                    "sim-001": { 
                        "status": "verifying",
                        "metrics": { "fidelity": 0.999 } 
                    }
                })
            });
        });

        await page.route('/api/lab/history', async route => {
            await route.fulfill({ status: 200, contentType: 'application/json', body: '[]' });
        });

        await page.route('/data/manifest.json', async route => {
            await route.fulfill({
                status: 200,
                contentType: 'application/json',
                body: JSON.stringify([{
                    "id": "claim_ui_constraint_test",
                    "status": "pending",
                    "description": "Dummy claim to force UI rendering"
                }])
            });
        });

        // Intercept audit routes to simulate a running state with extremely long log texts
        await page.route('/api/lab/audit/config', async route => {
            await route.fulfill({
                status: 200,
                contentType: 'application/json',
                body: JSON.stringify({
                    allowed: true,
                    execution_device: "cuda",
                    cuda_available: true,
                    canonical_audit_allowed_on_cuda: true
                })
            });
        });

        await page.route('/api/lab/audit/generate', async route => {
            await route.fulfill({ status: 200, body: 'OK' });
        });

        await page.route('/api/lab/audit/status', async route => {
            // Emulate an enormous log line that would previously break out of the button and cover the UI
            const longText = 'long_output_line_with_no_spaces_that_tests_word_breaking_' + 'A'.repeat(600) + ' ' + 'B'.repeat(400);
            await route.fulfill({
                status: 200,
                contentType: 'application/json',
                body: JSON.stringify({
                    state: "RUNNING",
                    phase: "VERIFYING_WAVE_CORE",
                    detail: longText
                })
            });
        });
    });

    test('Audit progress panel renders with bounded dimensions and does not overlay claims content', async ({ page }) => {
        await page.goto('/#claims');
        
        // Ensure UI is fully hydrated
        await expect(page.locator('.claims-sidebar')).toBeVisible();

        // Click the generate button to start polling (which hits the mocked endpoints and sets isGeneratingAudit = true)
        const generateBtn = page.locator('button.btn-generate-audit:not(.cancel)');
        await expect(generateBtn).toBeVisible();
        
        // Wait for auto-reconnect to lock the button and show the panel
        await expect(generateBtn).toBeDisabled({ timeout: 5000 });

        // 1. Assert the dedicated panel appears
        const progressPanel = page.locator('.audit-progress-panel');
        await expect(progressPanel).toBeVisible({ timeout: 2000 });

        // 2. Assert the panel is properly bounded
        const box = await progressPanel.boundingBox();
        expect(box.width).toBeLessThanOrEqual(452); // Max width allowed is 450 + 2px borders
        expect(box.height).toBeGreaterThan(50); // It should have some height

        // 3. Assert the long text is bounded inside the panel body and does not spill out
        const panelBody = progressPanel.locator('.panel-body');
        const bodyBox = await panelBody.boundingBox();
        expect(bodyBox.width).toBeLessThanOrEqual(box.width);
        
        // Let's verify CSS overflow and word-break are applied
        const overflowY = await panelBody.evaluate((el) => window.getComputedStyle(el).overflowY);
        const wordBreak = await panelBody.evaluate((el) => window.getComputedStyle(el).wordBreak);
        expect(overflowY).toBe('auto');
        expect(wordBreak).toBe('break-all');

        // 4. Check WhitepaperClaims status updates to AUDIT_RUNNING badge
        // Even if the claim status in the mocked /api/lab/health is something else, 
        // passing `isGeneratingAudit={true}` should force the "AUDIT_RUNNING" fallback badge visually.
        
        // Wait for the claims list to render at least one claim
        const firstClaim = page.locator('.claim-item').first();
        await expect(firstClaim).toBeVisible();
        await firstClaim.click(); // Open the claim
        
        // The badge next to the claim ID should show AUDIT_RUNNING
        const claimStatusBadge = firstClaim.locator('.claim-status');
        await expect(claimStatusBadge).toBeVisible();
        await expect(claimStatusBadge).toHaveText(/AUDIT_RUNNING/);
    });
});
