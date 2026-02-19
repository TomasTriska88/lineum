
import { render, screen, fireEvent, waitFor } from '@testing-library/svelte';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import ResonanceDeck from '../lib/components/ResonanceDeck.svelte';

// Mocks
vi.mock('$app/stores', () => ({
    page: { subscribe: (run: any) => { run({ url: { pathname: '/' } }); return () => { }; } }
}));

vi.mock('$app/environment', () => ({
    browser: true
}));

describe('ResonanceDeck Minimize Logic', () => {
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

        // Mock window properties needed for Svelte components
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

        // Mock fetch
        vi.stubGlobal('fetch', vi.fn(() => Promise.resolve({
            ok: true,
            json: () => Promise.resolve({ text: "Mock response" })
        })));

        // Mock SpeechSynthesis
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

        // Mock Element.prototype.animate
        Element.prototype.animate = vi.fn().mockReturnValue({
            finished: Promise.resolve(),
            cancel: vi.fn()
        });

        // Mock scroll methods
        HTMLElement.prototype.scrollIntoView = vi.fn();
        HTMLElement.prototype.scrollTo = vi.fn();
    });

    afterEach(() => {
        vi.unstubAllGlobals();
    });

    it('should start in default collapsed state (not minimized)', () => {
        render(ResonanceDeck, { props: { active: true } });
        // Should show the "Minimize" button
        const minimizeBtn = screen.getByLabelText('Minimize');
        expect(minimizeBtn).toBeTruthy();

        // Should NOT show the "Orb" content
        const deckContainer = screen.getByRole('button', { name: /toggle chat/i }).closest('.deck-container');
        expect(deckContainer?.className).not.toContain('minimized');
    });

    it('should switch to minimized mode when minimize button is clicked', async () => {
        render(ResonanceDeck, { props: { active: true } });

        const minimizeBtn = screen.getByLabelText('Minimize');
        await fireEvent.click(minimizeBtn);

        // Wait for update
        await waitFor(() => {
            const restoreBtn = screen.getByLabelText('Restore Chat');
            expect(restoreBtn).toBeTruthy();
        });

        // Check container class
        const deckContainer = screen.getByLabelText('Restore Chat').closest('.deck-container');
        expect(deckContainer?.className).toContain('minimized');
    });

    it('should restore to default state when minimized orb is clicked', async () => {
        render(ResonanceDeck, { props: { active: true } });

        // Minimize first
        const minimizeBtn = screen.getByLabelText('Minimize');
        await fireEvent.click(minimizeBtn);

        // Verify minimized
        await waitFor(() => {
            expect(screen.queryByLabelText('Restore Chat')).toBeTruthy();
        });

        // Click to restore
        const restoreBtn = screen.getByLabelText('Restore Chat');
        await fireEvent.click(restoreBtn);

        // Verify restored
        await waitFor(() => {
            expect(screen.queryByLabelText('Toggle chat')).toBeTruthy();
            expect(screen.queryByLabelText('Restore Chat')).toBeNull();
        });
    });

    it('should render wireframe mesh (multiple paths) in the resonance wave', () => {
        const { container } = render(ResonanceDeck, { props: { active: true } });
        // Look for the main wave container
        const waveContainer = container.querySelector('.resonance-wave.field-lines');
        expect(waveContainer).toBeTruthy();

        // Check for multiple paths (indicating the wireframe loop is working)
        const paths = waveContainer?.querySelectorAll('path');
        expect(paths?.length).toBeGreaterThan(3); // Should be around 12
    });
});
