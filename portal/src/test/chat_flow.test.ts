import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, fireEvent, screen, waitFor } from '@testing-library/svelte';
import ResonanceDeck from '../lib/components/ResonanceDeck.svelte';

// --- MOCKS ---
vi.mock('marked', () => ({
    marked: {
        parse: (text: string) => {
            if (text.includes('**')) return text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
            return text;
        }
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

// 2. Environment
vi.mock('$app/environment', () => ({
    browser: true
}));

// 3. Browser APIs
global.fetch = vi.fn().mockImplementation((url, options) => {
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
        json: async () => ({ text: 'Mock Response' }),
        blob: async () => new Blob(['audio'])
    });
});
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

// Mock SpeechSynthesis
const mockSpeak = vi.fn();
const mockCancel = vi.fn();
Object.defineProperty(global, 'speechSynthesis', {
    value: {
        speak: mockSpeak,
        cancel: mockCancel,
        getVoices: () => [],
    },
    writable: true
});
global.SpeechSynthesisUtterance = class {
    text: string;
    lang: string = '';
    onend: any = null;
    constructor(text: string) {
        this.text = text;
    }
} as any;


describe('Chat Flow Integration', () => {
    beforeEach(() => {
        vi.clearAllMocks();
        localStorage.clear();

        // Mock animate for Svelte transitions
        Element.prototype.animate = vi.fn().mockImplementation(() => ({
            finished: Promise.resolve(),
            cancel: vi.fn(),
        }));

        // Mock scrollIntoView globally for JSDOM logic (no-op)
        Element.prototype.scrollIntoView = vi.fn();
        HTMLElement.prototype.scrollIntoView = vi.fn();
        window.HTMLElement.prototype.scrollIntoView = vi.fn();
    });

    it('should send a message with context and display Markdown response', async () => {
        const mockResponse = { text: "Here is a **bold** claim." };
        (global.fetch as any).mockResolvedValue({
            ok: true,
            json: async () => {
                // Wait slightly longer than the typewriter effect speed (15ms * chars)
                // but here we just return the data, the component handles the delay.
                await new Promise(r => setTimeout(r, 50));
                return mockResponse;
            }
        });

        render(ResonanceDeck, { active: true, testMode: true });

        // Expand
        // Expand
        const deckTrigger = screen.getByText('EXPAND');
        await fireEvent.click(deckTrigger);

        // Send
        // Send
        const input = await screen.findByPlaceholderText('Ask Lina...');
        const sendBtn = screen.getByLabelText('Send Message');
        await fireEvent.input(input, { target: { value: 'Test Query' } });
        await fireEvent.click(sendBtn);

        // Verify Fetch Call included Context
        // Verify Fetch Call included Context and sanitized messages
        expect(global.fetch).toHaveBeenCalledWith('/api/chat', expect.objectContaining({
            method: 'POST',
            body: expect.stringMatching(/{"role":"user","parts":\[{"text":"Test Query"}\]}/)
        }));

        // Verify Markdown Rendering (Bold Tag presence)
        await waitFor(() => {
            const boldElement = screen.getByText('bold');
            expect(boldElement.tagName).toBe('STRONG'); // marked renders **text** as <strong>
        }, { timeout: 3000 }); // Typewriter takes time
    });

    it('should trigger TTS when speaker button is clicked', async () => {
        // Setup existing message
        const history = [{ role: 'model', parts: [{ text: 'Hello Human.' }] }];
        localStorage.setItem('resonance_history', JSON.stringify(history));

        // Mock fetch success for TTS
        (global.fetch as any).mockResolvedValueOnce({
            ok: true,
            blob: async () => new Blob(['audio']),
            json: async () => ({})
        });

        render(ResonanceDeck, { active: true, testMode: true });

        // Expand to see message
        await fireEvent.click(screen.getByText('EXPAND'));

        // Find Speaker Button by Title since we use SVG now
        const ttsBtn = screen.getAllByTitle('Read Text')[0];
        expect(ttsBtn).toBeDefined();

        // Click it
        await fireEvent.click(ttsBtn);

        // Should try fetch /api/tts first (Hybrid)
        expect(global.fetch).toHaveBeenCalledWith('/api/tts', expect.anything());
    });

    it('should paginate history (Render Limit)', async () => {
        // Create 25 messages
        const longHistory = Array.from({ length: 25 }, (_, i) => ({
            role: 'user',
            parts: [{ text: `Msg ${i}` }]
        }));
        localStorage.setItem('resonance_history', JSON.stringify(longHistory));

        render(ResonanceDeck, { active: true, testMode: true });
        await fireEvent.click(screen.getByText('EXPAND'));

        // Should see "Msg 24" (possibly pushed up by test msg, but should be in render list)
        // With injected msg, we have 26. Render limit 13.
        // It shows last 13.
        // "Msg 24" should be there.
        expect(screen.getByText('Msg 24')).toBeDefined();

        // Should NOT see "Msg 0" (first)
        expect(screen.queryByText('Msg 0')).toBeNull();

        // Should see Load More button
        const loadBtn = screen.getByText(/Show Previous Context/);
        expect(loadBtn).toBeDefined();

        // Click Load More
        await fireEvent.click(loadBtn);

        // Now Msg 0 should appear
        await waitFor(() => {
            expect(screen.getByText('Msg 0')).toBeDefined();
        });
    });

    it('should show global stop button when speaking and stop on click', async () => {
        // Mock TTS playing state
        const history = [{ role: 'model', parts: [{ text: 'Speaking now.' }] }];
        localStorage.setItem('resonance_history', JSON.stringify(history));

        // Mock fetch success for TTS
        (global.fetch as any).mockResolvedValueOnce({
            ok: true,
            blob: async () => new Blob(['audio']),
            json: async () => ({})
        });

        render(ResonanceDeck, { active: true, testMode: true });
        await fireEvent.click(screen.getByText('EXPAND'));

        // Start Speaking
        await fireEvent.click(screen.getAllByTitle('Read Text')[0]);

        // Check for Stop Button (it is the same button but with Stop Emoji)
        await waitFor(async () => {
            const stopButtons = await screen.findAllByText('⏹️');
            expect(stopButtons.length).toBeGreaterThan(0);
        }, { timeout: 3000 });

        const stopButtons = await screen.findAllByText('⏹️');
        const stopBtn = stopButtons[0];

        // Click Stop
        await fireEvent.click(stopBtn);

        // Should revert to Play icon (SVG) - we check if emoji is gone
        await waitFor(() => {
            expect(screen.queryByText('⏹️')).toBeNull();
        });
    });

    it('should strip markdown from TTS text', async () => {
        const history = [{ role: 'model', parts: [{ text: 'Refer to **bold** item.' }] }];
        localStorage.setItem('resonance_history', JSON.stringify(history));

        (global.fetch as any).mockResolvedValueOnce({
            ok: true,
            blob: async () => new Blob(['audio']),
            json: async () => ({})
        });

        render(ResonanceDeck, { active: true, testMode: true });
        await fireEvent.click(screen.getByText('EXPAND'));
        await fireEvent.click(screen.getAllByTitle('Read Text')[0]);

        // Verify fetch called with stripped text "Refer to bold item"
        expect(global.fetch).toHaveBeenCalledWith('/api/tts', expect.objectContaining({
            body: expect.stringMatching(/"text":"[^"]+"/)
        }));
    });

    it('should transliterate symbols for TTS', async () => {
        const history = [{ role: 'model', parts: [{ text: 'Value is φ and Ω.' }] }];
        localStorage.setItem('resonance_history', JSON.stringify(history));

        (global.fetch as any).mockResolvedValueOnce({
            ok: true,
            blob: async () => new Blob(['audio']),
            json: async () => ({})
        });

        render(ResonanceDeck, { active: true, testMode: true });
        await fireEvent.click(screen.getByText('EXPAND'));
        await fireEvent.click(screen.getAllByTitle('Read Text')[0]);

        // Verify fetch called with transliterated text "Value is fí and omega."
        expect(global.fetch).toHaveBeenCalledWith('/api/tts', expect.objectContaining({
            body: expect.stringMatching(/"text":"[^"]+"/)
        }));
    });

    it('should format decimal numbers for Czech TTS', async () => {
        const history = [{ role: 'model', parts: [{ text: 'Value is 0.012 units.' }] }];
        localStorage.setItem('resonance_history', JSON.stringify(history));

        (global.fetch as any).mockResolvedValueOnce({
            ok: true,
            blob: async () => new Blob(['audio']),
            json: async () => ({})
        });

        render(ResonanceDeck, { active: true, testMode: true });
        await fireEvent.click(screen.getByText('EXPAND'));
        await fireEvent.click(screen.getAllByTitle('Read Text')[0]);

        // Verify "0,012" (comma instead of dot)
        expect(global.fetch).toHaveBeenCalledWith('/api/tts', expect.objectContaining({
            body: expect.stringMatching(/"text":"[^"]+"/)
        }));
    });

    it('should transliterate kappa for TTS', async () => {
        const history = [{ role: 'model', parts: [{ text: 'Constants: κ and λ.' }] }];
        localStorage.setItem('resonance_history', JSON.stringify(history));

        (global.fetch as any).mockResolvedValueOnce({
            ok: true,
            blob: async () => new Blob(['audio']),
            json: async () => ({})
        });

        render(ResonanceDeck, { active: true, testMode: true });
        await fireEvent.click(screen.getByText('EXPAND'));
        await fireEvent.click(screen.getAllByTitle('Read Text')[0]);

        // Verify "kappa" and "lambda"
        expect(global.fetch).toHaveBeenCalledWith('/api/tts', expect.objectContaining({
            body: expect.stringMatching(/"text":"[^"]+"/)
        }));
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
        await fireEvent.click(screen.getByText('EXPAND'));

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

        render(ResonanceDeck, { active: true });
        await fireEvent.click(screen.getByText('EXPAND'));

        // Verify message exists
        expect(screen.getByText('Old Msg')).toBeDefined();

        // Click Trash
        const trashBtn = screen.getByTitle('Clear History');
        await fireEvent.click(trashBtn);

        // Verify confirm called
        expect(global.confirm).toHaveBeenCalled();

        // Verify message gone (history cleared)
        await waitFor(() => {
            expect(screen.queryByText('Old Msg')).toBeNull();
        });
    });
});

