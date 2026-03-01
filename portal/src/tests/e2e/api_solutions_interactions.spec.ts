import { test, expect } from './base';

test.describe('API Solutions Applications Interactions', () => {

    test('Should successfully interact with Zeta Entropy API', async ({ page }) => {
        await page.goto('/api-solutions', { waitUntil: 'networkidle' });
        const section = page.locator('#zeta');
        await section.scrollIntoViewIfNeeded();
        await page.waitForTimeout(500);

        const simulateBtn = section.getByRole('button', { name: /Stream Entropy/i });
        await expect(simulateBtn).toBeVisible();
        await simulateBtn.click();

        await expect(section.getByRole('button', { name: /New Stream/i })).toBeVisible({ timeout: 20000 });
        await expect(section.getByText('DISTRIBUTION CONFIRMED', { exact: false })).toBeVisible({ timeout: 20000 });
    });

    test('Should successfully interact with Fast TRNG API', async ({ page }) => {
        await page.goto('/api-solutions', { waitUntil: 'networkidle' });
        // Original ID was fast_trng
        const section = page.locator('#fast_trng');
        await section.scrollIntoViewIfNeeded();
        await page.waitForTimeout(500);

        const sampleBtn = section.getByRole('button', { name: /Generate Session Key/i });
        await expect(sampleBtn).toBeVisible();
        await sampleBtn.click();

        await expect(section.getByRole('button', { name: /New Key/i })).toBeVisible({ timeout: 25000 });
        await expect(section.getByText('PASS', { exact: true }).first()).toBeVisible({ timeout: 25000 });
    });

    test('Should successfully interact with Web3 VRF API', async ({ page }) => {
        await page.goto('/api-solutions', { waitUntil: 'networkidle' });
        const section = page.locator('#web3');
        await section.scrollIntoViewIfNeeded();
        await page.waitForTimeout(500);

        const requestBtn = section.getByRole('button', { name: /Generate VRF Proof/i });
        await expect(requestBtn).toBeVisible();
        await requestBtn.click();

        await expect(section.getByRole('button', { name: /New VRF Hash/i })).toBeVisible({ timeout: 15000 });
        await expect(section.getByText('ON-CHAIN VERIFICATION PASSED', { exact: false })).toBeVisible();
    });

    test('Should successfully interact with LineumHash API', async ({ page }) => {
        await page.goto('/api-solutions', { waitUntil: 'networkidle' });
        const section = page.locator('#hash');
        await section.scrollIntoViewIfNeeded();
        await page.waitForTimeout(500);

        const inputField = section.getByPlaceholder(/Enter string data/i);
        await expect(inputField).toBeVisible();
        await inputField.fill('E2E Test Payload');

        await expect(section.getByText('mapping text tensor', { exact: false })).toBeVisible();
        await expect(section.getByText('0x', { exact: false }).last()).toBeVisible({ timeout: 10000 });
    });

    test('Should successfully interact with Gaming RNG API', async ({ page }) => {
        await page.goto('/api-solutions');
        const section = page.locator('#gaming');
        await section.scrollIntoViewIfNeeded();
        await page.waitForTimeout(500);

        const startBtn = section.getByRole('button', { name: /Generate Game Seed/i });
        await expect(startBtn).toBeVisible();
        await startBtn.click();

        await expect(section.getByRole('button', { name: /Stop Stream/i })).toBeVisible();
        await expect(section.getByText('TENSOR_SYNC', { exact: false })).toBeVisible({ timeout: 15000 });
    });

});
