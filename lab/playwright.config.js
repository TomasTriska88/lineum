import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
    testDir: './tests',
    fullyParallel: true,
    forbidOnly: !!process.env.CI,
    retries: process.env.CI ? 2 : 0,
    reporter: [['html', { outputFolder: '.scratch/playwright-report', open: 'never' }]],
    outputDir: '.scratch/test-results',
    use: {
        baseURL: 'http://127.0.0.1:5174',
        trace: 'on-first-retry',
    },
    webServer: {
        command: 'npm run build && npm run preview -- --port 5174',
        url: 'http://127.0.0.1:5174',
        reuseExistingServer: !process.env.CI,
        timeout: 120 * 1000,
    },

    projects: [
        {
            name: 'chromium',
            use: { ...devices['Desktop Chrome'] },
        },
        {
            name: 'Mobile Chrome',
            use: { ...devices['Pixel 5'] },
        },
    ],
});
