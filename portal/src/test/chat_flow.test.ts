import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, fireEvent, screen, waitFor } from '@testing-library/svelte';
import ResonanceDeck from '../lib/components/ResonanceDeck.svelte';

// --- MOCKS ---

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
global.fetch = vi.fn();
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
global.SpeechSynthesisUtterance = vi.fn().mockImplementation((text) => ({ text, lang: '', onend: null }));


describe('Chat Flow Integration', () => {
    beforeEach(() => {
        vi.clearAllMocks();
        localStorage.clear();

        // Mock animate for Svelte transitions
        Element.prototype.animate = vi.fn().mockImplementation(() => ({
            finished: Promise.resolve(),
            cancel: vi.fn(),
        }));
    });

    it('should send a message with context and display Markdown response', async () => {
        const mockResponse = { text: "Here is a **bold** claim." };
        (global.fetch as any).mockResolvedValue({
            ok: true,
            json: async () => {
                await new Promise(r => setTimeout(r, 50));
                return mockResponse;
            }
        });

        render(ResonanceDeck, { active: true });

        // Expand
        const deckTrigger = screen.getByText('EXPAND EXPLORER');
        await fireEvent.click(deckTrigger);

        // Send
        const input = screen.getByPlaceholderText('Ask the Explorer...');
        const sendBtn = screen.getByText('LINK →');
        await fireEvent.input(input, { target: { value: 'Test Query' } });
        await fireEvent.click(sendBtn);

        // Verify Fetch Call included Context
        expect(global.fetch).toHaveBeenCalledWith('/api/chat', expect.objectContaining({
            method: 'POST',
            body: expect.stringContaining('"context":"/lab/simulation"')
        }));

        // Verify Markdown Rendering (Bold Tag presence)
        await waitFor(() => {
            const boldElement = screen.getByText('bold');
            expect(boldElement.tagName).toBe('STRONG'); // marked renders **text** as <strong>
        });
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

        render(ResonanceDeck, { active: true });

        // Expand to see message
        await fireEvent.click(screen.getByText('EXPAND EXPLORER'));

        // Find Speaker Button (aria-label="Read alound" -> typo in svelte file "Read alound" -> "Read aloud" likely intended but I must match code)
        // Code had `aria-label="Read alound"`. I should fix the typo in code or match it here.
        // Let's rely on class .tts-btn if strict matcher fails, or get by role button.
        // There are multiple buttons (Link ->, Load More?), let's find by emoji if accessible or class.

        // The button contains 🔊.
        const ttsBtn = screen.getByText('🔊');
        expect(ttsBtn).toBeDefined();

        // Click it
        await fireEvent.click(ttsBtn);

        // Should try fetch /api/tts first (Hybrid)
        expect(global.fetch).toHaveBeenCalledWith('/api/tts', expect.anything());

        // We need to mock the response for the fetch call above to avoid unhandled rejection
        // But since we are mocking global.fetch, we should have set it up before the click if we want to test the success path
        // The issue was that the default mock didn't return a blob function.
        // Let's improve the test to actually wait for the audio play.
    });

    it('should paginate history (Render Limit)', async () => {
        // Create 25 messages
        const longHistory = Array.from({ length: 25 }, (_, i) => ({
            role: 'user',
            parts: [{ text: `Msg ${i}` }]
        }));
        localStorage.setItem('resonance_history', JSON.stringify(longHistory));

        render(ResonanceDeck, { active: true });
        await fireEvent.click(screen.getByText('EXPAND EXPLORER'));

        // Should see "Msg 24" (last)
        expect(screen.getByText('Msg 24')).toBeDefined();

        // Should NOT see "Msg 0" (first) because limit is 20
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

        render(ResonanceDeck, { active: true });
        await fireEvent.click(screen.getByText('EXPAND EXPLORER'));

        // Start Speaking
        await fireEvent.click(screen.getByText('🔊'));

        // Check for Stop Button in Header
        const stopBtn = await screen.findByText('⏹️ STOP READING');
        expect(stopBtn).toBeDefined();

        // Click Stop
        await fireEvent.click(stopBtn);

        // Should cancel speech
        // Note: we can't easily check window.speechSynthesis.cancel mocked call count unless we spy on it differently 
        // but we can check if button disappears
        await waitFor(() => {
            expect(screen.queryByText('⏹️ STOP READING')).toBeNull();
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

        render(ResonanceDeck, { active: true });
        await fireEvent.click(screen.getByText('EXPAND EXPLORER'));
        await fireEvent.click(screen.getByText('🔊'));

        // Verify fetch called with stripped text "Refer to bold item"
        expect(global.fetch).toHaveBeenCalledWith('/api/tts', expect.objectContaining({
            body: expect.stringContaining('"text":"Refer to bold item."')
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

        render(ResonanceDeck, { active: true });
        await fireEvent.click(screen.getByText('EXPAND EXPLORER'));
        await fireEvent.click(screen.getByText('🔊'));

        // Verify fetch called with transliterated text "Value is fí and omega."
        expect(global.fetch).toHaveBeenCalledWith('/api/tts', expect.objectContaining({
            body: expect.stringContaining('"text":"Value is fí and omega."')
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

        render(ResonanceDeck, { active: true });
        await fireEvent.click(screen.getByText('EXPAND EXPLORER'));
        await fireEvent.click(screen.getByText('🔊'));

        // Verify "0,012" (comma instead of dot)
        expect(global.fetch).toHaveBeenCalledWith('/api/tts', expect.objectContaining({
            body: expect.stringContaining('"text":"Value is 0,012 units."')
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

        render(ResonanceDeck, { active: true });
        await fireEvent.click(screen.getByText('EXPAND EXPLORER'));
        await fireEvent.click(screen.getByText('🔊'));

        // Verify "kappa" and "lambda"
        expect(global.fetch).toHaveBeenCalledWith('/api/tts', expect.objectContaining({
            body: expect.stringContaining('"text":"Constants: kappa and lambda."')
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
        await fireEvent.click(screen.getByText('EXPAND EXPLORER'));

        const copyBtn = screen.getByLabelText('Copy Markdown');
        expect(copyBtn).toBeTruthy();

        await fireEvent.click(copyBtn);
        expect(writeText).toHaveBeenCalledWith(messageText);
    });

    it('should scroll new message into view at start', async () => {
        render(ResonanceDeck, { active: true });
        await fireEvent.click(screen.getByText('EXPAND EXPLORER'));

        const input = screen.getByPlaceholderText('Ask the Explorer...');
        await fireEvent.input(input, { target: { value: 'Hello' } });

        // Mock scrollIntoView
        const scrollIntoViewMock = vi.fn();
        HTMLElement.prototype.scrollIntoView = scrollIntoViewMock;

        await fireEvent.click(screen.getByText('LINK →'));

        // Wait for typing indicator which triggers scroll
        await waitFor(() => {
            expect(scrollIntoViewMock).toHaveBeenCalledWith({ behavior: 'smooth', block: 'start' });
        });
    });
});
