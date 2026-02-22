import { test, expect } from '@playwright/test';

test.describe('Mobile Responsiveness', () => {
    // Tests will run with the default viewport for the project (Pixel 5 for mobile-chrome)
    test.skip(({ isMobile }) => !isMobile, 'Mobile responsiveness tests only run on mobile projects');

    test.beforeEach(async ({ page }) => {
        // Bypass cookie banner
        await page.addInitScript(() => {
            localStorage.setItem('cookie_consent', 'accepted');
        });

        await page.goto('/');
        // Wait for hydration
        await page.waitForLoadState('networkidle');
    });

    test('Hero Section Layout', async ({ page }) => {
        const hero = page.locator('.hero');
        await expect(hero).toBeVisible();

        // Check if flex direction is column (stacked)
        const flexDirection = await hero.evaluate((el) => {
            return window.getComputedStyle(el).flexDirection;
        });
        expect(flexDirection).toBe('column');

        // Check H1 visibility and size
        const h1 = page.locator('h1');
        await expect(h1).toBeVisible();
        const fontSize = await h1.evaluate((el) => {
            return window.getComputedStyle(el).fontSize;
        });
        // 2.5rem * 14px (root font size on mobile) = 35px. 
        // 2.5rem * 16px = 40px. 
        // Allowing range
        expect(parseInt(fontSize)).toBeLessThanOrEqual(56); // definitely smaller than desktop ~3.5rem (56px)
    });

    test('CTA Group Layout', async ({ page }) => {
        const ctaGroup = page.locator('.cta-group');
        await expect(ctaGroup).toBeVisible();

        // Check if flex direction is column (stacked)
        const flexDirection = await ctaGroup.evaluate((el) => {
            return window.getComputedStyle(el).flexDirection;
        });
        expect(flexDirection).toBe('column');

        // Check buttons take mostly full width of container
        const buttons = ctaGroup.locator('.btn');
        const count = await buttons.count();
        expect(count).toBeGreaterThan(0);

        for (let i = 0; i < count; i++) {
            const btn = buttons.nth(i);
            const btnBox = await btn.boundingBox();
            const groupBox = await ctaGroup.boundingBox();
            if (btnBox && groupBox) {
                expect(btnBox.width).toBeCloseTo(groupBox.width, -1);
            }
        }
    });

    test('Navigation Layout', async ({ page }) => {
        const navContent = page.locator('.nav-content');

        // Check if flex direction is row (Logo + Toggle)
        const flexDirection = await navContent.evaluate((el) => {
            return window.getComputedStyle(el).flexDirection;
        });
        expect(flexDirection).toBe('row');

        // Check Toggle Button Visibility
        const toggle = page.locator('.mobile-toggle');
        await expect(toggle).toBeVisible();

        // Check Links are hidden initially
        const navLinks = page.locator('.nav-links');
        await expect(navLinks).toBeHidden();

        // Click Toggle
        await toggle.click();

        // Check Links are visible
        await expect(navLinks).toBeVisible();
        await expect(navLinks).toHaveCSS('flex-direction', 'column');
    });

    test('Chat Interface (ResonanceDeck)', async ({ page }) => {
        // By default on mobile, deck should be at bottom
        const wrapper = page.locator('.resonance-wrapper');
        await expect(wrapper).toBeVisible();

        const bottom = await wrapper.evaluate((el) => {
            return window.getComputedStyle(el).bottom;
        });
        expect(bottom).toBe('0px');

        // Open the deck (Orb -> Bar)
        await page.locator('.deck-main').click({ force: true });
        await page.waitForTimeout(500); // Wait for transition

        // Open the chat (Bar -> Panel)
        await page.locator('.deck-main').click({ force: true });

        // Check input accessibility
        const input = page.locator('input[type="text"]');
        await expect(input).toBeVisible(); // Should be visible even if behind keyboard (logic handled by browser but element must be there)
    });

    test('Card Layout', async ({ page }) => {
        const grid = page.locator('.scientific-grid');
        const gridTemplateColumns = await grid.evaluate((el) => {
            return window.getComputedStyle(el).gridTemplateColumns;
        });
        // Should be 1fr (single column)
        // Computed style might return pixel values '350px' or similar if 1 col
        // Or checks number of visible items

        // Better check: check bounding boxes of children
        const cards = grid.locator('.card');
        const firstCard = cards.nth(0);
        const secondCard = cards.nth(1);

        const box1 = await firstCard.boundingBox();
        const box2 = await secondCard.boundingBox();

        if (box1 && box2) {
            // Second card should be below first card
            expect(box2.y).toBeGreaterThan(box1.y + box1.height);
        }
    });
});
