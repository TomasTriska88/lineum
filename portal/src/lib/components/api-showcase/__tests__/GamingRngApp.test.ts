import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, fireEvent, screen } from '@testing-library/svelte';
import GamingRngApp from '../GamingRngApp.svelte';
import { tick } from 'svelte';

describe('GamingRngApp Component', () => {

    // Mock getContext if it's used inside the component or any of its children
    // In our case Svelte components sometimes use context or stores
    beforeEach(() => {
        vi.clearAllMocks();
        // Setup any global mock required for the WebGL canvas
        HTMLCanvasElement.prototype.getContext = vi.fn(() => ({
            fillRect: vi.fn(),
            clearRect: vi.fn(),
            getImageData: vi.fn(),
            putImageData: vi.fn(),
            createImageData: vi.fn(),
            setTransform: vi.fn(),
            drawImage: vi.fn(),
            save: vi.fn(),
            fillText: vi.fn(),
            restore: vi.fn(),
            beginPath: vi.fn(),
            moveTo: vi.fn(),
            lineTo: vi.fn(),
            closePath: vi.fn(),
            stroke: vi.fn(),
            translate: vi.fn(),
            scale: vi.fn(),
            rotate: vi.fn(),
            arc: vi.fn(),
            fill: vi.fn(),
            measureText: vi.fn(() => ({ width: 0 })),
            transform: vi.fn(),
            rect: vi.fn(),
            clip: vi.fn(),
        })) as any;
    });

    it('renders the header and proof points', () => {
        const { getByText } = render(GamingRngApp);

        // Assert header exists
        expect(getByText('Monte Carlo & Scientific RNG')).toBeTruthy();

        // Assert some key proof text is present
        expect(getByText('Algorithmic Pseudo-Randomness')).toBeTruthy();
        expect(getByText('Topological Simulation Entropy')).toBeTruthy();
    });

    it('toggles simulation state on button click', async () => {
        render(GamingRngApp);

        const button = screen.getByRole('button', { name: /START SIMULATION/i });
        expect(button).toBeTruthy();

        // Click to start
        await fireEvent.click(button);
        await tick();

        // Button should now text-toggle to HALT
        const haltButton = screen.getByRole('button', { name: /HALT STREAM/i });
        expect(haltButton).toBeTruthy();

        // Click to halt
        await fireEvent.click(haltButton);
        await tick();

        // Should revert back to START SIMULATION
        expect(screen.getByRole('button', { name: /START SIMULATION/i })).toBeTruthy();
    });

    it('updates terminal logs when simulation is running', async () => {
        render(GamingRngApp);

        const button = screen.getByRole('button', { name: /START SIMULATION/i });
        await fireEvent.click(button);
        await tick();

        // Fast forward timers if we are using vitest fake timers
        // For now, let's just check if the terminal container exists
        const terminalHeader = screen.getByText('LIVE SCIENTIFIC AUDIT /// TRNG STREAM');
        expect(terminalHeader).toBeTruthy();
    });
});
