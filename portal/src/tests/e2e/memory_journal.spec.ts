import { test, expect } from '@playwright/test';

test.describe('Memory Imprint Journal UI verification', () => {

    test('should list memory imprints and allow topological forgetting', async ({ page }) => {
        page.on('console', msg => console.log('BROWSER LOG:', msg.text()));
        page.on('pageerror', err => console.log('BROWSER ERROR:', err.message));

        // We will mock the API response for robustness instead of hitting live Python physics,
        // since setting up perfect Eq-4 topography inside E2E tests is flaky.

        const mockImprint = {
            status: "success",
            imprints: [
                {
                    imprint_id: "test-hash-12345",
                    ts: Date.now() / 1000,
                    grid: 64,
                    dt: 1.0,
                    seed: 99,
                    delta_mu_path: "C:\\path\\mock.npz",
                    stats: {
                        l1: 15.2,
                        max: 2.1,
                        ratio_tau: 0.05
                    },
                    affect_v0: {
                        arousal: 1000.5,
                        certainty: 0.95,
                        valence: 0.1,
                        resonance: 0.0
                    }
                }
            ]
        };

        // Intercept GET and OPTIONS requests to inject Mock Imprint
        await page.route(/\/entity\/.*\/memory\/imprints/, async route => {
            const headers = {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, DELETE, OPTIONS',
                'Access-Control-Allow-Headers': '*'
            };
            if (route.request().method() === 'OPTIONS') {
                await route.fulfill({ status: 200, headers });
            } else if (route.request().method() === 'GET') {
                await route.fulfill({ json: mockImprint, headers });
            } else {
                await route.continue();
            }
        });

        // Intercept DELETE requests
        let deletedId = "";
        await page.route(/\/entity\/.*\/memory\/imprints\/.*/, async route => {
            const headers = {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, DELETE, OPTIONS',
                'Access-Control-Allow-Headers': '*'
            };
            if (route.request().method() === 'OPTIONS') {
                await route.fulfill({ status: 200, headers });
            } else if (route.request().method() === 'DELETE') {
                const url = route.request().url();
                deletedId = url.substring(url.lastIndexOf("/") + 1);
                await route.fulfill({ json: { status: "success", message: "Forgotten." }, headers });
            } else {
                await route.continue();
            }
        });

        await page.goto('/journal');

        // Check Header
        await expect(page.locator('h1')).toContainText('Memory Imprint Journal');

        // Verify Imprint card renders
        await expect(page.locator('.imprint-card')).toBeVisible();
        await expect(page.locator('.imprint-card h3')).toContainText('test-hash-12345');

        // Verify Physics config details
        await expect(page.locator('.metric-box.config')).toContainText('Grid: 64');

        // Ensure Affect metrics exist
        await expect(page.locator('.metric-box.affect')).toContainText('Arousal: 1.00e+3');

        // Click Forget
        page.on('dialog', dialog => dialog.accept()); // Automatically accept the deterministic revert confirm box

        await page.locator('.forget-btn').click();

        // Verify that the route interceptor successfully captured the DELETE call for this ID
        // To be sure that delete happened, we wait for the interceptor logic
        await page.waitForTimeout(500);
        expect(deletedId).toBe("test-hash-12345");
    });

});
