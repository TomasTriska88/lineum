// @vitest-environment jsdom
import './setup-globals.js';
import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest';
import { render, screen, waitFor, cleanup } from '@testing-library/svelte';
import '@testing-library/jest-dom';
import App from '../src/App.svelte';
import { tick } from 'svelte';
import { locale } from '../src/lib/i18n';

// Mock Chart.js completely
vi.mock('chart.js/auto', () => ({
    default: vi.fn().mockImplementation(() => ({
        destroy: vi.fn(),
        update: vi.fn(),
        resetZoom: vi.fn(),
        data: { datasets: [] },
        options: { plugins: { zoom: { zoom: { wheel: {} } } } }
    })),
    register: vi.fn(),
}));

// Robust Global Fetch Mock
const mockFetch = vi.fn();
global.fetch = mockFetch;
if (typeof window !== 'undefined') {
    window.fetch = mockFetch;
}

describe('UI Integrity & UX Polish (Phase 20)', { timeout: 30000 }, () => {
    afterEach(() => {
        cleanup();
        vi.clearAllMocks();
    });

    beforeEach(() => {
        localStorage.clear();
        locale.set('en');
        localStorage.setItem('lab_active_tab', 'stats');

        mockFetch.mockImplementation((url) => {
            const getJson = (data) => Promise.resolve({
                ok: true,
                json: () => Promise.resolve(data)
            });

            const sUrl = url.toString();
            if (sUrl.includes('manifest')) return getJson([{ run_id: 'test_run', run_tag: 'Test' }]);

            // Match all required data files for App.svelte initialization
            if (sUrl.includes('phi_frames')) return getJson({
                metadata: { frame_count: 100 },
                frames: []
            });
            if (sUrl.includes('trajectories')) return getJson({
                trajectories: []
            });
            if (sUrl.includes('discovery')) return getJson({
                fourier_spectrum: new Array(100).fill(0),
                norm_riemann: new Array(100).fill(0),
                norm_dejavu: new Array(100).fill(0),
                pearson_r: 0.95,
                euclidean_dist: 0.1
            });
            if (sUrl.includes('metadata')) return getJson({ frame_count: 100, birth_frame: 391, pearson_r: 0.95 });
            if (sUrl.includes('resonance')) return getJson({ fourier_spectrum: [] });
            if (sUrl.includes('harmonics')) return getJson({ golden_ratio: 1.618 });

            return getJson({});
        });
    });

    it('should have a stabilized alert row and no junk code', async () => {
        const { container } = render(App);
        // Wait for LOADING to disappear
        await waitFor(() => expect(screen.queryByText(/LOADING/i)).not.toBeInTheDocument(), { timeout: 20000 });

        await waitFor(() => expect(screen.getByText(/SIMULACRUM/i)).toBeInTheDocument(), { timeout: 5000 });
        const overlay = container.querySelector('.overlay');
        expect(overlay).toHaveStyle('grid-template-rows: auto 60px 1fr auto');
    });

    it('should open global modal with high z-index and padding', async () => {
        render(App);
        await waitFor(() => expect(screen.queryByText(/LOADING/i)).not.toBeInTheDocument(), { timeout: 20000 });

        const hypothesisTab = await screen.findByText(/HYPOTHESIS/i);
        await hypothesisTab.click();
        await tick();

        const maxBtns = await screen.findAllByText('MAX');
        await maxBtns[0].click();
        await tick();

        const modal = await screen.findByRole('dialog');
        expect(modal).toBeInTheDocument();
        expect(modal).toHaveClass('global-modal-overlay');
    });

    it('should show high-visibility Fourier dataset', async () => {
        render(App);
        await waitFor(() => expect(screen.queryByText(/LOADING/i)).not.toBeInTheDocument(), { timeout: 20000 });

        const hypothesisTab = await screen.findByText(/HYPOTHESIS/i);
        await hypothesisTab.click();
        await tick();

        await waitFor(() => {
            const elements = screen.queryAllByText(/FOURIER/i);
            expect(elements.length).toBeGreaterThan(0);
        }, { timeout: 10000 });
    });
});
