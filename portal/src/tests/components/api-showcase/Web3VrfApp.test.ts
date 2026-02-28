import { render, fireEvent } from '@testing-library/svelte';
import { describe, it, expect, vi } from 'vitest';
import Web3VrfApp from '$lib/components/api-showcase/Web3VrfApp.svelte';

// Mock IntersectionObserver which is not available in jsdom
vi.stubGlobal('IntersectionObserver', class {
    observe() { }
    unobserve() { }
    disconnect() { }
});

describe('Web3VrfApp Showcase Component', () => {
    it('renders the title and strict content rule sections', () => {
        const { getByText } = render(Web3VrfApp);
        expect(getByText('Web3 VRF API')).toBeTruthy();
        expect(getByText('Lineum ZK-VRF')).toBeTruthy(); // Head-to-Head
        expect(getByText('Live Cryptographic Audit')).toBeTruthy(); // Proof
    });

    it('renders the interactive random payload trigger', () => {
        const { getByText, getByRole } = render(Web3VrfApp);
        const button = getByRole('button');
        expect(button.textContent).toContain('Request VRF Randomness');
    });

    it('starts broadcasting transaction upon first click', async () => {
        const { getByRole } = render(Web3VrfApp);

        const triggerBtn = getByRole('button');
        await fireEvent.click(triggerBtn);

        // button enters broadcasting state
        expect(triggerBtn.textContent).toContain('Broadcasting TXN...');
        expect(triggerBtn).toHaveProperty('disabled', true);
    });
});
