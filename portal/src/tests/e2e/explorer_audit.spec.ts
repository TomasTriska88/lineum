import { test, expect } from '@playwright/test';

test.describe('Explorer UI Audit', () => {
    test.beforeEach(async ({ page }) => {
        // Skip on mobile since the UI layout overflows and is intended for desktop debugging
        const viewport = page.viewportSize();
        if (viewport && viewport.width < 768) {
            test.skip();
        }

        // The explorer requires the backend to wake the entity
        await page.goto('/explorer', { waitUntil: 'networkidle' });
    });

    test('should display default RAW PHYSICS mode', async ({ page }) => {
        // Wait for the Explorer specific wrapper or header
        await expect(page.getByRole('heading', { name: 'Explorer', exact: true })).toBeVisible();

        // The exact case toggle label must be visible
        await expect(page.getByText('Voice: OFF', { exact: true })).toBeVisible();

        // Assert absence of VOICE ON
        await expect(page.getByText('VOICE ON')).not.toBeVisible();
    });

    test('should toggle to VOICE ON hybrid mode', async ({ page }) => {
        const toggleBtn = page.getByRole('button', { name: /Scientific/i });
        await toggleBtn.click();

        await expect(toggleBtn).toHaveClass(/bg-indigo-600/);
        await expect(page.getByRole('button', { name: 'Voice: OFF', exact: true })).toBeVisible(); // Still visible as an inactive button
    });

    test('should render inject input correctly', async ({ page }) => {
        const inputLocator = page.getByPlaceholder('Inject semantic perturbation (X)...');
        await expect(inputLocator).toBeVisible();

        const injectBtn = page.getByRole('button', { name: 'Inject' });
        await expect(injectBtn).toBeVisible();
    });
});
