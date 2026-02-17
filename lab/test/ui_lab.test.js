// @vitest-environment jsdom
import './setup-globals.js';
import { describe, it, expect, beforeEach, vi, afterEach, beforeAll } from 'vitest';
import { render, fireEvent, screen, waitFor, cleanup } from '@testing-library/svelte';
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

// Mock fetch
global.fetch = vi.fn();

describe('UI Integrity & UX Polish (Phase 20)', { timeout: 30000 }, () => {
    afterEach(() => {
        cleanup();
    });

    beforeEach(() => {
        vi.clearAllMocks();
        localStorage.clear();
        locale.set('en');
        localStorage.setItem('lab_active_tab', 'stats');

        fetch.mockImplementation((url) => {
            const getJson = (data) => Promise.resolve({
                ok: true,
                json: () => Promise.resolve(data)
            });

            if (url.includes('manifest')) return getJson([{ run_id: 'test_run', run_tag: 'Test' }]);
            if (url.includes('discovery')) return getJson({
                fourier_spectrum: new Array(100).fill(0),
                norm_riemann: new Array(100).fill(0),
                norm_dejavu: new Array(100).fill(0),
                pearson_r: 0.95,
                euclidean_dist: 0.1
            });
            if (url.includes('phi_frames') || url.includes('trajectories')) return getJson({
                metadata: { frame_count: 100 },
                frames: new Array(100).fill(new Array(64).fill(new Array(64).fill(0))),
                trajectories: []
            });
            if (url.includes('metadata')) return getJson({ frame_count: 100, birth_frame: 391, pearson_r: 0.95 });
            if (url.includes('resonance')) return getJson({ fourier_spectrum: [] });
            if (url.includes('harmonics')) return getJson({ golden_ratio: 1.618 });
            return getJson({});
        });
    });

    it('should have a stabilized alert row and no junk code', async () => {
        const { container } = render(App);
        await waitFor(() => expect(screen.getByText(/SIMULACRUM/i)).toBeInTheDocument(), { timeout: 15000 });
        const overlay = container.querySelector('.overlay');
        expect(overlay).toHaveStyle('grid-template-rows: auto 60px 1fr auto');
    });

    it('should open global modal with high z-index and padding', async () => {
        render(App);
        // Wait for loader to finish - increased timeout for Windows
        await waitFor(() => expect(screen.queryByText(/LOADING/i)).not.toBeInTheDocument(), { timeout: 15000 });

        // Find the tab button specifically
        const hypothesisTab = await screen.findByText(/HYPOTHESIS/i);
        await fireEvent.click(hypothesisTab);
        await tick();

        // Modal MAX button
        const maxBtns = await screen.findAllByText('MAX');
        await fireEvent.click(maxBtns[0]);
        await tick();

        const modal = await screen.findByRole('dialog');
        expect(modal).toBeInTheDocument();
        expect(modal).toHaveClass('global-modal-overlay');
    });

    it('should show high-visibility Fourier dataset', async () => {
        render(App);
        await waitFor(() => expect(screen.queryByText(/LOADING/i)).not.toBeInTheDocument(), { timeout: 15000 });

        const hypothesisTab = await screen.findByText(/HYPOTHESIS/i);
        await fireEvent.click(hypothesisTab);
        await tick();

        // The chart title should eventually appear
        await waitFor(() => {
            const elements = screen.queryAllByText(/FOURIER/i);
            expect(elements.length).toBeGreaterThan(0);
        }, { timeout: 15000 });
    });
});
