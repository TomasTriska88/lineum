import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, fireEvent, screen } from '@testing-library/svelte';
import { hudActive } from '../lib/stores/hudStore';
import ResonanceDeck from '../lib/components/ResonanceDeck.svelte';
import { get } from 'svelte/store';

vi.stubGlobal('fetch', vi.fn(() => Promise.resolve({
    ok: true,
    json: () => Promise.resolve({}),
    blob: () => Promise.resolve(new Blob([]))
})));

describe('HUD Store and Interaction', () => {
    beforeEach(() => {
        vi.clearAllMocks();
        localStorage.clear();

        // Mock animate
        Element.prototype.animate = vi.fn().mockReturnValue({
            finished: Promise.resolve(),
            cancel: vi.fn()
        });

        // Mock speechSynthesis
        Object.defineProperty(window, 'speechSynthesis', {
            value: {
                cancel: vi.fn(),
                speak: vi.fn(),
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
    });

    it('should render ResonanceDeck and allow expansion', async () => {
        // Reset stores
        hudActive.set(true);

        render(ResonanceDeck, { active: true });

        // The button has aria-label="Toggle chat"
        const deck = screen.getByRole('button', { name: /toggle chat/i });
        expect(deck).toBeDefined();

        await fireEvent.click(deck);

        // When expanded, we expect "ONLINE" or "Lina"
        // The Minimize button was removed, so we just check for Lina's name
        const linaText = await screen.findByText('Lina');
        expect(linaText).toBeDefined();
    });
});
