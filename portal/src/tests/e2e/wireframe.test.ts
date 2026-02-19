import { test, expect } from '@playwright/test';

test.describe('Resonance Deck Wireframe', () => {
    test.beforeEach(async ({ page }) => {
        // Navigate to the main page
        await page.goto('/');

        // Wait for hydration
        await page.waitForLoadState('networkidle');
    });

    test('should render 32x32 SVG grid when active', async ({ page }) => {
        // 1. Ensure deck is active (it might be by default, or we might need to click)
        // Check if we need to open it. Assuming it's the main background or accessible via HUD.
        // If the deck is minimized, we might need to click the orb.

        // We'll look for the resonance-wave container.
        const waveContainer = page.locator('.resonance-wave');

        // Wait for it to be attached
        await expect(waveContainer).toBeAttached();

        // 2. Check for SVG existence
        const svg = waveContainer.locator('svg');
        await expect(svg).toBeVisible();

        // 3. Verify ViewBox (simulating the "strictly 32x32" requirement)
        await expect(svg).toHaveAttribute('viewBox', '0 0 32 32');
        await expect(svg).toHaveAttribute('preserveAspectRatio', 'none');

        // 4. Verify Paths are generated (requires JS execution/WAAPI)
        // We wait a bit for animation loop to produce paths
        await page.waitForTimeout(500);

        const paths = svg.locator('path');
        // Should have multiple paths (lines)
        expect(await paths.count()).toBeGreaterThan(0);

        // 5. Verify Path Attributes (roughly)
        const firstPath = paths.first();
        await expect(firstPath).toHaveAttribute('vector-effect', 'non-scaling-stroke');
        const stroke = await firstPath.getAttribute('stroke');
        expect(stroke).toBeTruthy(); // Should have a color
    });

    test('should animate (paths change over time)', async ({ page }) => {
        const waveContainer = page.locator('.resonance-wave');
        await expect(waveContainer).toBeVisible();
        const svg = waveContainer.locator('svg');
        const paths = svg.locator('path');

        // Capture initial state of the first path
        await page.waitForTimeout(200);
        const firstPath = paths.first();
        const d1 = await firstPath.getAttribute('d');

        // Wait for animation frame updates
        await page.waitForTimeout(200);
        const d2 = await firstPath.getAttribute('d');

        // Paths should be different if animation is running
        expect(d1).not.toBe(d2);
    });
});
