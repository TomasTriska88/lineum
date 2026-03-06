import { test, expect } from '@playwright/test';

test('Debug: verify mock intercepts cross-origin fetch to port 8000', async ({ page }) => {
    let mockHit = false;

    await page.route('**/api/lab/playground', async route => {
        mockHit = true;
        console.log('MOCK HIT! URL:', route.request().url());
        await route.fulfill({ json: { test: true } });
    });

    await page.route('**/api/lab/health', async route => {
        await route.fulfill({ json: { status: "ok", build: "test", loaded_modules: { routing_backend: "mock", validation_core: "mock" } } });
    });
    await page.route('**/api/lab/history', async route => await route.fulfill({ json: [] }));
    await page.route('**/data/manifest.json', async route => await route.fulfill({ json: [] }));

    await page.setViewportSize({ width: 1280, height: 800 });
    await page.goto('http://127.0.0.1:5174/');
    await page.getByRole('button', { name: 'Validation Core' }).click();

    // Navigate to playground
    await page.getByText('⚡ EXPLORE').click();
    await page.getByText('Single-particle Bound-state Analogs').click();
    await page.getByRole('button', { name: /Double/ }).click();

    // Listen for console messages
    page.on('console', msg => console.log('BROWSER:', msg.text()));

    // Click RUN to trigger fetch
    await page.getByRole('button', { name: 'RUN SCENARIO' }).click();

    // Wait a bit for the fetch to happen
    await page.waitForTimeout(3000);

    // Check the button state
    const btnText = await page.getByRole('button', { name: /RUN SCENARIO|EXECUTING/ }).textContent();
    console.log('Button text after 3s:', btnText);

    // Make sure the mock was actually hit
    console.log('Mock was hit:', mockHit);
});
