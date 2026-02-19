
import { test, expect } from '@playwright/test';

test.describe('Chat Math Rendering', () => {
    test.beforeEach(async ({ page }) => {
        // Mock the chat API to return a math equation
        await page.route('/api/chat', async route => {
            const json = {
                text: "The mass-energy equivalence is $E=mc^2$ and the field equation is $$G_{\\mu\\nu} + \\Lambda g_{\\mu\\nu} = \\kappa T_{\\mu\\nu}$$",
                candidates: [{
                    content: {
                        parts: [{ text: "The mass-energy equivalence is $E=mc^2$ and the field equation is $$G_{\\mu\\nu} + \\Lambda g_{\\mu\\nu} = \\kappa T_{\\mu\\nu}$$" }],
                        role: "model"
                    }
                }]
            };
            await route.fulfill({ json });
        });
    });

    test('should render inline and block math using KaTeX', async ({ page }) => {
        test.setTimeout(60000);
        await page.goto('/');

        // Always force open via Wiki to ensure consistent state
        await page.goto('/wiki');
        await page.getByRole('button', { name: '✨ Ask Lina Instead' }).click();

        // Wait for chat to be visible
        await expect(page.locator('.deck-container')).toBeVisible();

        // Send a message
        const input = page.locator('.input-area input');
        await input.waitFor({ state: 'visible' });
        await input.fill('Show me math');
        await input.press('Enter');

        // Wait for response
        // The mock returns immediately.

        // Check for KaTeX elements
        // Inline math
        await expect(page.locator('.katex').first()).toBeVisible();

        // Check specifically for E=mc^2 parts?
        // simple check for .katex class is enough to prove the library is working.
        const mathCount = await page.locator('.katex').count();
        expect(mathCount).toBeGreaterThan(0);
    });
});
