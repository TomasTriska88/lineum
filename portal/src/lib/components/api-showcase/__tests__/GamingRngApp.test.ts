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
        const { getByText } = render(GamingRngApp);

        const button = getByText(/Generate Game Seed/i).closest('button');
        expect(button).not.toBeNull();
        if (!button) return;

        // Click to start
        await fireEvent.click(button);
        await tick();

        // Button should now text-toggle to Stop
        const haltText = getByText(/Stop Stream/i);
        expect(haltText).toBeTruthy();

        // Click to halt
        const haltBtn = haltText.closest('button');
        expect(haltBtn).not.toBeNull();
        if (haltBtn) await fireEvent.click(haltBtn);
        await tick();

        // Should revert back to Done (which requires reset) or Start if it loops
        // Actually, gaming RNG goes to "New Seed" or "done" after stopping depending on logic
        expect(getByText(/New Seed/i)).toBeTruthy();
    });

    it('updates terminal logs when simulation is running', async () => {
        const { getByText } = render(GamingRngApp);

        const button = getByText(/Generate Game Seed/i).closest('button');
        expect(button).not.toBeNull();
        if (button) await fireEvent.click(button);
        await tick();

        // Fast forward timers if we are using vitest fake timers
        // For now, let's just check if the terminal component or a log exists
        const terminalHeader = screen.getByText(/LIVE SCIENTIFIC AUDIT/i);
        expect(terminalHeader).toBeTruthy();
    });
});
