import { expect, test } from '@playwright/test';

test.describe('Routing Pulse Lab - Advanced Holo UI & WebGL Lifecycle', () => {

    test('Page load, UI elements and navigation without WebGL memory leaks', async ({ page }) => {
        const consoleErrors: string[] = [];

        // Listen for memory leak errors such as "Too many active WebGL contexts"
        page.on('console', msg => {
            if (msg.type() === 'error' || msg.type() === 'warning') {
                const text = msg.text().toLowerCase();
                if (text.includes('too many active')) {
                    consoleErrors.push(msg.text());
                }
            }
        });

        // Mock the backend API to ensure the test does not depend on the python server
        await page.route('**/api/route/task', async route => {
            await route.fulfill({ status: 200, json: { task_id: 'mock-task-id' } });
        });

        // Step 1: Direct navigation to Routing Lab
        await page.goto('/api-solutions');

        // Monitor the visibility of the canvas element
        const webglCanvas = page.locator('#routing canvas').first();
        await expect(webglCanvas).toBeVisible({ timeout: 10000 });

        // Test the existence of the main B2B UI elements
        await expect(page.getByText('Lineum API Solutions', { exact: false })).toBeVisible();

        const startBtn = page.getByRole('button', { name: /Optimize Fleet Routes/i });
        await expect(startBtn).toBeVisible();

        // Step 2: Start and check tensor field UI
        // We evaluate the request and don't immediately drop the socket to keep "isSimulating" true.
        // We override the WebSocket constructor locally for this test.
        await page.addInitScript(() => {
            window.WebSocket = class MockWebSocket {
                onmessage: any;
                onclose: any;
                constructor() {
                    setTimeout(() => {
                        if (this.onmessage) {
                            this.onmessage({ data: JSON.stringify({ step: 1, phi_flat: [], paths: {} }) });
                        }
                    }, 100);
                }
                close() {
                    if (this.onclose) this.onclose();
                }
                send() { }
            } as any;
        });

        await startBtn.click();

        // Wait for simulating state to finish
        const doneBtn = page.getByRole('button', { name: /New Iteration/i });
        await expect(doneBtn).toBeVisible({ timeout: 10000 });
        await page.waitForTimeout(500); // let the WebGL routing output render

        // Step 3: Lifecycle navigation to verify onDestroy WebGL memory leak cleanup
        // We go back to the Homepage, and then back to Routing.
        await page.goto('/');
        await page.waitForLoadState('networkidle');

        // The second Canvas on the homepage must initialize its WebGL Context correctly
        await expect(page.locator('canvas.shader-canvas')).toBeVisible();

        // And back to routing to initialize another WebGL Context
        // If cleanup is missing, a "Too many contexts" warning will definitely appear.
        await page.goto('/api-solutions');
        await expect(page.locator('#routing canvas').first()).toBeVisible();

        // Evaluate if any WebGL limit errors were caught in the console.
        expect(consoleErrors).toEqual([]);
    });

});
