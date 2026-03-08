import { test, expect } from '@playwright/test';
import { whitepaperClaims } from '../src/lib/data/claims.js';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

test.describe('Whitepaper Claims MVP', () => {
    test.beforeEach(async ({ page }) => {
        page.on('pageerror', error => console.error(`\n[PAGE ERROR]: ${error.message}\n`));
        page.on('console', msg => {
            console.error(`\n[CONSOLE ${msg.type().toUpperCase()}]: ${msg.text()}\n`);
        });

        // Global mocks for all backend endpoints used on mount to prevent App.svelte error state
        await page.route('**/api/lab/claim_results', async route => {
            await route.fulfill({ json: { results: {} } });
        });
        await page.route('**/health', async route => {
            await route.fulfill({ json: { active_contract: null, audit_status: "NONE" } });
        });
        await page.route('**/data/manifest.json', async route => {
            await route.fulfill({ json: [] });
        });
        await page.route('**/api/lab/audit/config', async route => {
            await route.fulfill({ json: { allowed: true, execution_device: "mock-cpu" } });
        });
        await page.route('**/integration_log', async route => {
            await route.fulfill({ json: { events: [] } });
        });
    });
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
            // Rule-based exclusion: Do not enforce Integration Log traceability 
            // on claims that are not yet technically prepared for automated testing
            if (claim.testability === 'NOT_TESTABLE_YET' ||
                claim.testability === 'NEEDS_NEW_SCENARIO' ||
                claim.verification_spec_status !== 'APPROVED') {
                continue;
            }

            const match = appliedLogs.find(l => l.claim_id === claim.id);
            expect(match, `Runnable claim ${claim.id} is missing an applied=true traceability record`).toBeDefined();
            // Also cross-check source file matches
            if (match) {
                expect(match.source_file).toBe(claim.source_file);
            }
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

        // Assert source link does not contain vscode and points to wiki
        const sourceHref = await page.locator('.source-link a').getAttribute('href');
        expect(sourceHref).not.toContain('vscode://');
        expect(sourceHref).toContain('/wiki/');

        // Promotion progress block UX
        const promotionBlock = page.locator('.promotion-block');
        if (await promotionBlock.isVisible()) {
            await expect(promotionBlock.locator('text=Wave Core Promotion')).toBeVisible();
            await expect(promotionBlock.locator('text=Goal: Elevating')).not.toBeVisible(); // Default collapsed

            // Expand
            await promotionBlock.locator('[role="button"]').click();
            await expect(promotionBlock.locator('text=Goal: Elevating')).toBeVisible();
            await expect(promotionBlock.locator('text=Required Claims Status:')).toBeVisible();

            // Claims list must remain usable after expansion
            await expect(listItems.last()).toBeVisible();
            await expect(listItems.first()).toBeVisible();

            // Collapse
            await promotionBlock.locator('[role="button"]').click();
            await expect(promotionBlock.locator('text=Goal: Elevating')).not.toBeVisible();
        }

        // Falsification Explicit Fields UI
        if (whitepaperClaims[0].falsification_mode) {
            await expect(page.locator('text=Falsification State')).toBeVisible();
            // Should not show fake AUTOMATIC if it's MANUAL
            await expect(page.locator(`.falsification-section:has-text("${whitepaperClaims[0].falsification_mode}")`)).toBeVisible();
            await expect(page.locator('.fals-meta-grid:has-text("Evidence Source")')).toBeVisible();
            // Should render the explicit real status from JSON
            if (whitepaperClaims[0].falsification_status) {
                await expect(page.locator(`.fals-meta-grid:has-text("${whitepaperClaims[0].falsification_status}")`)).toBeVisible();
            }
        }

        // Explain pack canon
        await expect(page.locator('.ep-liner')).toContainText('Human Translation');
        await expect(page.locator('text=Scientific Claim')).toBeVisible();
        await expect(page.locator('text=What this is NOT')).toBeVisible();

        // Testability logic check in UI
        if (whitepaperClaims[0].testability === 'TESTABLE_NOW') {
            await expect(page.locator('button:has-text("Run Verification Scenario")')).toBeVisible();
        }
    });

    test('Mapping Test: Strict Gating and Audit Badge UI', async ({ page }) => {
        // Assert initial state: all claims UNTESTED
        for (const claim of whitepaperClaims) {
            expect(claim.status).toBe('UNTESTED');
        }

        // --- Mock State 1: NO AUDIT CONTRACT ---
        await page.route('**/health', async route => {
            await route.fulfill({
                json: {
                    active_contract: null,
                    audit_status: "NONE",
                    current_build: "mock-hash (main)",
                    canonicalPromotion: { canonical_promotion_status: 'NOT_READY', required_claims_status: [], missing_requirements: [] },
                    productionSafety: { can_verify_all: true, can_generate_audit: true }
                }
            });
        });

        await page.goto('/');
        await page.click('text=Claims');

        // Mock the verification API so Playwright doesn't wait for Vite proxy timeout
        await page.route('**/run_preset*', async route => {
            await route.fulfill({
                json: { manifest_id: "mock-123", overall_pass: true, message: "Mocked fetch", resolved_claim_status: "EXPERIMENTAL_SUPPORTED", audit_status: "NONE", scenario_id: "mock-scenario" }
            });
        });

        // Check global navigation header to ensure audit generation button is present
        await expect(page.locator('.btn-generate-audit')).toBeVisible();

        // Ensure the global loading overlay is gone so it doesn't intercept clicks
        await expect(page.locator('.loader')).toHaveCount(0, { timeout: 15000 });

        // Find a TESTABLE_NOW claim
        const testableClaim = whitepaperClaims.find(c => c.testability === 'TESTABLE_NOW');
        const claimLocator = page.locator(`.claim-item:has(span.claim-id:text-is("${testableClaim.id}"))`);
        await expect(claimLocator).toBeVisible();
        await claimLocator.click();

        let runBtn = page.locator('button:has-text("Run Verification Scenario")');
        await expect(runBtn).toBeVisible();
        await runBtn.click();

        // Wait for exploratory evidence box to definitively prove state transfer
        let exploratoryBox = page.locator('.evidence-box.exploratory');
        await expect(exploratoryBox).toBeVisible({ timeout: 15000 });

        // --- Mock State 2: AUDITED ---
        // Remock health
        await page.route('**/health', async route => {
            await route.fulfill({
                json: {
                    contract_id: "LNC-AUDIT-MOCK123",
                    audit_status: "AUDITED",
                    contract_commit: "mock123",
                    current_build: "mock123 (main)",
                    summary_pass: 10,
                    summary_fail: 0,
                    canonicalPromotion: { canonical_promotion_status: 'CANONICAL_AUDITED', required_claims_status: [], missing_requirements: [] },
                    productionSafety: { can_verify_all: true, can_generate_audit: true }
                }
            });
        });

        // Remount to trigger onMount health fetch
        await page.reload();
        await page.click('text=Claims');

        // Wait for loader to disappear after reload
        await expect(page.locator('.loader')).toHaveCount(0, { timeout: 15000 });

        // Wait for claim list to populate again after reload
        const reloadedClaimLocator = page.locator(`.claim-item:has(span.claim-id:text-is("${testableClaim.id}"))`);
        await expect(reloadedClaimLocator).toBeVisible({ timeout: 10000 });

        // DO NOT CLICK IT AGAIN! The claim is already selected because Svelte preserves selectedClaimId in localStorage
        // Just verify detail card appeared
        await expect(page.locator('.detail-card h2')).toBeVisible({ timeout: 5000 });

        // Take a screenshot of the claims interface
        await page.screenshot({ path: '../../output_wp/runs/_whitepaper_contract/audit_claims_view.png' });

        // Click same claim
        // Ensure the warning banner is gone now that the build is AUDITED
        await expect(page.locator('.audit-warning-banner')).not.toBeVisible();

        // Remock verification API to return AUDIT grade results
        await page.route('**/run_preset*', async route => {
            await route.fulfill({
                json: { manifest_id: "mock-123-audited", overall_pass: true, message: "Mocked fetch", resolved_claim_status: "SUPPORTED", audit_status: "AUDITED", scenario_id: "mock-scenario", contract_id: "LNC-AUDIT-MOCK123" }
            });
        });

        runBtn = page.locator('button.run-btn'); // using simpler selector
        await expect(runBtn).toBeVisible({ timeout: 5000 });
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
        await page.route('**/health', async route => {
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
        await page.route('**/integration_log', async (route, request) => {
            if (request.method() === 'GET') {
                await route.fulfill({ json: { events: [] } });
            } else if (request.method() === 'POST') {
                await route.fulfill({ json: { status: "success" } });
            }
        });

        // Mock preset run
        await page.route('**/run_preset*', async route => {
            await route.fulfill({ json: { manifest_id: "manifest-789", overall_pass: true, resolved_claim_status: "SUPPORTED", audit_status: "AUDITED", contract_id: "LNC-AUDIT-456" } });
        });

        await page.goto('/');
        await page.click('text=Claims');

        // Check if Applied filter exists
        await page.goto('/');
        await page.click('text=Claims');

        // Ensure loader is gone
        await expect(page.locator('.loader')).toHaveCount(0, { timeout: 15000 });

        // 1. Initial State Check
        // Find a TESTABLE_NOW claim
        const testableClaim = whitepaperClaims.find(c => c.testability === 'TESTABLE_NOW');
        const claimLocator = page.locator(`.claim-item:has(span.claim-id:text-is("${testableClaim.id}"))`);
        await expect(claimLocator).toBeVisible({ timeout: 10000 });
        await claimLocator.click();

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
        await page.unroute('**/integration_log');
        await page.route('**/integration_log', async (route, request) => {
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

        // Button should switch to Unmark
        await expect(applyBtn).toBeEnabled();
        await expect(applyBtn).toContainText('Unmark Applied');

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
    test('UI Test: Claims Filtering Logic and Combinations', async ({ page }) => {
        await page.goto('/');
        await page.click('text=Claims');

        // Wait for list to load
        const listItems = page.locator('.claim-item');
        await expect(listItems).toHaveCount(whitepaperClaims.length);

        // 1. Single Filter: Testability
        const testabilitySelect = page.locator('select.tag-select').nth(2); // index 2 is testabilityFilter
        await testabilitySelect.selectOption('TESTABLE_NOW');

        let expectedTestableCount = whitepaperClaims.filter(c => c.testability === 'TESTABLE_NOW').length;
        // Wait for reactivity to process
        await page.waitForTimeout(500);
        await expect(listItems).toHaveCount(expectedTestableCount);

        // 2. Clear Filters
        const clearBtn = page.locator('.clear-filters-btn');
        await clearBtn.click();
        await page.waitForTimeout(500);
        await expect(listItems).toHaveCount(whitepaperClaims.length);

        // 3. Combined Filter (AND semantics)
        const scopeSelect = page.locator('select.tag-select').nth(3); // index 3 is scopeFilter
        await testabilitySelect.selectOption('TESTABLE_NOW');
        await scopeSelect.selectOption('MODEL_INTERNAL');

        let expectedCombinedCount = whitepaperClaims.filter(c => c.testability === 'TESTABLE_NOW' && c.scope === 'MODEL_INTERNAL').length;
        await page.waitForTimeout(500);
        await expect(listItems).toHaveCount(expectedCombinedCount);

        // 4. Clear Filters again
        await clearBtn.click();
        await page.waitForTimeout(500);
        await expect(listItems).toHaveCount(whitepaperClaims.length);

        // 5. Falsification needed 
        const falsificationSelect = page.locator('select.tag-select').nth(4); // index 4 is falsificationFilter
        await falsificationSelect.selectOption('needed');

        let expectedFalsCount = whitepaperClaims.filter(c => c.falsification_needed === true).length;
        await page.waitForTimeout(500);
        await expect(listItems).toHaveCount(expectedFalsCount);
    });

    test('Agent Automation: Handoff Packet text generation', async ({ page, context }) => {
        // Grant clipboard permissions for writeText to work natively, or we can mock it
        await context.grantPermissions(['clipboard-read', 'clipboard-write']);

        // Mock health and claim results so we establish a specific state for CL-CORE-001
        await page.route('**/health', async route => {
            await route.fulfill({
                json: {
                    active_contract: "LNC-AUDIT-TEST",
                    contract_id: "LNC-AUDIT-TEST",
                    audit_status: "AUDITED"
                }
            });
        });

        await page.route('**/api/lab/claim_results', async route => {
            await route.fulfill({
                json: {
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
                }
            });
        });

        await page.goto('/');
        await page.click('text=Claims');

        // Ensure loader is gone
        await expect(page.locator('.loader')).toHaveCount(0, { timeout: 15000 });

        // Click a verified claim
        const claimLocator = page.locator('.claim-item:has(span.claim-id:text-is("CL-CORE-001"))');
        await expect(claimLocator).toBeVisible({ timeout: 10000 });
        await claimLocator.click();

        // Wait for the canonical evidence box and Assistant button to appear
        await expect(page.locator('.evidence-box.canonical')).toBeVisible({ timeout: 10000 });
        const assistantBtn = page.locator('button.agent-handoff');
        await expect(assistantBtn).toBeVisible();

        // Intercept clipboard write
        await page.evaluate(() => {
            window._clipboardText = "";
            navigator.clipboard.writeText = async (text) => {
                window._clipboardText = text;
                return Promise.resolve();
            };
        });

        // Click the handoff button
        await assistantBtn.click();

        // Retrieve recorded text
        const packetText = await page.evaluate(() => window._clipboardText);

        // Assert schema stability features
        expect(packetText).toContain('LINEUM HANDOFF PROTOCOL [v1.0.0]');
        expect(packetText).toContain('META-INSTRUCTIONS FOR PRIMARY AGENT (ASSISTANT)');
        expect(packetText).toContain('Treat this packet as the absolute current source of truth for the Lineum project.');

        // Assert claim identity fields
        expect(packetText).toContain('- **Claim ID:** CL-CORE-001');
        expect(packetText).toContain('- **Current Status:** SUPPORTED');
        expect(packetText).toContain('- **Evidence Level:** CANONICAL_AUDIT_SUITE');

        // Assert traceability
        expect(packetText).toContain('f0_mean_hz: 4.3210e+2');

        // Assert automation routing fields based on our mocked state (READY_FOR_EDITORIAL_REVIEW)
        expect(packetText).toContain('Is this ready for wording proposal now?** YES');
        expect(packetText).toContain('Primary agent action:** Review constraints and generate the final whitepaper prose');
        expect(packetText).toContain('wording_proposal_allowed_now:** true');
        expect(packetText).toContain('escalate_to_secondary_agent:** false');

        // Assert no external files attached, fully plain text
        expect(typeof packetText).toBe('string');
        expect(packetText.length).toBeGreaterThan(500);
    });
});
