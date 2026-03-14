import { test, expect } from '@playwright/test';
import fs from 'fs';
import path from 'path';

// Define explicit screenshot directory inside the lab scratch space
const screenshotDir = path.join(process.cwd(), '.scratch', 'screenshots', 'matrix');
if (!fs.existsSync(screenshotDir)) {
    fs.mkdirSync(screenshotDir, { recursive: true });
}

test.describe('Exhaustive Evidence Verification Matrix Coverage', () => {

    test('State 1: True no-evidence state', async ({ page }) => {
        await page.route('/api/lab/health', async route => {
            await route.fulfill({
                status: 200,
                contentType: 'application/json',
                body: JSON.stringify({
                    status: "online",
                    audit_status: "NOT_AUDITED",
                    audit_banner_kind: "not_audited",
                    current_build: { git_commit: "mock_commit", display: "mock_commit" },
                    active_profile: "linux_x86",
                    is_canonical_audit_status: false,
                    is_current_build_audited: false,
                    summary_pass: 0,
                    summary_fail: 0,
                    contract_id: null,
                    canonicalPromotion: {
                        canonical_promotion_status: "NOT_READY",
                        required_claims_status: []
                    },
                    production_safety: {
                        can_verify_all: true
                    }
                })
            });
        });

        await page.route('/api/lab/claim_results', async route => {
            await route.fulfill({
                status: 200,
                contentType: 'application/json',
                body: JSON.stringify({ results: {} }) 
            });
        });

        await page.route('/data/manifest.json', async route => {
            await route.fulfill({ status: 200, body: '[]' });
        });
        await page.route('/api/lab/history', async route => {
            await route.fulfill({ status: 200, body: '[]' });
        });

        // Claims Surface
        await page.goto('/#claims');
        const claimItem = page.locator('.claim-item').first();
        await expect(claimItem).toBeVisible({ timeout: 10000 });
        const claimStatus = claimItem.locator('.claim-status').first();
        await expect(claimStatus).toHaveText(/UNTESTED/);
        
        await page.waitForTimeout(500); // Give fonts & badges a moment to settle
        await page.screenshot({ path: path.join(screenshotDir, 'matrix_s1_claims_no_evidence.png'), fullPage: true });

        // Validation Core Surface
        await page.goto('/#validation');
        await page.waitForTimeout(1000);
        fs.writeFileSync(path.join(process.cwd(), '.scratch', 'dom_dump.html'), await page.evaluate(() => document.body.innerHTML));
        const vBanner = page.locator('.system-health-bar').first();
        await expect(vBanner).toContainText('NOT_AUDITED');
        // Assert no undefined artifacts
        await expect(page.locator('body')).not.toContainText('undefined PASS');
        await expect(page.locator('body')).not.toContainText('undefined FAIL');
        await page.waitForTimeout(500);
        await page.screenshot({ path: path.join(screenshotDir, 'matrix_s1_validation_no_evidence.png'), fullPage: true });
    });

    test('State 2: Historical experimental-only evidence', async ({ page }) => {
        await page.route('/api/lab/health', async route => {
            await route.fulfill({
                status: 200,
                contentType: 'application/json',
                body: JSON.stringify({
                    status: "online",
                    audit_status: "NOT_AUDITED",
                    audit_banner_kind: "not_audited",
                    current_build: { git_commit: "mock_commit", display: "mock_commit" },
                    active_profile: "linux_x86",
                    is_canonical_audit_status: false,
                    is_current_build_audited: false,
                    summary_pass: 0,
                    summary_fail: 0,
                    contract_id: null,
                    canonicalPromotion: {
                        canonical_promotion_status: "NOT_READY",
                        required_claims_status: []
                    },
                    production_safety: { can_verify_all: true }
                })
            });
        });

        await page.route('/api/lab/claim_results', async route => {
            await route.fulfill({
                status: 200,
                contentType: 'application/json',
                body: JSON.stringify({ 
                    results: {
                        "CL-CORE-001": {
                            resolved_claim_status: "SUPPORTED",
                            verdict: "SUPPORTED",
                            evidence_provenance: "EXPERIMENTAL_RUN",
                            manifest_id: "mock_manifest",
                            scenario_id: "preset-core-001",
                            is_stale: false,
                            is_audit_grade: false
                        }
                    } 
                }) 
            });
        });

        await page.route('/api/lab/history', async route => { await route.fulfill({ status: 200, body: '[]' }); });
        await page.route('/data/manifest.json', async route => { await route.fulfill({ status: 200, body: '[]' }); });

        // Claims Surface
        await page.goto('/#claims');
        const claimItem = page.locator('.claim-item').filter({ hasText: 'CL-CORE-001' });
        await expect(claimItem.locator('.claim-status').first()).toHaveText(/SUPPORTED/);
        await expect(claimItem).toContainText('EXPERIMENTAL DRAFT');
        
        await page.waitForTimeout(500);
        await page.screenshot({ path: path.join(screenshotDir, 'matrix_s2_claims_experimental.png'), fullPage: true });

        // Validation Core Surface
        await page.goto('/#validation');
        const vBanner = page.locator('.system-health-bar').first();
        await expect(vBanner).toContainText('NOT_AUDITED');
        await page.waitForTimeout(500);
        await page.screenshot({ path: path.join(screenshotDir, 'matrix_s2_validation_experimental.png'), fullPage: true });
    });

    test('State 3 & 5: Historical canonical evidence + stale build AND Post-Verify-All flow', async ({ page }) => {
        // We will execute State 3, take a layout screenshot, then click Verify All and take the State 5 screenshot.
        await page.route('/api/lab/health', async route => {
            await route.fulfill({
                status: 200,
                contentType: 'application/json',
                body: JSON.stringify({
                    status: "online",
                    audit_status: "CANONICAL_AUDITED_ARTIFACT_COMMIT_NEWER",
                    audit_banner_kind: "stale_for_current_build",
                    current_build: { git_commit: "mock_newer_commit", display: "mock_newer_commit" },
                    contract_id: "01-core-lineum.md",
                    contract_timestamp: "2026-03-01T12:00:00Z",
                    contract_commit: "old_commit",
                    active_audit: { git_commit: "old_commit" },
                    equation_fingerprint: "hash123",
                    audit_relevant_code_fingerprint: "hash456",
                    summary_pass: 34,
                    summary_fail: 0,
                    active_profile: "linux_x86",
                    is_canonical_audit_status: true,
                    is_current_build_audited: false,
                    canonical_promotion: {
                        canonical_promotion_status: "EVALUATING",
                        required_claims_status: [
                            { id: "CL-CORE-001", is_ready: false }
                        ]
                    },
                    production_safety: { can_verify_all: true }
                })
            });
        });

        await page.route('/api/lab/claim_results', async route => {
            await route.fulfill({
                status: 200,
                contentType: 'application/json',
                body: JSON.stringify({ 
                    results: {
                        "CL-CORE-001": {
                            resolved_claim_status: "SUPPORTED",
                            verdict: "SUPPORTED",
                            evidence_provenance: "STALE_EVIDENCE",
                            manifest_id: "mock_manifest",
                            scenario_id: "preset-core-001",
                            is_stale: true,
                            is_audit_grade: true
                        }
                    } 
                }) 
            });
        });

        await page.route('/api/lab/verify_all', async route => {
            await route.fulfill({
                status: 200,
                contentType: 'application/json',
                body: JSON.stringify({
                    summary: { duration_ms: 100, is_canonical: false },
                    results: {
                        "CL-CORE-001": {
                            resolved_claim_status: "SUPPORTED",
                            evidence_provenance: "STALE_EVIDENCE",
                            manifest_id: "mock_manifest",
                            scenario_id: "preset-core-001",
                            is_audit_grade: true
                        }
                    }
                })
            });
        });

        await page.route('/api/lab/history', async route => { await route.fulfill({ status: 200, body: '[]' }); });
        await page.route('/data/manifest.json', async route => { await route.fulfill({ status: 200, body: '[]' }); });

        // -------------------------------------------------------------
        // State 3: Pre-Verify (Stale Canonical)
        // -------------------------------------------------------------
        await page.goto('/#claims');
        const claimItem = page.locator('.claim-item').filter({ hasText: 'CL-CORE-001' });
        await expect(claimItem.locator('.claim-status').first()).toHaveText(/SUPPORTED/);
        await expect(claimItem).toContainText('STALE EVIDENCE');
        
        await page.waitForTimeout(500);
        await page.screenshot({ path: path.join(screenshotDir, 'matrix_s3_claims_stale_canonical.png'), fullPage: true });

        await page.goto('/#validation');
        const vBanner = page.locator('.system-health-bar').first();
        await expect(vBanner).toContainText('CANONICAL_AUDITED_ARTIFACT_COMMIT_NEWER');
        // Assert mock fixture coherence
        await expect(page.locator('.scorecard-root')).not.toContainText('undefined PASS');
        await expect(page.locator('.scorecard-root')).not.toContainText('undefined FAIL');
        
        await page.waitForTimeout(500);
        await page.screenshot({ path: path.join(screenshotDir, 'matrix_s3_validation_stale_canonical.png'), fullPage: true });

        // -------------------------------------------------------------
        // State 5: Post-Verify-All
        // -------------------------------------------------------------
        await page.goto('/#claims');
        const verifyAllBtn = page.locator('.verify-all-btn');
        await expect(verifyAllBtn).toBeVisible();
        await verifyAllBtn.click();
        
        // Let it finish processing logic
        await expect(verifyAllBtn).not.toBeDisabled({ timeout: 5000 });
        
        // Assert it does NOT collapse to UNTESTED
        await expect(claimItem.locator('.claim-status').first()).toHaveText(/SUPPORTED/);
        // Assert it preserves STALE EVIDENCE linkage instead of collapsing to EXPERIMENTAL DRAFT
        await expect(claimItem).toContainText('STALE EVIDENCE');
        await expect(claimItem).not.toContainText('EXPERIMENTAL DRAFT');
        await expect(claimItem.locator('.claim-status').first()).not.toHaveText(/UNTESTED/);

        await page.waitForTimeout(500);
        await page.screenshot({ path: path.join(screenshotDir, 'matrix_s5_claims_post_verify.png'), fullPage: true });
    });

    test('State 4: Clean canonical current-build state', async ({ page }) => {
        await page.route('/api/lab/health', async route => {
            await route.fulfill({
                status: 200,
                contentType: 'application/json',
                body: JSON.stringify({
                    status: "online",
                    audit_status: "CANONICAL_AUDITED_ARTIFACT_COMMIT_SAME",
                    audit_banner_kind: "clean",
                    current_build: { git_commit: "mock_commit", display: "mock_commit" },
                    contract_id: "01-core-lineum.md",
                    contract_timestamp: "2026-03-01T12:00:00Z",
                    contract_commit: "mock_commit",
                    active_audit: { git_commit: "mock_commit" },
                    equation_fingerprint: "hash123",
                    audit_relevant_code_fingerprint: "hash456",
                    summary_pass: 34,
                    summary_fail: 0,
                    active_profile: "linux_x86",
                    is_canonical_audit_status: true,
                    is_current_build_audited: true,
                    canonical_promotion: {
                        canonical_promotion_status: "READY_FOR_CANONICAL_PROMOTION",
                        required_claims_status: [
                            { id: "CL-CORE-001", is_ready: true }
                        ],
                        missing_requirements: []
                    },
                    production_safety: { can_verify_all: true }
                })
            });
        });

        await page.route('/api/lab/claim_results', async route => {
            await route.fulfill({
                status: 200,
                contentType: 'application/json',
                body: JSON.stringify({ 
                    results: {
                        "CL-CORE-001": {
                            resolved_claim_status: "SUPPORTED",
                            verdict: "SUPPORTED",
                            evidence_provenance: "CANONICAL_SUITE",
                            manifest_id: "mock_manifest",
                            scenario_id: "preset-core-001",
                            is_stale: false,
                            is_audit_grade: true
                        }
                    } 
                }) 
            });
        });

        await page.route('/api/lab/history', async route => { await route.fulfill({ status: 200, body: '[]' }); });
        await page.route('/data/manifest.json', async route => { await route.fulfill({ status: 200, body: '[]' }); });

        // Claims Surface
        await page.goto('/#claims');
        const claimItem = page.locator('.claim-item').filter({ hasText: 'CL-CORE-001' });
        await expect(claimItem.locator('.claim-status').first()).toHaveText(/SUPPORTED/);
        // Canonical is implicit; it should not have Stale or Experimental markers
        await expect(claimItem).not.toContainText('STALE EVIDENCE');
        await expect(claimItem).not.toContainText('EXPERIMENTAL DRAFT');
        
        const promotionPanel = page.locator('.promotion-block');
        await expect(promotionPanel).toContainText('READY FOR CANONICAL PROMOTION');
        
        await page.waitForTimeout(500);
        await page.screenshot({ path: path.join(screenshotDir, 'matrix_s4_claims_clean_canonical.png'), fullPage: true });

        // Validation Core Surface
        await page.goto('/#validation');
        const vBanner = page.locator('.system-health-bar').first();
        await page.waitForTimeout(1000);
        fs.writeFileSync(path.join(process.cwd(), '.scratch', 'dom_dump_s4.html'), await page.evaluate(() => document.body.innerHTML));
        await expect(vBanner).toContainText('CANONICAL_AUDITED_ARTIFACT_COMMIT_SAME');
        await expect(page.locator('.dashboard').first()).toBeVisible(); 
        
        await expect(page.locator('.scorecard-root')).not.toContainText('undefined PASS');
        await expect(page.locator('.scorecard-root')).not.toContainText('undefined FAIL');
        
        await page.waitForTimeout(500);
        await page.screenshot({ path: path.join(screenshotDir, 'matrix_s4_validation_clean_canonical.png'), fullPage: true });
    });
});
