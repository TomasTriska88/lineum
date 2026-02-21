import { expect, test } from '@playwright/test';

test.describe('Routing Pulse Lab - Advanced Holo UI & WebGL Lifecycle', () => {

    test('Načtení stránky, UI prvky a navigace bez WebGL úniků z paměti', async ({ page }) => {
        const consoleErrors: string[] = [];

        // Listen pro chyby typu paměťový únik ("Too many active WebGL contexts" apod)
        page.on('console', msg => {
            if (msg.type() === 'error' || msg.type() === 'warning') {
                const text = msg.text().toLowerCase();
                if (text.includes('webgl') || text.includes('context') || text.includes('too many active')) {
                    consoleErrors.push(msg.text());
                }
            }
        });

        // Krok 1: Přímá navigace na Routing Lab
        await page.goto('/routing');

        // Sledujeme viditelnost canvas prvku
        const webglCanvas = page.locator('canvas.w-full.h-full.object-cover');
        await expect(webglCanvas).toBeVisible({ timeout: 10000 });

        // Otestování existence hlavních ovládacích UI prvků Holo-Decku
        await expect(page.getByRole('heading', { name: /Lineum Pulse Lab/i })).toBeVisible();
        await expect(page.getByText('SYSTEM: IDLE')).toBeVisible();

        const startBtn = page.getByRole('button', { name: /INITIATE WAVE/i });
        await expect(startBtn).toBeVisible();

        // Krok 2: Spuštění a kontrola tensor pole UI
        await startBtn.click();
        await expect(page.getByText(/TENSOR FIELD:/i)).toBeVisible({ timeout: 5000 });
        const stopBtn = page.getByRole('button', { name: /ABORT SIMULATION/i });
        await expect(stopBtn).toBeVisible();
        await stopBtn.click();

        // Krok 3: Lifecycle navigace pro ověření onDestroy WebGL Cleanup Memory Leaku
        // Jdeme zpět na Homepage s FieldShader komponentou, pak znova na Routing.
        await page.goto('/');
        await page.waitForLoadState('networkidle');

        // Druhý Canvas na homepage musí natáhnout svůj WebGL Context v pořádku
        await expect(page.locator('canvas.shader-canvas')).toBeVisible();

        // A zpět na routing abychom inicializovaly další WebGL Kontext a narušili limit prohlížeče
        // Pokud chybí cleanup v komponentách, tak zde zaručeně vyskočí Warning: "Too many contexts".
        await page.goto('/routing');
        await expect(page.locator('canvas.w-full.h-full.object-cover')).toBeVisible();

        // Vyhodnocujeme, zdali se v konzoli nezachytil WebGL Limit error.
        expect(consoleErrors).toEqual([]);
    });

});
