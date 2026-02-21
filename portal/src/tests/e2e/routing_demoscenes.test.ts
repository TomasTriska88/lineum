import { test, expect } from '@playwright/test';

test.describe('Lineum Routing Demoscenes UI', () => {
    test('Should load Routing page without 500 Error and select presets', async ({ page }) => {
        // Navštívíme stránku s routingem
        const res = await page.goto('/routing');

        // Zjistíme jestli aplikace vůbec nenaběhla na 500 Error server-side renderu
        expect(res?.status()).toBe(200);

        // Ověříme, že se renderuje WebGL Canvas a nadpisy Themingu
        await expect(page.locator('canvas.webgl-canvas')).toBeVisible();
        await expect(page.locator('text=Business Use-Cases')).toBeVisible();

        // Vybereme z Demoscény dropdownu preset 'vascular'
        const selectPreset = page.locator('select.holo-select');
        await expect(selectPreset).toBeVisible();
        await selectPreset.selectOption('vascular');

        // Zkontrolujeme, zda UI adekvátně zreagovalo změnou textu (Algoritmus pro vascular)
        await expect(page.locator('text=High noise divergence. Fluid covers maximum tissue area forming fractals.')).toBeVisible();

        // Ověříme, že tlačítko INITIATE SHOWCASE existuje
        const btnStart = page.locator('button.btn-initiate');
        await expect(btnStart).toBeVisible();
        await expect(btnStart).toContainText('INITIATE SHOWCASE');

        // CVIČNĚ klikneme na tlačítko a ověříme změnu stavu na ABORT SIMULATION
        // Pokud by padalo WebSocket připojení, Playwright console.error to chytí.
        page.on('console', msg => {
            if (msg.type() === 'error') {
                console.log('BROWSER ERROR CONSOLE:', msg.text());
            }
        });

        await btnStart.click();
        await expect(page.locator('button.btn-abort')).toBeVisible();
    });
});
