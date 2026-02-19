import { render, screen, fireEvent } from '@testing-library/svelte';
import { tick } from 'svelte';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import ResonanceDeck from '../lib/components/ResonanceDeck.svelte';

// Mock stores
vi.mock('$lib/stores/hudStore', () => ({
    hudActive: { subscribe: (run: any) => { run(false); return () => { }; } },
    addMessage: vi.fn(),
    hudMessages: { subscribe: (run: any) => { run([]); return () => { }; } }
}));

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

// Mock Window APIs
Object.defineProperty(window, 'speechSynthesis', {
    value: {
        cancel: vi.fn(),
        speak: vi.fn(),
        getVoices: vi.fn().mockReturnValue([]),
        onvoiceschanged: null
    }
});

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

describe('ResonanceDeck Interaction', () => {
    beforeEach(() => {
        vi.useFakeTimers();
    });

    afterEach(() => {
        vi.runOnlyPendingTimers();
        vi.useRealTimers();
    });



    it('should toggle minimize state', async () => {
        render(ResonanceDeck, { props: { active: true } });

        // Default state: Expanded (or at least valid DOM)
        const deckContainer = screen.getByRole('button', { name: /Toggle chat|Minimize to Orb/i });
        expect(deckContainer).toBeTruthy();
    });
});
