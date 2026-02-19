
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
    testDir: './src/tests/e2e',
    timeout: 30000,
    fullyParallel: true,
    forbidOnly: !!process.env.CI,
    retries: process.env.CI ? 2 : 0,
    workers: 1, // Enforce serial execution for reliability
    reporter: [['list'], ['html', { outputFolder: '.test-output/report' }]],
    outputDir: '.test-output/artifacts',
    use: {
        headless: true,
        baseURL: 'http://localhost:4173',
        trace: 'on-first-retry',
        extraHTTPHeaders: {
            'x-test-mode': 'true' // Signal to server we are in test mode
        }
    },
    projects: [
        {
            name: 'chromium',
            use: { ...devices['Desktop Chrome'] },
        },
    ],
    webServer: {
        command: 'cross-env GEMINI_API_KEY=INVALID_TEST_KEY npm run dev -- --port 4173',
        url: 'http://localhost:4173',
        reuseExistingServer: !process.env.CI,
        timeout: 120000,
        env: {
            GEMINI_API_KEY: 'INVALID_TEST_KEY',
            NODE_ENV: 'test'
        }
    },
});
