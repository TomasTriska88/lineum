import { test, expect } from '@playwright/test';

test('Standalone Chaotic test (no beforeEach)', async ({ page }) => {
    // Mock health
    await page.route('**/api/lab/health', async route => {
        await route.fulfill({ json: { status: "ok", build: "test", loaded_modules: { routing_backend: "mock", validation_core: "mock" } } });
    });
    // Mock playground API
    await page.route('**/api/lab/playground', async route => {
        let body = {};
        try { body = route.request().postDataJSON(); } catch (e) { }
        let json = {
            manifest: { run_id: "test", timestamp: 123, git: "test-hash" },
            ts_metrics: {
                E: [10, 15, 20], r: [0.1, 0.4, 0.5], max_edge: [0, 0, 0]
            },
            image_b64: "iVBORw0KGg"
        };
        if (body?.config?.potential_type === 'double_well' && body?.config?.dt >= 0.05) {
            json.ts_metrics.edge_mass = [0.01, 0.2, 0.5]; // CHAOTIC
        } else if (body?.config?.dt >= 0.02) {
            json.ts_metrics.edge_mass = [0.01, 0.1, 0.15];
        } else {
            json.ts_metrics.edge_mass = [0.01, 0.02, 0.03];
        }
        console.log('MOCK HIT! potential:', body?.config?.potential_type, 'dt:', body?.config?.dt, 'edge_mass:', json.ts_metrics.edge_mass);
        await route.fulfill({ json });
    });
    await page.route('**/api/lab/history', async route => await route.fulfill({ json: [] }));
    await page.route('**/data/manifest.json', async route => await route.fulfill({ json: [] }));

    await page.setViewportSize({ width: 1280, height: 800 });

    // Listen for console
    page.on('console', msg => {
        if (msg.type() === 'log' || msg.type() === 'error') console.log('BROWSER:', msg.text());
    });

    await page.goto('/');
    await page.getByRole('button', { name: 'Validation Core' }).click();

    // Go to Explore Mode
    await page.getByText('⚡ EXPLORE').click();
    await page.getByText('Single-particle Bound-state Analogs').click();

    // Select Double
    await page.getByRole('button', { name: /Double/ }).click();

    // Run Scenario
    console.log('About to click RUN SCENARIO');
    await page.getByRole('button', { name: 'RUN SCENARIO' }).click();
    console.log('Clicked RUN SCENARIO');

    // Wait for RUN SCENARIO to return
    await expect(page.getByRole('button', { name: 'RUN SCENARIO' })).toBeVisible({ timeout: 15000 });
    console.log('RUN SCENARIO button returned');

    // Check for Chaotic Status
    await expect(page.locator('text=❌ Chaotic (Unstable)')).toBeVisible({ timeout: 10000 });
    console.log('Chaotic text found!');
});
