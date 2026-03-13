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

            // 2. Touch Target Comfort (>= 16px for native range sliders and microbuttons)
            // Explicitly filter out non-interactive structurals and SVG internal elements
            // Execute the touch-target scan internally to bypass Playwright DOM evaluation latency
            const touchViolations = await page.evaluate(() => {
                // Filter structural menus and SVGs
                const nodes = document.querySelectorAll('a:not(nav.mobile-menu *):not(svg *), button:not(nav.mobile-menu *):not(svg *), input, select, [role="button"], .btn');
                const fails: { tag: string, class: string, height: number, html: string }[] = [];

                for (let i = 0; i < nodes.length; i++) {
                    const el = nodes[i] as HTMLElement;
                    // Approximate visibility
                    if (el.offsetWidth > 0 && el.offsetHeight > 0) {
                        const style = window.getComputedStyle(el);
                        if (style.display !== 'none' && style.visibility !== 'hidden') {
                            const rect = el.getBoundingClientRect();
                            if (rect.height > 0 && rect.height < 16) {
                                const tag = el.tagName.toLowerCase();
                                const cls = el.className;
                                if (tag === 'button' || tag === 'input' || tag === 'select' || (typeof cls === 'string' && cls.includes('btn'))) {
                                    fails.push({
                                        tag: tag,
                                        class: cls,
                                        height: rect.height,
                                        html: el.outerHTML.substring(0, 150)
                                    });
                                }
                            }
                        }
                    }
                }
                return fails;
            });

            if (touchViolations.length > 0) {
                console.log(`\n🚨 TOUCH TARGET FAILED 🚨`);
                console.log(touchViolations);
            }
            expect(touchViolations.length, `Found ${touchViolations.length} interactive elements below 16px touch height on mobile.`).toBe(0);

            // 3. Readability Assertion (Fonts >= 14px)
            // Ensure paragraph text doesn't shrink below 14px on mobile
            // We evaluate this entirely within browser context to prevent Playwright IPC timeouts
            const violations = await page.evaluate(() => {
                const nodes = document.querySelectorAll('p, span, li');
                const fails: { text: string, size: number, html: string }[] = [];

                for (let i = 0; i < nodes.length; i++) {
                    const el = nodes[i] as HTMLElement;
                    // Approximate visibility check
                    if (el.offsetWidth > 0 && el.offsetHeight > 0) {
                        const text = el.innerText || '';
                        if (text.length > 50) {
                            const style = window.getComputedStyle(el);
                            const size = parseFloat(style.fontSize);
                            if (size < 14.0) {
                                fails.push({
                                    text: text.substring(0, 100) + '...',
                                    size: size,
                                    html: el.outerHTML.substring(0, 150)
                                });
                            }
                        }
                    }
                }
                return fails;
            });

            if (violations.length > 0) {
                console.log(`\n🚨 READABILITY FAILED 🚨`);
                console.log(violations);
            }
            expect(violations.length, `Found ${violations.length} typography readability violations on mobile viewport.`).toBe(0);
        });
    }
});
