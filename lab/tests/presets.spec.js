import { test, expect } from '@playwright/test';

test.describe('Particle Presets Sandbox Guards', () => {
    test.beforeEach(async ({ page }) => {
        // Mock validation API
        await page.route('**/api/lab/playground', async route => {
            const body = await route.request().postDataJSON();
            let json = {
                manifest: { run_id: "test", timestamp: 123, git: "test-hash" },
                ts_metrics: {
                    E: [10, 15, 20], r: [0.1, 0.4, 0.5], max_edge: [0, 0, 0]
                },
                image_b64: "iVBORw0KGg"
            };

            // If dt is large and Z is high, leak edge mass
            if (body.config?.Z === 8 && body.config?.dt === 0.005) {
                json.ts_metrics.edge_mass = [0.01, 0.2, 0.5]; // CHAOTIC
            } else if (body.config?.Z === 6 && body.config?.dt >= 0.01) {
                json.ts_metrics.edge_mass = [0.01, 0.1, 0.15]; // LEAKING
            } else {
                json.ts_metrics.edge_mass = [0.01, 0.02, 0.03]; // STABLE
            }
            await route.fulfill({ json });
        });

        await page.route('**/api/lab/history', async route => await route.fulfill({ json: [] }));
        await page.route('**/data/manifest.json', async route => {
            await route.fulfill({ json: [] });
        });

        await page.setViewportSize({ width: 1280, height: 800 });
        await page.goto('http://127.0.0.1:5174/');
        // Navigate to the Validation Dashboard
        await page.getByRole('button', { name: 'Validation Core' }).click();
    });

    test('O-like preset triggers Chaotic warning and Auto-Fix works', async ({ page }) => {
        // Go to Explore Mode
        await page.getByText('⚡ EXPLORE').click();
        await page.getByText('Single-particle Bound-state Analogs').click();

        // Select O-like
        await page.getByRole('button', { name: 'O-like' }).click();

        // Run Scenario
        await page.getByRole('button', { name: 'RUN SCENARIO' }).click();

        // Check for Chaotic Status
        await expect(page.locator('text=☠️ CHAOTIC / COLLAPSED')).toBeVisible();

        // Check Auto-Fix button
        const autoFix = page.getByRole('button', { name: /Auto-Fix/i });
        await expect(autoFix).toBeVisible();

        // Click Auto-Fix
        await autoFix.click();

        // Given our mocked logic, a safer dt will yield -> STABLE (unless our auto fix doesn't hit it quickly, but 0.25 dt drop avoids the Z=8 threshold in our mock)
        await expect(page.locator('text=✅ STABLE CLOUD')).toBeVisible();
    });

    test('Charts can be maximized using the MAX button', async ({ page }) => {
        // Go to Explore Mode
        await page.getByText('⚡ EXPLORE').click();
        await page.getByText('Single-particle Bound-state Analogs').click();

        // Select H-like
        await page.getByRole('button', { name: 'H-like' }).click();

        // Run Scenario
        await page.getByRole('button', { name: 'RUN SCENARIO' }).click();

        await expect(page.locator('text=✅ STABLE CLOUD')).toBeVisible();

        // Click show details
        await page.getByRole('button', { name: 'Show Scientific Details' }).click();

        // Ensure charts show up
        await expect(page.locator('.charts-section')).toBeVisible();

        // Ensure MAX buttons are present
        const maxBtns = page.getByRole('button', { name: 'MAX' });
        await expect(maxBtns.first()).toBeVisible();

        // Click first MAX button
        await maxBtns.first().click();

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
            // Using a 1px tolerance 
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

    test('Clear DB button prompts and wipes run history', async ({ page }) => {
        // Set up an initial fake history response
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
        await page.goto('http://127.0.0.1:5174/');
        await page.getByRole('button', { name: 'Validation Core' }).click();

        // Ensure history cards are visible
        await expect(page.locator('.hist-card')).toHaveCount(2);

        // Prep dialog handler to accept the confirm()
        page.on('dialog', dialog => dialog.accept());

        // Click Clear DB button
        const clearBtn = page.getByRole('button', { name: '🗑️ Clear' });
        await expect(clearBtn).toBeVisible();

        // Change the route mock to return empty array after deletion
        await page.route('**/api/lab/history', async route => {
            if (route.request().method() === 'GET') {
                await route.fulfill({ json: [] });
            } else if (route.request().method() === 'DELETE') {
                await route.fulfill({ status: 200, json: { status: "cleared" } });
            } else {
                await route.continue();
            }
        });

        await clearBtn.click();

        // Confirm history list is empty
        await expect(page.locator('.hist-card')).toHaveCount(0);
    });
});
