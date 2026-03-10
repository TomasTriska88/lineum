import { test, expect } from '@playwright/test';

test.describe('Particle Presets Sandbox Guards', () => {
    test.beforeEach(async ({ page }) => {
        // Mock health endpoint
        await page.route('**/api/lab/health', async route => {
            await route.fulfill({ json: { status: "ok", commit_hash: "test-hash", tests: "1/1 PASS", loaded_modules: { routing_backend: "mock", validation_core: "mock" } } });
        });

        // Mock validation API — returns timeseries_data + explain_pack matching component expectations
        await page.route('**/api/lab/playground', async route => {
            let body = {};
            try {
                const postData = route.request().postData();
                if (postData) body = JSON.parse(postData);
            } catch (e) { /* GET or empty body */ }
            const Z = parseFloat(body.config?.Z) || 1;
            const dt = parseFloat(body.config?.dt) || 0;

            let json = {
                manifest: { run_id: "test", timestamp: 123, git: "test-hash", overall_pass: true },
                timeseries_data: {
                    E: [10, 15, 20], r: [0.1, 0.4, 0.5], max_edge: [0, 0, 0]
                },
                expectations: [
                    { metric: "edge_mass_max", op: "<", value: 0.05, label: "Max edge mass < 5%", human_label: "Cloud stays contained" }
                ],
                expectation_results: [
                    { metric: "edge_mass_max", op: "<", value: 0.05, label: "Max edge mass < 5%", human_label: "Cloud stays contained", measured: 0.02, expected: 0.05, passed: true }
                ],
                overall_pass: true,
                explain_pack: {
                    one_liner_human: "Custom Sandbox for tuning particle environments and shapes.",
                    what_you_see: ["The resulting wave density mapped to color.", "Brighter = denser particle cloud."],
                    what_it_is_not: ["Not validation-grade unless locked.", "Free parameters can cause the engine to explode numerically."],
                    success_criteria_human: "Expectations met: The wave equation behaves according to known physics.",
                    next_action_pass: "Compare to History / Export Data",
                    next_action_fail: "Make stable / Enhance Grid",
                    disclaimers: ["2D Slice: You are looking at a cross-section.", "Single-particle analog."],
                    glossary_terms_used: ["Validate", "Explore", "Cloud", "Leak"]
                },
                image_b64: "iVBORw0KGg"
            };

            // Chaotic if Z >= 6 and dt is too large (one makeStable halving → 0.025 → STABLE)
            if (Z >= 6 && dt >= 0.04) {
                json.timeseries_data.edge_mass = [0.01, 0.2, 0.5]; // CHAOTIC
                json.overall_pass = false;
                json.expectation_results[0].passed = false;
                json.expectation_results[0].measured = 0.5;
            } else if (Z >= 3 && dt >= 0.03) {
                json.timeseries_data.edge_mass = [0.01, 0.1, 0.15]; // LEAKING
                json.overall_pass = false;
                json.expectation_results[0].passed = false;
                json.expectation_results[0].measured = 0.15;
            } else {
                json.timeseries_data.edge_mass = [0.01, 0.02, 0.03]; // STABLE
            }
            await route.fulfill({ json });
        });

        // Mock other API endpoints
        await page.route('**/api/lab/history', async route => await route.fulfill({ json: [] }));
        await page.route('**/api/lab/hydrogen/**', async route => {
            await route.fulfill({ json: { manifest: { run_id: "test", timestamp: 123 }, timeseries_data: { E: [10], r: [0.1], edge_mass: [0.01], max_edge: [0] }, explain_pack: { one_liner_human: "Simulating a Hydrogen-like atom.", what_you_see: ["Density map of particle."], what_it_is_not: ["Not quantum chemistry."], success_criteria_human: "Expectations met.", next_action_pass: "Compare", next_action_fail: "Fix", disclaimers: ["2D Slice."], glossary_terms_used: ["Cloud"] }, image_b64: "iVBORw0KGg" } });
        });
        await page.route('**/api/lab/regression/**', async route => {
            await route.fulfill({ json: { manifest: { run_id: "test", timestamp: 123 }, timeseries_data: { E: [10], r: [0.1], edge_mass: [0.01], max_edge: [0] }, explain_pack: { one_liner_human: "Memory test.", what_you_see: ["Mu map."], what_it_is_not: ["Not a fluid trace."], success_criteria_human: "Met.", next_action_pass: "Compare", next_action_fail: "Fix", disclaimers: [], glossary_terms_used: [] }, image_b64: "iVBORw0KGg" } });
        });
        await page.route('**/data/manifest.json', async route => {
            await route.fulfill({ json: [] });
        });

        await page.setViewportSize({ width: 1280, height: 800 });
        await page.goto('/');
        // Navigate to the Validation Dashboard
        await page.getByRole('button', { name: 'Validation Core' }).click();
    });

    test('Unstable preset triggers Chaotic warning and Make stable works', async ({ page }) => {
        // Go to Explore Mode
        await page.getByText('⚡ EXPLORE').click();
        await page.getByText('Single-particle Bound-state Analogs').click();

        // Select O-like preset (Z=8)
        await page.getByRole('button', { name: /O-like/ }).click();

        // Set dt to 0.05 to trigger CHAOTIC in mock (Z=8 >= 6, dt=0.05 >= 0.04)
        const dtInput = page.locator('input[type="number"]').nth(2);
        await dtInput.fill('0.05');

        // Run Scenario
        await page.getByRole('button', { name: 'RUN SCENARIO' }).click();

        // Wait for result
        await expect(page.getByRole('button', { name: 'RUN SCENARIO' })).toBeEnabled({ timeout: 10000 });

        // Check for Chaotic Status
        await expect(page.locator('text=❌ Chaotic (Unstable)')).toBeVisible({ timeout: 10000 });

        // Check single "Make stable" button (Canon §6 — one button, not two)
        const makeStableBtn = page.getByRole('button', { name: /Make stable/i }).first();
        await expect(makeStableBtn).toBeVisible();

        // Click Make stable — it runs multi-step stabilization (dt↓ → eps↑ → grid↑)
        await makeStableBtn.click();

        // After makeStable: dt halved from 0.05 to 0.025
        // Mock: Z=8>=6 but dt=0.025<0.04 → not CHAOTIC, Z=8>=3 but dt=0.025<0.03 → not LEAKING → STABLE
        await expect(page.locator('text=✅ Stable cloud')).toBeVisible({ timeout: 15000 });
    });

    test('Explain Pack renders after RUN (Canon §2)', async ({ page }) => {
        // Go to Explore Mode
        await page.getByText('⚡ EXPLORE').click();
        await page.getByText('Single-particle Bound-state Analogs').click();

        // Select H-like preset (Z=1, stable)
        await page.getByRole('button', { name: /H-like/ }).click();

        // Run Scenario
        await page.getByRole('button', { name: 'RUN SCENARIO' }).click();
        await expect(page.locator('text=✅ Stable cloud')).toBeVisible();

        // Explain Pack MUST be visible (Canon §2)
        const explainPack = page.locator('#explain-pack');
        await expect(explainPack).toBeVisible({ timeout: 5000 });

        // Check Canon mandatory fields render
        await expect(page.locator('text=What you\'re seeing')).toBeVisible();
        await expect(page.locator('text=What this is NOT')).toBeVisible();

        // Check one_liner_human content renders
        await expect(page.locator('.ep-liner')).toBeVisible();
        await expect(page.locator('.ep-liner')).toContainText('Sandbox');
    });

    test('Glossary opens with 1 click and contains Canon terms (Canon §5)', async ({ page }) => {
        // Glossary toggle must be always accessible
        const glossaryBtn = page.getByRole('button', { name: /Glossary/i });
        await expect(glossaryBtn).toBeVisible();

        // Click Glossary
        await glossaryBtn.click();

        // Panel must open
        const panel = page.locator('.glossary-panel');
        await expect(panel).toBeVisible({ timeout: 3000 });

        // Must contain Canon terms: Cloud / Blob and Leak
        await expect(panel.locator('text=Cloud / Blob')).toBeVisible();
        await expect(panel.locator('text=Leak')).toBeVisible();

        // Close glossary by clicking overlay backdrop (left side, outside the 380px panel)
        await page.mouse.click(50, 400);
        await expect(panel).toBeHidden({ timeout: 3000 });
    });

    test('Charts can be maximized using the MAX button', async ({ page }) => {
        // Go to Explore Mode
        await page.getByText('⚡ EXPLORE').click();
        await page.getByText('Single-particle Bound-state Analogs').click();

        // Select H-like preset
        await page.getByRole('button', { name: /H-like/ }).click();

        // Run Scenario
        await page.getByRole('button', { name: 'RUN SCENARIO' }).click();

        await expect(page.locator('text=✅ Stable cloud')).toBeVisible();

        // Click show details
        await page.getByRole('button', { name: 'Show Scientific Details' }).click();

        // Ensure charts show up
        await expect(page.locator('.metrics-dashboard')).toBeVisible();

        // Ensure chart cards are present
        const chartCards = page.locator('.metric-card');
        await expect(chartCards.first()).toBeVisible();

        // Click first chart card to maximize
        await chartCards.first().click();

        // Ensure Modal appears
        const modal = page.locator('.modal-content');
        await expect(modal).toBeVisible();

        // Close modal
        await page.getByRole('button', { name: 'Close' }).click();
        await expect(modal).toBeHidden();
    });

    test('RUN SCENARIO button remains sticky and visible when sidebar overflows', async ({ page }) => {
        // Go to Explore mode which opens more Tuning inputs
        await page.getByText('⚡ EXPLORE').click();
        await page.getByText('Single-particle Bound-state Analogs').click();

        // Ensure mega run button is visible in DOM
        const runBtn = page.locator('.mega-run');
        await expect(runBtn).toBeVisible();

        // Check if it's currently intersecting with its scroll container (visible before scrolling)
        let isIntersecting = await runBtn.evaluate((btn) => {
            const rect = btn.getBoundingClientRect();
            const parentRect = btn.closest('.sidebar-left').getBoundingClientRect();
            return rect.top >= parentRect.top && Math.floor(rect.bottom) <= Math.ceil(parentRect.bottom);
        });
        expect(isIntersecting).toBeTruthy();

        // Scroll the sidebar itself if it has overflow
        const sidebar = page.locator('.sidebar-left');
        await sidebar.evaluate((node) => node.scrollTo(0, node.scrollHeight));
        await page.waitForTimeout(100);

        // Check if it's STILL visible after scrolling to bottom
        isIntersecting = await runBtn.evaluate((btn) => {
            const rect = btn.getBoundingClientRect();
            const parentRect = btn.closest('.sidebar-left').getBoundingClientRect();
            return rect.top >= parentRect.top && Math.floor(rect.bottom) <= Math.ceil(parentRect.bottom);
        });
        expect(isIntersecting).toBeTruthy();
    });

    test('Clear DB button prompts and wipes run history', async ({ page, isMobile }) => {
        // Mobile layout hides the sidebar-right completely via CSS display:none
        if (isMobile) {
            test.skip();
            return;
        }

        // Override the history mock to return 2 items
        await page.route('**/api/lab/history', async route => {
            if (route.request().method() === 'GET') {
                await route.fulfill({
                    json: [
                        { run_id: "fake_run_1", timestamp: "2026-03-05T12:00:00Z", scenario: "h_ground" },
                        { run_id: "fake_run_2", timestamp: "2026-03-05T12:05:00Z", scenario: "c_p1" }
                    ]
                });
            } else if (route.request().method() === 'DELETE') {
                await route.fulfill({ status: 200, json: { status: "cleared" } });
            } else {
                await route.continue();
            }
        });

        // Reload so the GET hits the mocked route and populates the sidebar
        await page.goto('/');
        await page.getByRole('button', { name: 'Validation Core' }).click();

        // Ensure history cards are visible
        await expect(page.locator('.hist-card')).toHaveCount(2);

        // Click the Clear DB button — this opens the custom ConfirmDialog
        await page.locator('.clear-db-btn').click({ force: true });

        // The custom ConfirmDialog should now be open
        await expect(page.getByRole('button', { name: /Yes, delete everything/i })).toBeVisible({ timeout: 5000 });

        // Override history mock to return empty array
        await page.route('**/api/lab/history', async route => {
            if (route.request().method() === 'GET') {
                await route.fulfill({ json: [] });
            } else if (route.request().method() === 'DELETE') {
                await route.fulfill({ status: 200, json: { status: "cleared" } });
            } else {
                await route.continue();
            }
        });

        // Confirm the deletion
        await page.getByRole('button', { name: /Yes, delete everything/i }).click();

        // Confirm history list is empty
        await expect(page.locator('.hist-card')).toHaveCount(0);
    });
});
