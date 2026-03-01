import { render, fireEvent } from '@testing-library/svelte';
import { describe, it, expect, vi } from 'vitest';
import UrbanRoutingApp from '$lib/components/api-showcase/UrbanRoutingApp.svelte';

vi.stubGlobal('IntersectionObserver', class {
    observe() { }
    unobserve() { }
    disconnect() { }
});

describe('UrbanRoutingApp Showcase Component', () => {
    it('renders the core titles and proof section', () => {
        const { getByText } = render(UrbanRoutingApp);
        expect(getByText('Hyper-Scale Urban Routing')).toBeTruthy();
        expect(getByText('Lineum Tensor Field Solver')).toBeTruthy(); // Head-to-head title
    });

    it('renders the interactive agent scale slider', () => {
        const { container } = render(UrbanRoutingApp);
        const inputField = container.querySelector('input[type="range"]') as HTMLInputElement;
        expect(inputField).toBeTruthy();
    });

    it('displays the mock latency waste cost', () => {
        const { getByText } = render(UrbanRoutingApp);
        expect(getByText('A* Industry Waste:')).toBeTruthy();
    });
});
