import { render, fireEvent } from '@testing-library/svelte';
import { describe, it, expect, vi } from 'vitest';
import EvacRoutingApp from '$lib/components/api-showcase/EvacRoutingApp.svelte';

vi.stubGlobal('IntersectionObserver', class {
    observe() { }
    unobserve() { }
    disconnect() { }
});

describe('EvacRoutingApp Showcase Component', () => {
    it('renders the core titles and proof section', () => {
        const { getByText } = render(EvacRoutingApp);
        expect(getByText('High-Density Crowd Evacuation')).toBeTruthy();
        expect(getByText('Safety Analysis Log')).toBeTruthy(); // Terminal title
    });

    it('renders the interactive crowd scale slider', () => {
        const { container } = render(EvacRoutingApp);
        const inputField = container.querySelector('input[type="range"]') as HTMLInputElement;
        expect(inputField).toBeTruthy();
    });

    it('displays the mock ABM Compute Time', () => {
        const { getByText } = render(EvacRoutingApp);
        expect(getByText('ABM Compute Time:')).toBeTruthy();
    });
});
