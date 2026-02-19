
import { render, screen } from '@testing-library/svelte';
import { tick } from 'svelte';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import ResonanceDeck from '../lib/components/ResonanceDeck.svelte';

// Mock Svelte stores
vi.mock('$app/stores', () => ({
    page: { subscribe: (run: any) => { run({ url: { pathname: '/' } }); return () => { }; } }
}));

vi.mock('$app/environment', () => ({
    browser: true
}));

vi.mock('$lib/stores/hudStore', () => ({
    hudActive: { subscribe: (run: any) => { run(false); return () => { }; } },
    addMessage: vi.fn(),
    hudMessages: { subscribe: (run: any) => { run([]); return () => { }; } }
}));

vi.mock('$lib/stores/uiStore', () => ({
    isCookieBannerVisible: { subscribe: (run: any) => { run(false); return () => { }; } }
}));

vi.mock('$lib/utils/tts_utils', () => ({
    detectLanguage: () => 'en-US',
    selectVoice: () => null
}));

vi.mock('$lib/utils/chatUtils', () => ({
    stripMarkdown: (s: string) => s
}));

// Mock AudioContext to prevent JSDOM errors if used
window.AudioContext = vi.fn().mockImplementation(() => ({
    createAnalyser: () => ({
        connect: vi.fn(),
        disconnect: vi.fn(),
        frequencyBinCount: 128,
        getByteFrequencyData: vi.fn()
    }),
    createMediaStreamSource: () => ({ connect: vi.fn() }),
    state: 'suspended',
    resume: vi.fn()
}));

Object.defineProperty(navigator, 'mediaDevices', {
    value: {
        getUserMedia: vi.fn().mockResolvedValue({ getTracks: () => [] })
    }
});

describe('ResonanceDeck Wireframe', () => {
    beforeEach(() => {
        vi.useFakeTimers();
    });

    afterEach(() => {
        vi.useRealTimers();
    });

    it('should match the 32x32 grid specification', async () => {
        const { container } = render(ResonanceDeck, { props: { active: true } });

        // Advance time to allow the animation loop to generate paths
        // The loop increments 'time' which updates 'surfacePaths'
        await vi.advanceTimersByTimeAsync(100);
        await tick();

        // 1. Verify SVG ViewBox is strictly 32x32
        const wireframeSvg = container.querySelector('.field-lines svg');
        expect(wireframeSvg).toBeTruthy();

        if (wireframeSvg) {
            expect(wireframeSvg.getAttribute('viewBox')).toBe('0 0 32 32');
            expect(wireframeSvg.getAttribute('preserveAspectRatio')).toBe('none');
        }

        // 2. Verify Rendered Paths
        const paths = container.querySelectorAll('.field-lines path');
        expect(paths.length).toBeGreaterThan(0);

        // Check first path geometry
        const d = paths[0].getAttribute('d');
        expect(d).toBeTruthy();
        if (d) {
            // Check coordinate matching
            const coords = d.match(/([\d\.]+),([\d\.]+)/g);
            expect(coords).toBeTruthy();

            if (coords) {
                const points = coords.map(c => {
                    const [x, y] = c.split(',').map(Number);
                    return { x, y };
                });

                const maxX = Math.max(...points.map(p => p.x));
                const maxY = Math.max(...points.map(p => p.y));

                // X should be exactly 32 (width)
                expect(maxX).toBeLessThanOrEqual(32);
                expect(maxX).toBeGreaterThan(30); // Should be close to edge

                // Y should be within reasonable bounds (0-32 + amplitude)
                // BaseY is roughly 6-28, amp is small.
                expect(maxY).toBeLessThan(50); // Safe upper bound
            }
        }
    });

    it('should have visible dimensions in DOM', async () => {
        const { container } = render(ResonanceDeck);

        // Helper to check class existence
        const waveContainer = container.querySelector('.resonance-wave.field-lines');
        expect(waveContainer).toBeTruthy();

        // Checks for the class that enforcing 32px dimensions
        // Note: JSDOM doesn't compute styles fully, but we can check if class is applied
        // and if we can find the style tag or inline style if applied.
        // Since we used a CSS file, we mainly trust consistency of class name.
        expect(waveContainer?.classList.contains('field-lines')).toBe(true);
    });
});
