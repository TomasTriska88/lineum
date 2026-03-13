// @ts-check
import { test, expect } from '@playwright/test';

test.describe('Validation Core Semantics: Consistent Provenance UI', () => {

    test.beforeEach(async ({ page }) => {
        await page.route('**/data/manifest.json', async route => {
            await route.fulfill({ json: [] });
        });
    });

    test('Clean CANONICAL_AUDITED status prevents experimental warnings and shows Green Check', async ({ page }) => {
        // Mock the /health endpoint to return a perfectly clean CANONICAL_AUDITED state
        await page.route('**/api/lab/health', async route => {
            const json = {
                status: 'ok',
                audit_status: 'CANONICAL_AUDITED',
                active_contract_id: 'con-1234',
                contract_id: 'con-1234',
                contract_timestamp: new Date().toISOString(),
                contract_commit: '1234567',
                git_commit: '1234567',
                equation_fingerprint: 'eq-hash',
                audit_relevant_code_fingerprint: 'code-hash',
                summary_pass: 10,
                summary_fail: 0,
                active_profile: 'default',
                is_canonical_audit_status: true,
                is_current_build_audited: true,
                is_audit_in_progress: false,
                audit_banner_kind: 'none'
            };
            await route.fulfill({ json });
        });

        // Navigate to the lab root (Validation Core mode by default, or click it)
        await page.goto('http://127.0.0.1:5174/#validation');
        
        // Wait for validation root to mount...
        await page.waitForSelector('.scorecard-root');

        // It should display AUDIT CONTRACT: CANONICAL_AUDITED
        const badgeRow = page.locator('.scorecard-root .badge-row');
        await expect(badgeRow).toContainText('CANONICAL_AUDITED');

        // It should display the GREEN checkmark (not the red X or warning)
        await expect(badgeRow).toContainText('✅');

        // Crucially, it must NOT render the red warning box about experimental claims.
        // We ensure neither the yellow nor red warning box exists for a clean canonical state.
        const warningBox = page.locator('.scorecard-root .warning-box');
        await expect(warningBox).toHaveCount(0);
    });

    test('STALE_FOR_CURRENT_BUILD status shows Warning icon and Stale messaging, but separates the truths', async ({ page }) => {
        // Mock a state where canonical audit exists but build is newer (STALE)
        await page.route('**/api/lab/health', async route => {
            const json = {
                status: 'ok',
                audit_status: 'CANONICAL_AUDITED_ARTIFACT_COMMIT_NEWER',
                active_contract_id: 'con-1234',
                contract_id: 'con-1234',
                contract_timestamp: new Date().toISOString(),
                contract_commit: 'old-commit',
                git_commit: 'new-commit',
                is_canonical_audit_status: true,
                is_current_build_audited: false,
                is_audit_in_progress: false,
                audit_banner_kind: 'stale_for_current_build'
            };
            await route.fulfill({ json });
        });

        await page.goto('http://127.0.0.1:5174/#validation');
        await page.waitForSelector('.scorecard-root');

        // It should display AUDIT CONTRACT: CANONICAL_AUDITED_ARTIFACT_COMMIT_NEWER
        const badgeRow = page.locator('.scorecard-root .badge-row');
        await expect(badgeRow).toContainText('CANONICAL_AUDITED_ARTIFACT_COMMIT_NEWER');

        // It should display the WARNING icon because it's stale
        await expect(badgeRow).toContainText('⚠️');

        // It must show the yellow warning box (stale messaging) but not the red "never audited" warning box.
        const warningBox = page.locator('.scorecard-root .warning-box');
        await expect(warningBox).toHaveCount(1);
        await expect(warningBox).not.toHaveClass(/red-warning/);
        await expect(warningBox).toContainText('A canonical baseline pass exists for an older build, but this current build has un-audited changes');
    });

    test('UNAUDITED fallback shows Red X and explicit Experimental warning', async ({ page }) => {
        // Mock a state where no canonical audit exists at all
        await page.route('**/api/lab/health', async route => {
            const json = {
                status: 'ok',
                audit_status: 'UNAUDITED',
                active_contract_id: null,
                contract_id: null,
                contract_timestamp: null,
                contract_commit: null,
                git_commit: '1234567',
                is_canonical_audit_status: false,
                is_current_build_audited: false,
                is_audit_in_progress: false,
                audit_banner_kind: 'not_audited'
            };
            await route.fulfill({ json });
        });

        await page.goto('http://127.0.0.1:5174/#validation');
        await page.waitForSelector('.scorecard-root');

        const badgeRow = page.locator('.scorecard-root .badge-row');
        await expect(badgeRow).toContainText('UNAUDITED');

        // It should display the RED X icon because it has never been canonically audited
        await expect(badgeRow).toContainText('❌');

        // It must show the RED warning box explicitly stating it's experimental and not canonically backed
        const warningBox = page.locator('.scorecard-root .warning-box');
        await expect(warningBox).toHaveCount(1);
        await expect(warningBox).toHaveClass(/red-warning/);
        await expect(warningBox).toContainText('A canonical metric-backed audit is not complete');
        await expect(warningBox).toContainText('Claims remain in an experimental state');
    });

});
