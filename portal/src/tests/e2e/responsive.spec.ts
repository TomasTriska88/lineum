import { test, expect } from '@playwright/test';

test.describe('Sitewide User Comfort & Responsiveness', () => {

    // Test the main portal routes (can be expanded later)
    const routes = ['/', '/login', '/docs/index'];

    for (const route of routes) {
        test(`Mobile Viewport Layout for ${route}`, async ({ page, isMobile }) => {
            // Only run these stringent comfort tests on mobile devices
            if (!isMobile) return;

            await page.route('/data/manifest.json', async r => {
                await r.fulfill({ json: [] });
            });

            await page.goto(route);

            // 1. No-Horizontal-Scroll Assertion
            // The scrollWidth should not exceed the innerWidth of the window
            const layoutMetrics = await page.evaluate(() => {
                return {
                    scrollWidth: document.documentElement.scrollWidth,
                    innerWidth: window.innerWidth
                };
            });
            // We allow a tiny tolerance for potential scrollbar anomalies, but fundamentally they should match
            expect(layoutMetrics.scrollWidth).toBeLessThanOrEqual(layoutMetrics.innerWidth + 5);

            // 2. Touch Target Comfort (>= 44x44px)
            // Get all primary interactive elements
            const interactiveElements = await page.locator('button:visible, a:visible, select:visible, input:visible').all();

            for (const el of interactiveElements) {
                const box = await el.boundingBox();
                if (box) {
                    const tagName = await el.evaluate(n => n.tagName.toLowerCase());
                    const className = await el.evaluate(n => n.className);

                    if (tagName === 'button' || tagName === 'input' || tagName === 'select' || className.includes('btn')) {
                        if (box.height < 44) {
                            const html = await el.evaluate(n => n.outerHTML);
                            console.log(`\n🚨 TOUCH TARGET FAILED 🚨`);
                            console.log(`Element: ${html.substring(0, 150)}`);
                            console.log(`Height: ${box.height}px (Needs 44px)\n`);
                        }
                        expect(box.height, `Interactive element ${tagName}.${className} height ${box.height} is too small for touch`).toBeGreaterThanOrEqual(44);
                    }
                }
            }

            // 3. Readability Assertion (Fonts >= 16px)
            // Ensure paragraph text doesn't shrink below 16px on mobile
            const paragraphs = await page.locator('p:visible, span:visible, li:visible').all();
            for (const p of paragraphs) {
                // To avoid slowing down the test tracking thousands of spans, sample a few
                const text = await p.innerText();
                if (text.length > 50) { // Only care about actual blocks of text
                    const fontSize = await p.evaluate((el) => {
                        return window.getComputedStyle(el).fontSize;
                    });

                    // getComputedStyle returns strings like "16px"
                    const size = parseFloat(fontSize);
                    // Allow 14.0px just in case of subpixel rounding or secondary mobile metrics
                    if (size < 14.0) {
                        const html = await p.evaluate(n => n.outerHTML);
                        console.log(`\n🚨 READABILITY FAILED 🚨`);
                        console.log(`Text: ${html.substring(0, 100)}...`);
                        console.log(`Size: ${size}px (Needs 14px)\n`);
                    }
                    expect(size, `Font size ${fontSize} is below readability threshold for mobile`).toBeGreaterThanOrEqual(14.0);
                }
            }
        });
    }
});
