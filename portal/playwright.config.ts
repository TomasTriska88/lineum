
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
    testDir: './src/tests/e2e',
    timeout: 30000,
    fullyParallel: true,
    forbidOnly: !!process.env.CI,
    retries: process.env.CI ? 2 : 0,
    workers: process.env.CI ? 1 : undefined,
    reporter: 'list',
    use: {
        baseURL: 'http://localhost:4173',
        trace: 'on-first-retry',
        // CRITICAL: Block all external requests by default
        // We will whitelist localhost in tests or specific network contexts
    },
    projects: [
        {
            name: 'chromium',
            use: { ...devices['Desktop Chrome'] },
        },
    ],
    webServer: {
        command: 'npm run preview -- --port 4173',
        url: 'http://localhost:4173',
        reuseExistingServer: !process.env.CI,
        timeout: 120000, // Give extensive time for server boot
    },
});
