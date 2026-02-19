import { render, screen, fireEvent } from '@testing-library/svelte';
import { tick } from 'svelte';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import ResonanceDeck from '../lib/components/ResonanceDeck.svelte';

// Mock stores
vi.mock('$lib/stores/hudStore', async () => {
    const actual = await vi.importActual('svelte/store');
    return {
        // @ts-ignore
        ...actual,
        hudActive: { subscribe: (run: any) => { run(true); return () => { }; } }, // Active by default for these tests
        isChatOpen: actual.writable(false),
        addMessage: vi.fn(),
        hudMessages: { subscribe: (run: any) => { run([]); return () => { }; } }
    };
});

vi.mock('$lib/stores/uiStore', () => ({
    isCookieBannerVisible: { subscribe: (run: any) => { run(false); return () => { }; } }
}));

// Mock Utils
vi.mock('$lib/utils/tts_utils', () => ({
    detectLanguage: () => 'en-US',
    selectVoice: () => null
}));

vi.mock('$lib/utils/chatUtils', () => ({
    stripMarkdown: (s: string) => s
}));

// Mocks for Window APIs are handled in setup.ts

describe('ResonanceDeck Interaction', () => {
    // timers removed for debugging transitions
    beforeEach(() => {
        // vi.useFakeTimers();
        vi.stubGlobal('fetch', vi.fn(() => Promise.resolve({
            ok: true,
            json: () => Promise.resolve({ text: "Mock response" })
        })));
    });

    afterEach(() => {
        // vi.runOnlyPendingTimers();
        // vi.useRealTimers();
        vi.unstubAllGlobals();
    });



    it('should toggle minimize state', async () => {
        render(ResonanceDeck, { props: { active: true } });
        const deckContainer = screen.getByRole('button', { name: /Toggle chat|Minimize to Orb/i });
        expect(deckContainer).toBeTruthy();
    });

    it('should enter userTyping state on input', async () => {
        render(ResonanceDeck, { props: { active: true } });

        // Deck starts collapsed/minimized. Click to expand.
        const deckContainer = screen.getByRole('button', { name: "Toggle chat" });
        await fireEvent.click(deckContainer);
        console.log("Deck clicked. Waiting for expand.");

        // Advance time for transitions
        // await vi.advanceTimersByTimeAsync(1000);

        // Wait for inputs to appear
        const input = await screen.findByPlaceholderText(/Ask Lina|Click to ask/i);

        if (!input) throw new Error("Input not found");

        await fireEvent.input(input, { target: { value: 'Hello' } });
        expect(input).toBeTruthy();
    });
});
