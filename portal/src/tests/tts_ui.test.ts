
import { render, screen, fireEvent } from '@testing-library/svelte';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import ResonanceDeck from '../lib/components/ResonanceDeck.svelte';
import { tick } from 'svelte';

// Mock specific modules if needed
vi.mock('$app/stores', () => ({
    page: { subscribe: (run: any) => { run({ url: { pathname: '/' } }); return () => { }; } }
}));

vi.mock('$app/environment', () => ({
    browser: true
}));

describe('ResonanceDeck UI', () => {
    beforeEach(() => {
        vi.clearAllMocks();
        // Mock localStorage
        const store: Record<string, string> = {};
        vi.stubGlobal('localStorage', {
            getItem: (key: string) => store[key] || null,
            setItem: (key: string, value: string) => { store[key] = value; },
            removeItem: (key: string) => { delete store[key]; },
            clear: () => { }
        });

        // Mock matchMedia (handled by setup.ts, but we might want spies)
        // Mock SpeechSynthesis (handled by setup.ts)
        // Mock matchMedia
        Object.defineProperty(window, 'matchMedia', {
            writable: true,
            value: vi.fn().mockImplementation(query => ({
                matches: false,
                media: query,
                onchange: null,
                addListener: vi.fn(),
                removeListener: vi.fn(),
                addEventListener: vi.fn(),
                removeEventListener: vi.fn(),
                dispatchEvent: vi.fn(),
            })),
        });

        // Mock SpeechSynthesis if not present (JSDOM)
        if (!window.speechSynthesis) {
            Object.defineProperty(window, 'speechSynthesis', {
                value: {
                    speak: vi.fn(),
                    cancel: vi.fn(),
                    getVoices: vi.fn().mockReturnValue([]),
                    pause: vi.fn(),
                    resume: vi.fn(),
                    paused: false,
                    speaking: false,
                    onvoiceschanged: null,
                    addEventListener: vi.fn(),
                    removeEventListener: vi.fn(),
                    dispatchEvent: vi.fn(),
                },
                writable: true
            });
        }

        vi.spyOn(window.speechSynthesis, 'speak');
        vi.spyOn(window.speechSynthesis, 'cancel');
        vi.spyOn(window.speechSynthesis, 'getVoices').mockReturnValue([]);

        // Mock fetch for /api/chat
        vi.stubGlobal('fetch', vi.fn(() => Promise.resolve({
            ok: true,
            json: () => Promise.resolve({ text: "Mock response" }),
            blob: () => Promise.resolve(new Blob([]))
        })));

        // Mock scrolling logic (JSDOM does not implement layout)
        HTMLElement.prototype.scrollIntoView = vi.fn();
        HTMLElement.prototype.scrollTo = vi.fn();
        // Mock animate
        Element.prototype.animate = vi.fn().mockReturnValue({
            finished: Promise.resolve(),
            cancel: vi.fn()
        });
    });

    afterEach(() => {
        vi.unstubAllGlobals();
    });

    it('should hide copy button for system messages', async () => {
        render(ResonanceDeck);

        // Wait for greeting
        const greeting = await screen.findByText('Lina', {}, { timeout: 3000 });
        expect(greeting).toBeTruthy();

        // The Copy button has aria-label="Copy Markdown"
        // It should NOT be present for the greeting (system message)
        const copyBtns = screen.queryAllByLabelText('Copy Markdown');
        expect(copyBtns.length).toBe(0);
    });





    it('should trigger TTS when button is clicked', async () => {
        render(ResonanceDeck, { active: true });

        // Open deck
        const toggleBtn = screen.getByRole('button', { name: /toggle chat/i });
        await fireEvent.click(toggleBtn);

        // Find input and type
        const input = await screen.findByPlaceholderText(/Zeptejte se Liny/i, {}, { timeout: 3000 });
        const sendBtn = screen.getByLabelText('Send Message');

        await fireEvent.input(input, { target: { value: 'Hello' } });
        await fireEvent.click(sendBtn);

        // Wait for "Mock response" from model
        await screen.findByText("Mock response", {}, { timeout: 3000 });

        // Find "Read Aloud" button. It should appear on the model message.
        // It might take a tick.
        const ttsBtns = await screen.findAllByLabelText(/Read aloud/i, {}, { timeout: 3000 });
        expect(ttsBtns.length).toBeGreaterThan(0);

        await fireEvent.click(ttsBtns[0]);

        // Wait for async handlers
        await new Promise(r => setTimeout(r, 50));

        // Check speak called
        expect(window.speechSynthesis.speak).toHaveBeenCalled();
    });
});
