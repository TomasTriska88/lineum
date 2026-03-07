import { test, expect } from '@playwright/test';
import { whitepaperClaims } from '../src/lib/data/claims.js';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

test.describe('Whitepaper Claims MVP', () => {

    test('Schema Test: Every claim has required fields and valid enums', () => {
        const validStatuses = ['UNTESTED', 'SUPPORTED', 'CONTRADICTED'];
        const validTestabilities = ['TESTABLE_NOW', 'NEEDS_NEW_SCENARIO', 'NOT_TESTABLE_YET'];
        const validScopes = ['MODEL_INTERNAL', 'ANALOGICAL', 'REAL_WORLD_STRONG'];

        // Must have more than 10 claims (original demo count)
        expect(whitepaperClaims.length).toBeGreaterThan(10);

        for (const claim of whitepaperClaims) {
            // Original fields
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

            // New fields: scope
            expect(claim).toHaveProperty('scope');
            expect(validScopes).toContain(claim.scope);

            // New fields: falsification
            expect(claim).toHaveProperty('falsification_needed');
            expect(typeof claim.falsification_needed).toBe('boolean');

            if (claim.falsification_needed && !claim.falsification_plan) {
                expect(claim.missing_falsification_reason).toBeTruthy();
            }

            // New fields: disclaimers (string or undefined)
            expect(claim).toHaveProperty('disclaimers');

            // New fields: source_section, source_quote
            expect(claim).toHaveProperty('source_section');
            expect(claim).toHaveProperty('source_quote');
        }

        // Tag distribution checks
        const quarkTags = whitepaperClaims.filter(c => c.tags.some(t => ['quark', 'gluon', 'standard-model'].includes(t)));
        expect(quarkTags.length).toBeGreaterThanOrEqual(3);

        const psiTags = whitepaperClaims.filter(c => c.tags.includes('unified-psi-scale'));
        expect(psiTags.length).toBeGreaterThanOrEqual(3);

        const muTags = whitepaperClaims.filter(c => c.tags.some(t => ['mu', 'memory', 'topology'].includes(t)));
        expect(muTags.length).toBeGreaterThanOrEqual(2);

        // New: multi-source distribution — claims come from more than 1 source file
        const uniqueSources = new Set(whitepaperClaims.map(c => c.source_file));
        expect(uniqueSources.size).toBeGreaterThan(1);

        // New: at least 1 claim from each scope
        for (const scope of validScopes) {
            expect(whitepaperClaims.filter(c => c.scope === scope).length).toBeGreaterThanOrEqual(1);
        }
    });

    test('Traceability MVP: Integration Log forensically links claims to whitepapers', () => {
        const logPath = path.resolve(__dirname, '../src/lib/data/whitepaper_integration_log.json');
        const integrationLog = JSON.parse(fs.readFileSync(logPath, 'utf8'));

        // 1. Uniqueness check for claim_id
        const claimIds = integrationLog.map(entry => entry.claim_id);
        const uniqueIds = new Set(claimIds);
        expect(uniqueIds.size, 'Duplicate claim_ids found in integration log').toBe(claimIds.length);

        // 2. Validate all records
        integrationLog.forEach(record => {
            expect(record).toHaveProperty('source_file');
            expect(record.source_file).toBeTruthy();
            expect(record).toHaveProperty('source_section');
            expect(record.source_section).toBeTruthy();
            expect(record).toHaveProperty('claim_id');
            expect(record.claim_id).toBeTruthy();
            expect(typeof record.applied).toBe('boolean');
            expect(record).toHaveProperty('applied_at');
            expect(record).toHaveProperty('rationale');
            expect(record.rationale).toBeTruthy();

            if (record.applied === true) {
                // Must have evidence target
                expect(record.evidence_target, `Applied claim ${record.claim_id} missing evidence_target`).toBeTruthy();
            } else {
                // Must have skipped reason
                expect(record.skipped_reason, `Skipped claim ${record.claim_id} missing skipped_reason`).toBeTruthy();
            }
        });

        // 3. Ensure all curated claims in claims.js have a traceability record with applied=true
        const appliedLogs = integrationLog.filter(l => l.applied === true);

        for (const claim of whitepaperClaims) {
            const match = appliedLogs.find(l => l.claim_id === claim.id);
            expect(match, `Claim ${claim.id} is missing an applied=true traceability record`).toBeDefined();
            // Also cross-check source file matches
            expect(match.source_file).toBe(claim.source_file);
        }

        // Summary log
        console.log(`\n--- TRACEABILITY COVERAGE ---`);
        console.log(`Total Curated Claims in DB: ${whitepaperClaims.length}`);
        console.log(`Integration Log Entries: ${integrationLog.length}`);
        console.log(`Applied YES: ${appliedLogs.length}`);
        console.log(`Applied NO (Skipped): ${integrationLog.filter(l => !l.applied).length}`);
        console.log(`Coverage %: ${((appliedLogs.length / whitepaperClaims.length) * 100).toFixed(1)}%`);
        console.log(`Missing Traceability Records: 0`);
    });

    test('UI Test: Lists renders claims and details view shows source links', async ({ page }) => {
        await page.goto('/');

        // Navigate to Whitepapers mode
        await page.click('text=Claims');

        // Verify Search/Filter elements exist
        await expect(page.locator('input[placeholder="Search claims..."]')).toBeVisible();
        await expect(page.locator('select.tag-select').first()).toBeVisible();

        // Verify the list has exactly the number of claims we defined
        const listItems = page.locator('.claim-item');
        await expect(listItems).toHaveCount(whitepaperClaims.length);

        // Click the first claim
        await listItems.first().click();

        // Verify Detail view shows critical Explain Pack and Source components
        await expect(page.locator('.detail-card h2')).toContainText(whitepaperClaims[0].id);
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
        await expect(page.locator('.applied-banner')).toContainText('Not applied yet');

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
        await expect(page.locator('.applied-banner')).toContainText('Applied');
        await expect(page.locator('.applied-banner')).toContainText('commit456');

        // Button should become disabled
        await expect(applyBtn).toBeDisabled();
        await expect(applyBtn).toContainText('Logged as Applied');

        // The list item should have a ✓
        await expect(page.locator(`.claim-item:has(span.claim-id:text-is("${testableClaim.id}"))`).locator('text=✓')).toBeVisible();
    });

    test('Tooltip System: styled tooltip appears on hover with accessibility', async ({ page }) => {
        await page.goto('/');
        // Wait for initial page load and JS execution
        await page.waitForTimeout(3000);

        // Inject a test element with title attribute into the loaded page
        await page.evaluate(() => {
            const el = document.createElement('div');
            el.id = 'tooltip-test-target';
            el.setAttribute('title', 'Test Tooltip Content');
            el.textContent = 'Hover Me';
            el.style.cssText = 'position:fixed;top:100px;left:100px;padding:20px;background:#333;color:#fff;z-index:99999;';
            document.body.appendChild(el);
        });

        const target = page.locator('#tooltip-test-target');
        await expect(target).toBeVisible();

        // Hover to trigger tooltip
        await target.hover();
        await page.waitForTimeout(500);

        // Styled tooltip div should appear
        const tooltip = page.locator('.lab-tooltip');
        await expect(tooltip).toBeVisible({ timeout: 3000 });
        await expect(tooltip).toHaveAttribute('role', 'tooltip');
        await expect(tooltip).toContainText('Test Tooltip Content');

        // Native title should be suppressed -> data-tooltip + aria-label set
        await expect(target).toHaveAttribute('data-tooltip', 'Test Tooltip Content');
        await expect(target).toHaveAttribute('aria-label', 'Test Tooltip Content');

        // Move mouse away
        await page.mouse.move(0, 0);
        await page.waitForTimeout(500);

        // Tooltip should be removed
        await expect(tooltip).not.toBeVisible();

        // Title should be restored
        await expect(target).toHaveAttribute('title', 'Test Tooltip Content');
    });

});
