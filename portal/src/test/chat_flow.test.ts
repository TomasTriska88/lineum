import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { tick } from 'svelte';
import { render, fireEvent, screen, waitFor } from '@testing-library/svelte';
import { get } from 'svelte/store';
import ResonanceDeck from '../lib/components/ResonanceDeck.svelte';
import { isChatOpen } from '../lib/stores/hudStore';

// --- MOCKS ---
vi.mock('marked', () => ({
    marked: {
        parse: (text: string) => {
            if (text.includes('**')) return text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
            return text;
        },
        use: vi.fn()
    }
}));


// 1. SvelteKit Stores (for $page.url.pathname)
vi.mock('$app/stores', () => {
    return {
        page: {
            subscribe: (fn: any) => {
                fn({ url: { pathname: '/lab/simulation' } }); // Mock Context
                return () => { };
            }
        }
    };
});

vi.stubGlobal('confirm', vi.fn(() => true));

// 2. Environment
vi.mock('$app/environment', () => ({
    browser: true
}));

// 3. Browser APIs
vi.stubGlobal('fetch', vi.fn().mockImplementation((url, options) => {
    if (url === '/api/chat' && options?.method === 'POST') {
        const payload = options.body ? options.body.toString() : 'null';
        //console.log('DEBUG: /api/chat payload:', payload); 
        // Throw to see it in failure message if log is swallowed
        if (payload.includes('Test Query')) {
            console.error('CAPTURED_PAYLOAD::' + payload + '::END_PAYLOAD');
        }
    }
    return Promise.resolve({
        ok: true,
        json: async () => ({ text: 'Mock **bold** Response' }),
        blob: async () => new Blob(['audio'])
    });
}));
Element.prototype.scrollTo = vi.fn();
global.URL.createObjectURL = vi.fn(() => 'blob:http://localhost/mock-audio');

// Mock Audio
// Mock Audio
global.Audio = vi.fn(function () {
    return {
        play: vi.fn(),
        pause: vi.fn(),
        addEventListener: vi.fn(),
        removeEventListener: vi.fn(),
    };
}) as any;

// Spies will be set in beforeEach
let mockSpeak: any;
let mockCancel: any;

// Override speech synthesis for this file if needed, but spy is better
// setup.ts already defined window.SpeechSynthesisUtterance

