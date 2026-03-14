import { test, expect } from '@playwright/test';

test.describe('Whitepaper Claims State & Provenance Regressions', () => {
    test.beforeEach(async ({ page }) => {
        // Intercept health check to simulate CANONICAL_AUDITED_ARTIFACT_COMMIT_NEWER (stale canonical lineage)
        // Ensure canonical promotion panel natively declares 1/3 claims ready.
        await page.route('/api/lab/health', async route => {
            await route.fulfill({
                status: 200,
                contentType: 'application/json',
                body: JSON.stringify({
                    status: "online",
                    audit_status: "CANONICAL_AUDITED_ARTIFACT_COMMIT_NEWER",
                    audit_banner_kind: "stale_for_current_build",
                    contract_id: "mock_contract_id",
                    current_build: "mock_newer_commit",
                    production_safety: {
                        is_production: false,
                        can_generate_audit: true,
                        can_verify_all: true
                    },
                    canonical_promotion: {
                        canonical_promotion_status: "EVALUATING",
                        required_claims_status: [
                            { id: "CL-CORE-001", is_ready: true },
                            { id: "CL-CORE-002", is_ready: false },
                            { id: "CL-CORE-003", is_ready: false }
                        ]
                    }
                })
            });
        });

        // Intercept initial claim results. CL-CORE-001 is stale but mathematically supported.
        await page.route('/api/lab/claim_results', async (route, request) => {
            // We can return the same stale configuration payload because verify_all now calls refreshStatuses.
            // Even if the backend upgraded it to EXPERIMENTAL_RUN because it matched local git, Svelte mustn't say UNTESTED.
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
                    summary: { duration_ms: 100 },
                    results: {
                        "CL-CORE-001": {
                            resolved_claim_status: "SUPPORTED",
                            manifest_id: "mock_manifest",
                            scenario_id: "preset-core-001",
                            is_audit_grade: true
                        }
                    }
                })
            });
        });

        await page.route('/integration_log', async route => {
            await route.fulfill({ status: 200, body: JSON.stringify({ events: [] }) });
        });

        await page.route('/data/manifest.json', async route => {
            await route.fulfill({ status: 200, body: '[]' });
        });
    });

    test('Verify All Claims must NOT collapse stale historical canonical evidence to plain UNTESTED', async ({ page }) => {
        await page.goto('/#claims');

        // Wait for the claims list to render
        const claimItem = page.locator('.claim-item').filter({ hasText: 'CL-CORE-001' });
        await expect(claimItem).toBeVisible();

        // 1. Assert initial stale state is fully visible and not erased
        const statusBadge = claimItem.locator('.claim-status').first();
        await expect(statusBadge).toHaveText(/SUPPORTED/);
        
        // In the UI it might be formatted inside the name or next to it as (STALE EVIDENCE)
        await expect(claimItem).toContainText('STALE EVIDENCE');

        // 2. Assert Promotion Panel has 1 / 3
        const promotionPanel = page.locator('.collapsible-box').filter({ hasText: 'Wave Core Promotion' });
        await expect(promotionPanel).toBeVisible();
        await expect(promotionPanel).toContainText('1 / 3 required claims');

        // 3. Click Verify All Claims
        const verifyAllBtn = page.locator('.verify-all-btn');
        await expect(verifyAllBtn).toBeVisible();
        await verifyAllBtn.click();

        // Wait for loading to finish (verifyAllClaims sets isVerifyingAll = false)
        await expect(verifyAllBtn).not.toBeDisabled({ timeout: 5000 });

        // 4. Assert that after verify all completes, the claim is STILL SUPPORTED and NOT 'UNTESTED'
        await expect(statusBadge).toHaveText(/SUPPORTED/);
        await expect(statusBadge).not.toHaveText(/UNTESTED/);

        // 5. Assert the Promotion Panel did NOT regress to 0 / 3
        await expect(promotionPanel).toContainText('1 / 3 required claims');
        await expect(promotionPanel).not.toContainText('0 / 3 required claims');
    });

    test('Filters toggling, filtering, and clear functionality', async ({ page }) => {
        await page.goto('/#claims');

        const claimItem = page.locator('.claim-item').first();
        await expect(claimItem).toBeVisible();

        // Ensure "Clear Filters" is initially hidden
        const clearFiltersBtn = page.locator('.clear-filters-btn');
        await expect(clearFiltersBtn).not.toBeVisible();

        // Expand filters
        const filtersToggle = page.locator('[data-testid="filters-toggle"]');
        await expect(filtersToggle).toBeVisible();
        await filtersToggle.click();

        // Type in search to activate filters
        const searchInput = page.locator('.search-input');
        await expect(searchInput).toBeVisible();
        await searchInput.fill('CL-CORE');

        // Verify "Clear Filters" appears
        await expect(clearFiltersBtn).toBeVisible();

        // Clear filters
        await clearFiltersBtn.click();
        await expect(clearFiltersBtn).not.toBeVisible();
        await expect(searchInput).toHaveValue('');
    });
});
