import '@testing-library/jest-dom';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, fireEvent, screen, waitFor, cleanup } from '@testing-library/svelte';
import { tick } from 'svelte';
import ExplorerPage from './+page.svelte';

// Mock crypto.randomUUID
Object.defineProperty(globalThis, 'crypto', {
    value: {
        randomUUID: () => '12345678-1234-1234-1234-123456789012'
    }
});

// Mock fetch dynamically per test so it doesn't leak
let fetchMock: any;

describe('Portal Explorer Component', () => {
    beforeEach(() => {
        vi.resetAllMocks();
        fetchMock = vi.fn();
        global.fetch = fetchMock;
        vi.spyOn(console, 'error').mockImplementation(() => { });
    });

    afterEach(() => {
        cleanup();
    });

    it('should default to RAW PHYSICS mode', () => {
        render(ExplorerPage);

        // The toggle should display RAW PHYSICS initially
        expect(screen.getByText('RAW PHYSICS')).toBeInTheDocument();
        expect(screen.queryByText('VOICE ON')).not.toBeInTheDocument();
    });

    it('should switch to VOICE ON mode when toggled', async () => {
        render(ExplorerPage);

        const toggleBtn = screen.getByRole('button', { name: /Toggle translation/i });

        await fireEvent.click(toggleBtn);
        await tick();

        // After click, it should display VOICE ON
        expect(screen.getByText('VOICE ON')).toBeInTheDocument();
        expect(screen.queryByText('RAW PHYSICS')).not.toBeInTheDocument();
    });

    it('should display the injection input and button', async () => {
        render(ExplorerPage);

        await waitFor(() => {
            expect(screen.getByPlaceholderText('Inject semantic perturbation (X)...')).toBeInTheDocument();
            expect(screen.getByRole('button', { name: 'Inject' })).toBeInTheDocument();
        });
    });

    it('should call backend API on injection', async () => {
        // Mock successful API responses per URL
        fetchMock.mockImplementation(async (url: string) => {
            if (url.includes('/wake')) {
                return { ok: true, json: async () => ({ status: 'awoken' }) };
            }
            if (url.includes('/chat')) {
                return {
                    ok: true,
                    json: async () => ({
                        session_id: '12345678-1234-1234-1234-123456789012',
                        mode: 'phys',
                        metrics: { max_psi: 1234.5, mean_pressure: 9876.5 },
                        readout_r: [0.1],
                        message: 'test input'
                    })
                };
            }
            return { ok: false };
        });

        render(ExplorerPage);

        // Wait for waking to finish
        let injectBtn: HTMLElement;
        await waitFor(() => {
            injectBtn = screen.getByRole('button', { name: 'Inject' });
            expect(injectBtn).toBeInTheDocument();
        });

        const input = screen.getByPlaceholderText('Inject semantic perturbation (X)...');

        await fireEvent.input(input, { target: { value: 'Test semantic injection' } });
        await fireEvent.click(injectBtn!);

        await tick();
        await new Promise(r => setTimeout(r, 0)); // flush promises

        // Verify fetch called correctly with the exact semantic injection payload
        expect(fetchMock).toHaveBeenCalledWith('http://127.0.0.1:8000/entity/lina/chat', expect.objectContaining({
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: expect.stringContaining('"message":"Test semantic injection"')
        }));
    });
});