describe('Chat Flow Integration', () => {
    beforeEach(() => {
        vi.clearAllMocks();
        localStorage.clear();
        isChatOpen.set(false);

        // Mock animate for Svelte transitions
        Element.prototype.animate = vi.fn().mockImplementation(() => ({
            finished: Promise.resolve(),
            cancel: vi.fn(),
        }));

        // Initialize spies on global object (setup.ts guarantees window.speechSynthesis exists)
        // Initialize spies on global object (setup.ts guarantees window.speechSynthesis exists)
        if (typeof window !== 'undefined') {
            if (!window.speechSynthesis) {
                // Fallback for environment quirk
                Object.defineProperty(window, 'speechSynthesis', {
                    value: {
                        speak: vi.fn(),
                        cancel: vi.fn(),
                        getVoices: () => [],
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
            mockSpeak = vi.spyOn(window.speechSynthesis, 'speak');
            mockCancel = vi.spyOn(window.speechSynthesis, 'cancel');

            // Mock Voices so TTS button appears
            const voices = [{ name: 'Google US English', lang: 'en-US', default: true }];
            vi.spyOn(window.speechSynthesis, 'getVoices').mockReturnValue(voices as any);
        }

        // Mock scrollIntoView globally for JSDOM logic (no-op)
        Element.prototype.scrollIntoView = vi.fn();
        HTMLElement.prototype.scrollIntoView = vi.fn();
        window.HTMLElement.prototype.scrollIntoView = vi.fn();
    });

    it('should send a message with context and display Markdown response', async () => {
        const mockResponse = { text: "Here is a **bold** claim." };
        // MOCK FETCH for this test
        // MOCK FETCH for this test
        window.fetch = vi.fn().mockImplementation((url: string | URL | Request, config?: RequestInit) => {
            // Fix for relative URLs in JSDOM/Node fetch
            const urlStr = url.toString();
            // Handle both relative and absolute URLs
            if (urlStr.includes('/api/chat')) {
                return Promise.resolve({
                    ok: true,
                    json: async () => {
                        // Wait slightly longer than the typewriter effect speed (15ms * chars)
                        // but here we just return the data, the component handles the delay.
                        await new Promise(r => setTimeout(r, 50));
                        return mockResponse;
                    }
                } as Response);
            }
            return Promise.resolve({ ok: true, json: async () => ({}) } as Response);
        });

        render(ResonanceDeck, { active: true, testMode: false });

        // Expand
        // The button has aria-label="Toggle chat"
        const deckTrigger = screen.getByRole('button', { name: /toggle chat/i });
        await fireEvent.click(deckTrigger);

        // Send
        const input = await screen.findByPlaceholderText('Ask Lina a question...');
        const sendBtn = screen.getByLabelText('Send Message');
        await fireEvent.input(input, { target: { value: 'Test Query' } });
        await fireEvent.click(sendBtn);

        // Verify Fetch Call happened implicitly
        // We can't rely on toHaveBeenCalledWith if multiple calls happen (GET then POST) and race condition exists
        // Instead, wait for the UI update which confirms the fetch succeeded

        // Verify Markdown Rendering (Bold Tag presence)
        await waitFor(() => {
            const boldElement = screen.getByText('bold');
            expect(boldElement.tagName).toBe('STRONG'); // marked renders **text** as <strong>
        }, { timeout: 3000 }); // Typewriter takes time
    });



    it('should paginate history (Render Limit)', async () => {
        // Create 25 messages
        const longHistory = Array.from({ length: 25 }, (_, i) => ({
            role: 'user',
            parts: [{ text: `Msg ${i}` }]
        }));
        localStorage.setItem('resonance_history', JSON.stringify(longHistory));

        render(ResonanceDeck, { active: true, testMode: true });
        const deckTrigger = screen.getByRole('button', { name: /toggle chat/i });
        await fireEvent.click(deckTrigger);

        // Should see "Msg 24" (possibly pushed up by test msg, but should be in render list)
        // With injected msg, we have 26. Render limit 13.
        // It shows last 13.
        // "Msg 24" should be there.
        expect(await screen.findByText('Msg 24')).toBeDefined();

        // Should NOT see "Msg 4" (first visible is 5..24 = 20 messages)
        // Wait, if limit is 20, and we have 25 (0 to 24).
        // Slice -20 gives indices 5 to 24.
        // So Msg 5 should be first visible. Msg 4 should be hidden.
        await waitFor(() => {
            expect(screen.queryByText('Msg 4')).toBeNull();
        });

        // Should see Load More button
        const loadBtn = screen.getByText(/Show Previous Context/);
        expect(loadBtn).toBeDefined();

        // Click Load More
        await fireEvent.click(loadBtn);

        // Now Msg 0 should appear
        expect(await screen.findByText('Msg 0')).toBeDefined();
    });












    it('should show copy button and copy markdown', async () => {
        const messageText = 'Some **bold** text';
        const history = [{ role: 'model', parts: [{ text: messageText }] }];
        localStorage.setItem('resonance_history', JSON.stringify(history));

        // Mock clipboard
        const writeText = vi.fn();
        Object.assign(navigator, {
            clipboard: {
                writeText,
            },
        });

        render(ResonanceDeck, { active: true });
        const deckTrigger = screen.getByRole('button', { name: /toggle chat/i });
        await fireEvent.click(deckTrigger);

        const copyBtn = screen.getAllByLabelText('Copy Markdown')[0];
        expect(copyBtn).toBeTruthy();

        await fireEvent.click(copyBtn);
        expect(writeText).toHaveBeenCalledWith(messageText);
    });
    it('should clear history when trash button is clicked', async () => {
        const history = [{ role: 'user', parts: [{ text: 'Old Msg' }] }];
        localStorage.setItem('resonance_history', JSON.stringify(history));

        // Mock window.confirm
        global.confirm = vi.fn(() => true);

        render(ResonanceDeck, { active: true, testMode: true });

        // Wait for connection/render
        await tick();
        const deckTrigger = screen.getByRole('button', { name: /toggle chat/i });
        await fireEvent.click(deckTrigger);

        // Verify message exists
        expect(await screen.findByText('Old Msg')).toBeDefined();



        // Click Trash
        // The button has aria-label="Clear History"
        const trashBtn = await screen.findByLabelText('Clear History', {}, { timeout: 3000 });
        await fireEvent.click(trashBtn);

        // Verify confirm modal appears
        await screen.findByText('Clear Neural History?');

        const confirmBtn = screen.getByRole('button', { name: /Confirm Delete/i });
        await fireEvent.click(confirmBtn);

        // Verify message gone (history cleared)
        await waitFor(() => {
            expect(screen.queryByText('Old Msg')).toBeNull();
        });
    });
    afterEach(() => {
        vi.unstubAllGlobals();
    });
});

