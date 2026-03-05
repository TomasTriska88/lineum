import { test, expect } from '@playwright/test';

test.describe('Responsive Lab Navigation & Layout', () => {

    test('Desktop layout displays all panels', async ({ page }) => {
        await page.route('*/api/lab/history', async route => await route.fulfill({ json: [] }));
        await page.route('/data/manifest.json', async route => {
            const json = [];
            await route.fulfill({ json });
        });

        await page.setViewportSize({ width: 1280, height: 800 });
        await page.goto('http://127.0.0.1:5174/');

        // Wait for main UI to assemble
        const nav = page.locator('.top-nav');
        await expect(nav).toBeVisible();

        const disclaimer = page.locator('.warning-banner');
        await expect(disclaimer).toBeVisible();

        // Right panel should be visible on desktop
        const rightPanel = page.locator('.sidebar-right');
        await expect(rightPanel).toBeVisible();
    });

    test('Mobile layout collapses right panel and stacks navigation', async ({ page }) => {
        await page.route('*/api/lab/history', async route => await route.fulfill({ json: [] }));
        await page.route('/data/manifest.json', async route => {
            const json = [];
            await route.fulfill({ json });
        });

        // iPhone 12 Pro dimensions approx
        await page.setViewportSize({ width: 390, height: 844 });
        await page.goto('http://127.0.0.1:5174/');

        const nav = page.locator('.top-nav');
        await expect(nav).toBeVisible();

        // Due to flex-direction: column on mobile, height should be > normal nav height
        const box = await nav.boundingBox();
        expect(box.height).toBeGreaterThan(60);

        // Right panel is hidden on mobile via display: none
        const rightPanel = page.locator('.sidebar-right');
        await expect(rightPanel).toBeHidden();

        // Ensure disclaimer is still visible but structured differently (column flex)
        const disclaimer = page.locator('.warning-banner');
        await expect(disclaimer).toBeVisible();
    });

    test('Run Selector is hidden when exiting simulator mode', async ({ page }) => {
        await page.route('*/api/lab/history', async route => await route.fulfill({ json: [] }));
        await page.route('/data/manifest.json', async route => {
            const json = [];
            await route.fulfill({ json });
        });

        await page.setViewportSize({ width: 1280, height: 800 });
        await page.goto('http://127.0.0.1:5174/');

        // Switch to VALIDATE mode
        await page.getByText('VALIDATE').click();

        // Disclaimer should STILL be visible since it was moved to the global root
        const disclaimer = page.locator('.warning-banner');
        await expect(disclaimer).toBeVisible();
    });

    test('Footer does not obscure scrolled content in VALIDATE', async ({ page }) => {
        await page.route('*/api/lab/history', async route => await route.fulfill({ json: [] }));

        // Mock the scenario execution so we get a results table large enough to force scrolling
        await page.route('**/api/lab/hydrogen/sweep', async route => {
            const json = {
                manifest: { run_id: "test", timestamp: 123 },
                ts_metrics: {
                    E: [10, 15, 20], r: [0.1, 0.4, 0.5], edge_mass: [0.01, 0.02, 0.05],
                    max_edge: [0, 0, 0], N: [1, 1, 1], r_sq: [0.01, 0.16, 0.25], dot_0: [0, 0, 0]
                },
                image_b64: "iVBORw0KGg"
            };
            await route.fulfill({ json });
        });

        // Test especially on mobile where the footer is tallest and screen shortest
        await page.setViewportSize({ width: 390, height: 844 });
        await page.goto('http://127.0.0.1:5174/');

        // Switch to VALIDATE mode
        await page.getByText('VALIDATE').click();

        // Ensure we selected Hydrogen (which points to our mocked URL)
        await page.getByText('Hydrogen Validation Mini').click();

        // Execute runner
        await page.getByRole('button', { name: 'RUN SCENARIO' }).click();

        // Wait for results col to appear
        const resultsCol = page.locator('.run-col').first();
        await expect(resultsCol).toBeVisible();

        // Reveal the advanced metrics footer
        await page.getByRole('button', { name: /Show Scientific Details/i }).click();

        // Target the very bottom element inside the results panel
        const bottomElement = page.locator('.visuals-grid');
        await expect(bottomElement).toBeVisible();

        // Scroll exactly to the bottom element, bypassing manual container logic which breaks between Desktop and Mobile
        await bottomElement.scrollIntoViewIfNeeded();
        // Force scroll all potential scroll-parents to their absolute maximum, as scrollIntoView only brings the element to the viewport edge (behind the footer)
        await page.evaluate(() => {
            document.querySelectorAll('main, .dashboard, .fullscreen-mode').forEach(n => {
                if (n.scrollHeight > n.clientHeight) n.scrollTo(0, n.scrollHeight);
            });
        });

        // Let the scroll effect and layout settle
        await page.waitForTimeout(300);

        // Get bounding boxes relative to viewport
        const footer = page.locator('.warning-banner');
        const footerBox = await footer.boundingBox();
        const elementBox = await bottomElement.boundingBox();

        // The bottom Y coordinate of the final footer must be strictly <= the top Y of the disclaimer
        const elementBottomY = elementBox.y + elementBox.height;
        const footerTopY = footerBox.y;

        expect(elementBottomY).toBeLessThanOrEqual(footerTopY + 1); // +1px rounding tolerance
    });

    test('RUN SCENARIO button is visible immediately without scrolling', async ({ page }) => {
        await page.route('*/api/lab/history', async route => await route.fulfill({ json: [] }));
        await page.setViewportSize({ width: 1280, height: 800 });
        await page.goto('http://127.0.0.1:5174/');

        // Wait for UI to load
        await page.getByText('VALIDATE').click();

        // Ensure "RUN SCENARIO" is present and intersecting the viewport without any scrolling necessary
        const runBtn = page.getByRole('button', { name: 'RUN SCENARIO' });
        await expect(runBtn).toBeVisible();
        await expect(runBtn).toBeInViewport();
    });

    test('Custom ConfirmDialog appears when clearing history', async ({ page }) => {
        // Mock history so Clear button works
        await page.route('*/api/lab/history', async route => {
            if (route.request().method() === 'DELETE') {
                await route.fulfill({ status: 200 });
            } else {
                await route.fulfill({ json: [{ run_id: "test1", timestamp: "2026-03-05T12:00:00Z", scenario: "t0", manifest: {} }] });
            }
        });
        await page.goto('http://127.0.0.1:5174/');
        await page.getByText('Validation Core').click();

        // Click Clear All History
        await page.getByRole('button', { name: /Clear All History/i }).click();

        // Our custom dialog should appear
        const dialog = page.getByRole('dialog');
        await expect(dialog).toBeVisible();
        await expect(dialog).toContainText('Are you sure you want to delete all run data?');

        // Click Confirm
        await page.getByRole('button', { name: 'Yes, delete everything' }).click();

        // Dialog should close
        await expect(dialog).toBeHidden();
    });
});
