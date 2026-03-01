// @ts-nocheck

import { test, expect } from './base';

test.describe('Chat & TTS Flow', () => {
    test.beforeEach(async ({ page }) => {
        // Network blocking is handled by base.ts

        // 2. Mock Chat API

        // 2. Mock Chat API
        await page.route('**/api/chat', async (route) => {
            await route.fulfill({
                status: 200,
                contentType: 'application/json',
                body: JSON.stringify({
                    text: 'Hello! I am a simulated response.'
                })
            });
        });

        // 3. Mock TTS API
        await page.route('**/api/tts', async (route) => {
            // Return a dummy audio blob
            const dummyAudio = Buffer.from('dummy-audio-content');
            await route.fulfill({
                status: 200,
                contentType: 'audio/mpeg',
                body: dummyAudio
            });
        });

        // 4. Mock Speech Synthesis (Browser API)
        // Playwright opens a real browser, so window.speechSynthesis exists.
        // But we might want to ensure it has voices to trigger the UI.
        // 4. Mock Speech Synthesis (Browser API)
        await page.addInitScript(() => {
            // Complete Mock of Speech Synthesis because headless browsers are quirky
            // and we want to verify the 'text' passed to speak()

            // @ts-ignore
            window.SpeechSynthesisUtterance = class {
                constructor(text) {
                    this.text = text;
                    this.lang = 'en-US';
                    this.voice = null;
                    this.rate = 1;
                    this.pitch = 1;
                    this.volume = 1;
                    this.onstart = null;
                    this.onend = null;
                    this.onerror = null;
                }
            };

            const mockVoice = {
                name: 'Google US English',
                lang: 'en-US',
                default: true,
                localService: true,
                voiceURI: 'Google US English'
            };

            // @ts-ignore
            Object.defineProperty(window, 'speechSynthesis', {
                value: {
                    pending: false,
                    speaking: false,
                    paused: false,
                    onvoiceschanged: null,
                    // @ts-ignore
                    getVoices: () => [mockVoice],
                    // @ts-ignore
                    speak: (utterance) => {
                        console.log('MOCK_SPEAK:' + utterance.text);
                        // Simulate async speaking
                        // @ts-ignore
                        if (utterance.onstart) setTimeout(() => utterance.onstart(), 10);
                        setTimeout(() => {
                            // @ts-ignore
                            if (utterance.onend) utterance.onend();
                        }, 100);
                    },
                    cancel: () => { },
                    pause: () => { },
                    resume: () => { },
                    addEventListener: () => { },
                    removeEventListener: () => { },
                    dispatchEvent: () => true
                },
                writable: true,
                configurable: true
            });

            // Trigger events
            setTimeout(() => window.dispatchEvent(new Event('voiceschanged')), 50);
        });
    });

    test('should open chat, send message, and trigger TTS', async ({ page }) => {
        // Monitor browser console
        page.on('console', msg => console.log(`BROWSER LOG: ${msg.text()}`));
        page.on('pageerror', err => console.log(`BROWSER ERROR: ${err.message}`));

        await page.goto('/', { timeout: 60000 });

        // 1. Open Chat (if closed)
        // Look for the deck main container instead of text-matching the aria-label
        const toggleBtn = page.locator('.deck-main');
        try {
            await toggleBtn.waitFor({ state: 'visible', timeout: 15000 });
            await toggleBtn.click();
        } catch (e) {
            console.log('Toggle chat button not found or click failed. Checking if already open...');
        }

        // 2. Type Message
        const input = page.locator('input[type="text"]');
        await input.waitFor({ state: 'visible', timeout: 15000 });
        await input.fill('Hello AI');
        await page.waitForTimeout(500); // Wait for state to settle
        await input.press('Enter');

        // 3. Wait for Response
        await expect(page.getByText('Hello! I am a simulated response.')).toBeVisible({ timeout: 30000 });

        // 4. Verify TTS Button
        // The TTS button should appear because we mocked voices.
        // The aria-label is still 'Read aloud' unlocalized right now in the svelte file.
        const ttsBtn = page.getByLabel(/Read aloud/i).first();
        await expect(ttsBtn).toBeVisible();

        // 5. Click TTS and Verify Request
        // We use a Promise to wait for the speak call (captured via console log from our mock)
        // Note: The app defaults to Native TTS, so it calls window.speechSynthesis.speak()
        const ttsSpeakPromise = page.waitForEvent('console', msg => msg.text().includes('MOCK_SPEAK'));

        await ttsBtn.click();

        const msg = await ttsSpeakPromise;
        expect(msg.text()).toContain('Hello! I am a simulated response.');
    });
});
