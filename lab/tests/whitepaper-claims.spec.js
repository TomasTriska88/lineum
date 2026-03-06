import { test, expect } from '@playwright/test';
import { whitepaperClaims } from '../src/lib/data/claims.js';

test.describe('Whitepaper Claims MVP', () => {

    test('Schema Test: Every claim has required fields and valid enums', () => {
        const validStatuses = ['UNTESTED', 'SUPPORTED', 'CONTRADICTED'];
        const validTestabilities = ['TESTABLE_NOW', 'NEEDS_NEW_SCENARIO', 'NOT_TESTABLE_YET'];

        for (const claim of whitepaperClaims) {
            expect(claim).toHaveProperty('id');
            expect(claim).toHaveProperty('short_claim');
            expect(claim).toHaveProperty('human_claim');
            expect(claim).toHaveProperty('scientific_claim');
            expect(claim).toHaveProperty('what_it_is_not');
            expect(claim).toHaveProperty('source_file');
            expect(claim).toHaveProperty('source_anchor');
            expect(claim).toHaveProperty('tags');
            expect(Array.isArray(claim.tags)).toBeTruthy();

            expect(validStatuses).toContain(claim.status);
            expect(validTestabilities).toContain(claim.testability);

            expect(claim).toHaveProperty('test_reason');
        }

        // Specific Tag Distribution Hard Requirements
        const quarkTags = whitepaperClaims.filter(c => c.tags.some(t => ['quark', 'gluon', 'standard-model'].includes(t)));
        expect(quarkTags.length).toBeGreaterThanOrEqual(3);

        const psiTags = whitepaperClaims.filter(c => c.tags.includes('unified-psi-scale'));
        expect(psiTags.length).toBeGreaterThanOrEqual(3);

        const muTags = whitepaperClaims.filter(c => c.tags.some(t => ['mu', 'memory', 'topology'].includes(t)));
        expect(muTags.length).toBeGreaterThanOrEqual(2);
    });

    test('UI Test: Lists renders claims and details view shows source links', async ({ page }) => {
        await page.goto('/');

        // Navigate to Whitepapers mode
        await page.click('text=Whitepapers');

        // Verify Search/Filter elements exist
        await expect(page.locator('input[placeholder="Search claims..."]')).toBeVisible();
        await expect(page.locator('select.tag-select').first()).toBeVisible();

        // Verify the list has exactly the number of claims we defined
        const listItems = page.locator('.claim-item');
        await expect(listItems).toHaveCount(whitepaperClaims.length);

        // Click the first claim
        await listItems.first().click();

        // Verify Detail view shows critical Explain Pack and Source components
        await expect(page.locator('.detail-card h2')).toContainText(whitepaperClaims[0].short_claim);
        await expect(page.locator('.source-link a')).toContainText(whitepaperClaims[0].source_file);

        // Explain pack canon
        await expect(page.locator('.ep-liner')).toContainText('Human Translation');
        await expect(page.locator('text=Scientific Claim')).toBeVisible();
        await expect(page.locator('text=What this is NOT')).toBeVisible();

        // Testability logic check in UI
        if (whitepaperClaims[0].testability === 'TESTABLE_NOW') {
            await expect(page.locator('.run-btn')).toBeVisible();
        }
    });

    test('Mapping Test: Strict Gating and Audit Badge UI', async ({ page }) => {
        // Assert initial state: all claims UNTESTED
        for (const claim of whitepaperClaims) {
            expect(claim.status).toBe('UNTESTED');
        }

        // --- Mock State 1: NO AUDIT CONTRACT ---
        await page.route('http://127.0.0.1:8000/health', async route => {
            await route.fulfill({
                json: {
                    active_contract: null,
                    audit_status: "NONE",
                    current_build: "mock-hash (main)"
                }
            });
        });

        await page.goto('/');
        await page.click('text=Whitepapers');

        // Mock the verification API so Playwright doesn't wait for Vite proxy timeout
        await page.route('**/run_preset*', async route => {
            await route.fulfill({
                json: { manifest_id: "mock-123", overall_pass: true, message: "Mocked fetch" }
            });
        });

        // Check global navigation header to ensure audit generation button is present
        await expect(page.locator('.btn-generate-audit')).toBeVisible();

        // Find a TESTABLE_NOW claim
        const testableClaim = whitepaperClaims.find(c => c.testability === 'TESTABLE_NOW');
        await page.locator(`.claim-item:has(span.claim-id:text-is("${testableClaim.id}"))`).click();

        let runBtn = page.locator('.run-btn');
        await expect(runBtn).toBeVisible();
        await runBtn.click();

        // Wait for exploratory evidence box to definitively prove state transfer
        let exploratoryBox = page.locator('.evidence-box.exploratory');
        await expect(exploratoryBox).toBeVisible({ timeout: 15000 });

        // --- Mock State 2: AUDITED ---
        // Remock health
        await page.route('http://127.0.0.1:8000/health', async route => {
            await route.fulfill({
                json: {
                    contract_id: "LNC-AUDIT-MOCK123",
                    audit_status: "AUDITED",
                    contract_commit: "mock123",
                    current_build: "mock123 (main)",
                    summary_pass: 10,
                    summary_fail: 0
                }
            });
        });

        // Remount to trigger onMount health fetch
        await page.reload();
        await page.click('text=Whitepapers');
        // Check claim detail status directly (it relies on audit status)
        await page.locator(`.claim-item:has(span.claim-id:text-is("${testableClaim.id}"))`).click();

        // Take a screenshot of the claims interface
        await page.screenshot({ path: '../../output_wp/runs/_whitepaper_contract/audit_claims_view.png' });

        // Click same claim
        // Ensure the warning banner is gone now that the build is AUDITED
        await expect(page.locator('.audit-warning-banner')).not.toBeVisible();

        runBtn = page.locator('.run-btn');
        await runBtn.click();

        // Wait for canonical evidence box
        let canonicalBox = page.locator('.evidence-box.canonical');
        await expect(canonicalBox).toBeVisible({ timeout: 15000 });

        // Assert status transition to pure SUPPORTED or CONTRADICTED
        await expect(page.locator('.detail-card strong:has-text("SUPPORTED"), .detail-card strong:has-text("CONTRADICTED")')).toBeVisible();

        // Assert canonical evidence box contains the contract ID
        await expect(page.locator('.evidence-box.canonical .contract-id')).toContainText(/LNC-AUDIT-MOCK123/);
    });

    test('Integration Log Traceability Test', async ({ page }) => {
        // Mock health
        await page.route('http://127.0.0.1:8000/health', async route => {
            await route.fulfill({
                json: {
                    active_contract: "LNC-AUDIT-456",
                    contract_id: "LNC-AUDIT-456",
                    audit_status: "AUDITED",
                    contract_commit: "commit456",
                    current_build: "commit456 (main)",
                }
            });
        });

        // Mock empty integration log
        await page.route('http://127.0.0.1:8000/integration_log', async (route, request) => {
            if (request.method() === 'GET') {
                await route.fulfill({ json: { events: [] } });
            } else if (request.method() === 'POST') {
                await route.fulfill({ json: { status: "success" } });
            }
        });

        // Mock preset run
        await page.route('**/run_preset*', async route => {
            await route.fulfill({ json: { manifest_id: "manifest-789", overall_pass: true } });
        });

        await page.goto('/');
        await page.click('text=Whitepapers');

        // Check if Applied filter exists
        await expect(page.locator('select.tag-select').nth(1)).toBeVisible();

        // Select first TESTABLE claim
        const testableClaim = whitepaperClaims.find(c => c.testability === 'TESTABLE_NOW');
        await page.locator(`.claim-item:has(span.claim-id:text-is("${testableClaim.id}"))`).click();

        // Assert Applied banner says NOT APPLIED
        await expect(page.locator('.applied-banner')).toContainText('NOT APPLIED IN LOG');

        // Run Verification to generate the evidence block
        await page.locator('.run-btn').first().click();

        // Wait for Evidence Block Action generator area
        await expect(page.locator('.evidence-generator')).toBeVisible({ timeout: 15000 });

        // Assert Mark as Applied button exists
        const applyBtn = page.locator('button.mark-applied');
        await expect(applyBtn).toBeVisible();
        await expect(applyBtn).toContainText('Mark as Applied in Log');

        // Now mock the GET log response to return our new event so Svelte updates natively
        await page.unroute('http://127.0.0.1:8000/integration_log');
        await page.route('http://127.0.0.1:8000/integration_log', async (route, request) => {
            if (request.method() === 'GET') {
                await route.fulfill({ json: { events: [{ event: "APPLIED", claim_id: testableClaim.id, applied_commit: "commit456" }] } });
            } else if (request.method() === 'POST') {
                await route.fulfill({ json: { status: "success" } });
            }
        });

        // Click apply
        await applyBtn.click();

        // Banner should change to APPLIED
        await expect(page.locator('.applied-banner.is-applied')).toBeVisible({ timeout: 10000 });
        await expect(page.locator('.applied-banner')).toContainText('APPLIED');
        await expect(page.locator('.applied-banner')).toContainText('commit456');

        // Button should become disabled
        await expect(applyBtn).toBeDisabled();
        await expect(applyBtn).toContainText('Logged as Applied');

        // The list item should have a ✓
        await expect(page.locator(`.claim-item:has(span.claim-id:text-is("${testableClaim.id}"))`).locator('text=✓')).toBeVisible();
    });

});
