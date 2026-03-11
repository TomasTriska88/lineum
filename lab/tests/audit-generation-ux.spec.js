import { test, expect } from '@playwright/test';

test.describe('Audit Generation UX and Truthfulness', () => {

    test.beforeEach(async ({ page }) => {
        // Go to the lab page
        await page.goto('http://127.0.0.1:5174');
    });

    test('Production Policy - Button Disabled and Localhost Warning', async ({ page }) => {
        // Intercept config to simulate production
        await page.route('http://127.0.0.1:8000/api/lab/audit/config', async route => {
            const json = {
                allowed: false,
                cuda_available: true,
                execution_device: "cuda",
                device_name: "GPU",
                fallback_reason: null,
                reason: "Audit generation is available only on localhost / internal environment."
            };
            await route.fulfill({ json });
        });

        // Intercept verify_all to not crash
        await page.route('http://127.0.0.1:8000/api/lab/health', async route => {
            await route.fulfill({ json: { current_build: {}, active_audit: {} } });
        });

        await page.reload();

        // Check if the button is rendered but shows LOCAL ONLY and is disabled
        const genBtn = page.locator('button.btn-generate-audit');
        await expect(genBtn).toBeVisible();
        await expect(genBtn).toBeDisabled();
        await expect(genBtn).toContainText('LOCAL ONLY');
    });

    test('CPU Fallback Warning - Cancel', async ({ page }) => {
        // Intercept config to simulate CPU only
        await page.route('http://127.0.0.1:8000/api/lab/audit/config', async route => {
            const json = {
                allowed: true,
                cuda_available: false,
                execution_device: "cpu",
                device_name: "Standard CPU",
                fallback_reason: "Mock CPU only",
                reason: null
            };
            await route.fulfill({ json });
        });

        await page.reload();

        const genBtn = page.locator('button.btn-generate-audit');
        await expect(genBtn).toBeVisible();
        await expect(genBtn).toBeEnabled();
        await expect(genBtn).toContainText('GENERATE AUDIT CONTRACT');

        // Click to trigger warning
        await genBtn.click();

        // Warning modal should appear
        const modal = page.locator('.warning-modal');
        await expect(modal).toBeVisible();
        await expect(modal).toContainText('CUDA unavailable');
        await expect(modal).toContainText('Mock CPU only');

        // Click cancel
        await page.locator('.warning-modal .btn-cancel').click();

        // Modal should close
        await expect(modal).toBeHidden();

        // Progress should not start
        await expect(genBtn).toContainText('GENERATE AUDIT CONTRACT');
    });

    test('CPU Fallback Warning - Continue (Mock SSE)', async ({ page }) => {
        // Intercept config to simulate CPU only
        await page.route('http://127.0.0.1:8000/api/lab/audit/config', async route => {
            const json = {
                allowed: true,
                cuda_available: false,
                execution_device: "cpu",
                device_name: "Standard CPU",
                fallback_reason: "Mock CPU only",
                reason: null
            };
            await route.fulfill({ json });
        });

        // Intercept generate to stream mock SSE
        await page.route('http://127.0.0.1:8000/api/lab/audit/generate', async route => {
            const stream = "data: {\"status\":\"progress\",\"step\":0,\"detail\":\"Checking environment\",\"elapsed\":0.1}\n\n" +
                "data: {\"status\":\"success\",\"step\":5,\"detail\":\"Done\",\"new_run_id\":\"mock_run_123\",\"elapsed\":1.5}\n\n";
            await route.fulfill({
                status: 200,
                headers: { 'Content-Type': 'text/event-stream' },
                body: stream
            });
        });

        await page.reload();

        // Click generate
        await page.locator('button.btn-generate-audit').click();

        // Warning modal should appear
        const modal = page.locator('.warning-modal');
        await expect(modal).toBeVisible();

        // Setup dialog handler for the final window.alert
        page.on('dialog', async dialog => {
            expect(dialog.message()).toContain('Audit Contract Generated!');
            await dialog.accept();
        });

        // Click continue
        await page.locator('.warning-modal .btn-proceed').click();

        // Button should show generation
        await expect(page.locator('button.btn-generate-audit')).toContainText('Done');
    });

    test('CUDA Localhost - Direct Generation (Mock SSE)', async ({ page }) => {
        // Intercept config to simulate proper CUDA
        await page.route('http://127.0.0.1:8000/api/lab/audit/config', async route => {
            const json = {
                allowed: true,
                cuda_available: true,
                execution_device: "cuda",
                device_name: "Mock RTX",
                fallback_reason: null,
                reason: null
            };
            await route.fulfill({ json });
        });

        // Intercept generate to stream mock SSE
        await page.route('http://localhost:8000/api/lab/audit/generate', async route => {
            const stream = "data: {\"status\":\"progress\",\"step\":0,\"detail\":\"Checking environment\",\"elapsed\":0.1}\n\n" +
                "data: {\"status\":\"progress\",\"step\":1,\"detail\":\"Starting mock GPU run\",\"elapsed\":0.5}\n\n" +
                "data: {\"status\":\"success\",\"step\":5,\"detail\":\"Done\",\"new_run_id\":\"mock_run_gpu\",\"elapsed\":1.2}\n\n";
            await route.fulfill({
                status: 200,
                headers: { 'Content-Type': 'text/event-stream' },
                body: stream
            });
        });

        await page.reload();

        const genBtn = page.locator('button.btn-generate-audit');

        // Setup dialog handler for the final window.alert
        page.on('dialog', async dialog => {
            expect(dialog.message()).toContain('Audit Contract Generated!');
            await dialog.accept();
        });

        // Click generate
        await genBtn.click();

        // Modal should NOT appear
        await expect(page.locator('.warning-modal')).toBeHidden();

        // Wait for final state
        await expect(genBtn).toContainText('Done');
    });
});
