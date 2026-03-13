import { test, expect } from '@playwright/test';

test.describe('Capture Final Screenshots', () => {

    test.beforeEach(async ({ page }) => {
        await page.route('**/data/manifest.json', async route => {
            await route.fulfill({ json: [] });
        });
    });

    test('Capture Clean CANONICAL_AUDITED', async ({ page }) => {
        await page.route('**/api/lab/health', async route => {
            const json = {
                status: 'ok',
                audit_status: 'CANONICAL_AUDITED',
                active_contract_id: 'lineum-core-1.1.4-core',
                contract_id: 'lineum-core-1.1.4-core',
                contract_timestamp: new Date().toISOString(),
                contract_commit: 'b5ede929b3e17d62e1e1850f24b7abe2fe661d50',
                git_commit: 'b5ede929b3e17d62e1e1850f24b7abe2fe661d50',
                equation_fingerprint: '7197faf5a92a141a4847314485bee819ae9fdecdf08eead313ffdd3da6fe9f5',
                audit_relevant_code_fingerprint: '88b80a9d7dadb9be6c20518e20cb164ca57a28e0af73c6fc36eb42d5c70fc500',
                summary_pass: 3,
                summary_fail: 0,
                active_profile: 'wave_core',
                is_canonical_audit_status: true,
                is_current_build_audited: true,
                is_audit_in_progress: false,
                audit_banner_kind: 'none'
            };
            await route.fulfill({ json });
        });

        await page.goto('http://127.0.0.1:5174/#validation');
        await page.waitForSelector('.scorecard-root');
        
        // Wait a small moment for animations
        await page.waitForTimeout(1000);
        
        await page.screenshot({ path: 'C:/Users/Tomáš/.gemini/antigravity/brain/bfdbbf37-fd4f-478b-aca7-f8cedcd1cff0/validation_core_clean_canonical.png' });
    });

    test('Capture STALE_FOR_CURRENT_BUILD', async ({ page }) => {
        await page.route('**/api/lab/health', async route => {
            const json = {
                status: 'ok',
                audit_status: 'CANONICAL_AUDITED_ARTIFACT_COMMIT_NEWER',
                active_contract_id: 'lineum-core-1.1.4-core',
                contract_id: 'lineum-core-1.1.4-core',
                contract_timestamp: new Date().toISOString(),
                contract_commit: 'b5ede929b3e17d62e1e1850f24b7abe2fe661d50',
                git_commit: '5b2d8940b7cedc3ba30e2d4b079beda5614824fa',
                equation_fingerprint: '7197faf5a92a141a4847314485bee819ae9fdecdf08eead313ffdd3da6fe9f5',
                audit_relevant_code_fingerprint: '88b80a9d7dadb9be6c20518e20cb164ca57a28e0af73c6fc36eb42d5c70fc500',
                summary_pass: 3,
                summary_fail: 0,
                active_profile: 'wave_core',
                is_canonical_audit_status: true,
                is_current_build_audited: false,
                is_audit_in_progress: false,
                audit_banner_kind: 'stale_for_current_build'
            };
            await route.fulfill({ json });
        });

        await page.goto('http://127.0.0.1:5174/#validation');
        await page.waitForSelector('.scorecard-root');
        
        // Wait a small moment for animations
        await page.waitForTimeout(1000);
        
        await page.screenshot({ path: 'C:/Users/Tomáš/.gemini/antigravity/brain/bfdbbf37-fd4f-478b-aca7-f8cedcd1cff0/validation_core_stale_canonical.png' });
    });

});
